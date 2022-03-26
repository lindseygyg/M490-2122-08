import smbus
import time
import os
import matplotlib.animation as animation
import numpy as np  # This is the package needed for functions.
from scipy.integrate import cumtrapz, trapz
from scipy.signal import detrend, lfilter, filtfilt, butter, find_peaks
import matplotlib
import matplotlib.pyplot as plt
import csv, datetime
from scipy.optimize import curve_fit

mpu = mpu6050(0x68)

class Accelerometer:
    # Global Variables
    GRAVITIY_MS2 = 9.80665
    address = None
    bus = None

    # Scale Modifiers
    ACCEL_SCALE_MODIFIER_2G = 16384.0
    ACCEL_SCALE_MODIFIER_4G = 8192.0
    ACCEL_SCALE_MODIFIER_8G = 4096.0
    ACCEL_SCALE_MODIFIER_16G = 2048.0

    # Pre-defined ranges
    ACCEL_RANGE_2G = 0x00
    ACCEL_RANGE_4G = 0x08
    ACCEL_RANGE_8G = 0x10
    ACCEL_RANGE_16G = 0x18

    FILTER_BW_256 = 0x00
    FILTER_BW_188 = 0x01
    FILTER_BW_98 = 0x02
    FILTER_BW_42 = 0x03
    FILTER_BW_20 = 0x04
    FILTER_BW_10 = 0x05
    FILTER_BW_5 = 0x06

    # MPU-6050 Registers
    PWR_MGMT_1 = 0x6B
    PWR_MGMT_2 = 0x6C

    ACCEL_XOUT0 = 0x3B
    ACCEL_YOUT0 = 0x3D
    ACCEL_ZOUT0 = 0x3F

    ACCEL_CONFIG = 0x1C

    def __init__(self, address, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)
        # Wake up the MPU-6050 since it starts in sleep mode
        # self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
        # TODO: TESTING WITH NEW VALUE
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, self.FILTER_BW_5)

    def read_i2c_word(self, register):
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    def set_filter_range(self, filter_range=FILTER_BW_5):
        """Sets the low-pass bandpass filter frequency"""
        # Keep the current EXT_SYNC_SET configuration in bits 3, 4, 5 in the MPU_CONFIG register
        EXT_SYNC_SET = self.bus.read_byte_data(self.address, self.MPU_CONFIG) & 0b00111000
        return self.bus.write_byte_data(self.address, self.MPU_CONFIG, EXT_SYNC_SET | filter_range)

    def set_accel_range(self, accel_range, filter_range=FILTER_BW_5):
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range, filter_range)

    def read_accel_range(self, raw=False):
        raw_data = self.bus.read_byte_data(self.address, self.ACCEL_CONFIG)

        if raw is True:
            return raw_data
        elif raw is False:
            if raw_data == self.ACCEL_RANGE_2G:
                return 2
            elif raw_data == self.ACCEL_RANGE_4G:
                return 4
            elif raw_data == self.ACCEL_RANGE_8G:
                return 8
            elif raw_data == self.ACCEL_RANGE_16G:
                return 16
            else:
                return -1

    def get_accel_data(self, g=False):
        try:
            #x = self.read_i2c_word(self.ACCEL_XOUT0)
            #y = self.read_i2c_word(self.ACCEL_YOUT0)
            z = self.read_i2c_word(self.ACCEL_ZOUT0)
        except OSError:
            print("Disconnected")
            return

        accel_scale_modifier = None
        accel_range = self.read_accel_range(True)

        if accel_range == self.ACCEL_RANGE_2G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G
        elif accel_range == self.ACCEL_RANGE_4G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_4G
        elif accel_range == self.ACCEL_RANGE_8G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_8G
        elif accel_range == self.ACCEL_RANGE_16G:
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_16G
        else:
            print("Unknown range-accel_scale_modifier set to self.ACCEL_SCALE_MODIFIER_2G")
            accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G

        #x = x / accel_scale_modifier
        #y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g is True:
            return z
        elif g is False:
            #x = x * self.GRAVITIY_MS2
            #y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2

            return z

    #####################################
    # Accel Calibration (gravity)
    #####################################
    #
    def accel_fit(x_input, m_x, b):
        return (m_x * x_input) + b  # fit equation for accel calibration

    #
    def get_accel(self):
      z, _ = mpu6050_conv()  # read and convert accel data
      return z

    def accel_cal(self):
        print("-" * 50)
        print("Accelerometer Calibration")
        mpu_offsets = [[], [], []]  # offset array to be printed
        axis_vec = ['z']  # axis labels
        cal_directions = ["upward", "downward", "perpendicular to gravity"]  # direction for IMU cal
        cal_indices = [2, 1, 0]  # axis indices

        for qq, ax_qq in enumerate(axis_vec):
            ax_offsets = [[], [], []]
            print("-" * 50)

            for direc_ii, direc in enumerate(cal_directions):
                input("-" * 8 + " Press Enter and Keep IMU Steady to Calibrate the Accelerometer with the -" + \
                      ax_qq + "-axis pointed " + direc)
                [mpu6050_conv() for ii in range(0, cal_size)]  # clear buffer between readings
                mpu_array = []
                while len(mpu_array) < cal_size:
                    try:
                        z = get_accel()
                        mpu_array.append([z])  # append to array
                    except:
                        continue
                ax_offsets[direc_ii] = np.array(mpu_array)[:, cal_indices[qq]]  # offsets for direction

            # Use three calibrations (+1g, -1g, 0g) for linear fit
            popts, _ = curve_fit(accel_fit, np.append(np.append(ax_offsets[0],
                                                                ax_offsets[1]), ax_offsets[2]),
                                 np.append(np.append(1.0 * np.ones(np.shape(ax_offsets[0])),
                                                     -1.0 * np.ones(np.shape(ax_offsets[1]))),
                                           0.0 * np.ones(np.shape(ax_offsets[2]))),
                                 maxfev=10000)
            mpu_offsets[cal_indices[qq]] = popts  # place slope and intercept in offset array
        print('Accelerometer Calibrations Complete')
        return mpu_offsets


    def cal_data (self):
        # Accelerometer Gravity Calibration
        ###################################
        #

        cal_size = 1000  # number of points to use for calibration
        accel_coeffs = accel_cal()  # grab accel coefficients
        #
        ###################################
        # Record new data
        ###################################

        data = np.array([get_accel() for ii in range(0, cal_size)])  # new values

        calData= accel_fit(data[:,ii], *accel_coeffs[ii])

        ###################################
        # Plot with and without offsets
        ###################################

        plt.style.use('ggplot')
        fig, axs = plt.subplots(2, 1, figsize=(12, 9))
        for ii in range(0, 3):
            axs[0].plot(data[:, ii],
                        label='${}$, Uncalibrated'.format(accel_labels[ii]))
            axs[1].plot(accel_fit(data[:, ii], *accel_coeffs[ii]),
                        label='${}$, Calibrated'.format(accel_labels[ii]))
        axs[0].legend(fontsize=14)
        axs[1].legend(fontsize=14)
        axs[0].set_ylabel('$a_{x,y,z}$ [g]', fontsize=18)
        axs[1].set_ylabel('$a_{x,y,z}$ [g]', fontsize=18)
        axs[1].set_xlabel('Sample', fontsize=18)
        axs[0].set_ylim([-2, 2])
        axs[1].set_ylim([-2, 2])
        axs[0].set_title('Accelerometer Calibration Calibration Correction', fontsize=18)
        fig.savefig('accel_calibration_output.png', dpi=300,
                    bbox_inches='tight', facecolor='#FCFCFC')
        fig.show()

        return calData

    def get_displacement_data (self):
        data = cal_data()

        #time_span = accel_data['t'][0] - accel_data['t'][-1]

        #t = np.arange(len(data)) / 100.

        # We should remove the linear trend because there is an off-set.
        data = detrend(data)  # detrend removes the mean value or linear trend from a vector or matrix

        maxP = max(data)
        minP = min(data)
        print('The max peak is ' + str(maxP))
        print('The min peak is ' + str(minP))

        # So the peak to peak would be
        # print('P to P: ' + str(abs(minP) + abs(maxP))) # this is the peak to peak accel

        # The function cumtrapz calculates the area under the curve.
        # The area under the acceleration curve, using the trapezoidal rule
        # is velocity, and the area under the velocity curve is displacment.
        dataVelocity = cumtrapz(data, x=None, dx=0.01)

        order = 1  # Order is the order of the filter -
        fs = 100.0  # fs is the sampling rate, in Hz
        corner = 0.1  # corner is the frequency cut off, so we will keep all data less
        # than 0.1 Hz and everything greater than 0.1 Hz will be attenuated.
        nyq = 0.5 * fs

        # Butterworth Filter - a signal processing filter that aims for
        # as flat a frequency response as possible in the passband (aka band pass).
        b, a = butter(order, corner / nyq, btype='high', analog=False)
        dataVelocityHP= filtfilt(b, a, dataVelocity)

        dataDisplacement = cumtrapz(dataVelocityHP, x=None, dx=0.01)
        # Check what cumtrapz returns.  Notice we need a different time vector.
        # cumtrapz computes an approximation of the cumulative integral of
        # Y via the trapezoidal method with unit spacing

        order = 1  # Order is the order of the filter -
        fs = 100.0  # fs is the sampling rate, in Hz
        corner = 0.1  # corner is the frequency cut off, so we will keep all data less
        # than 5 Hz and everything greater than 5 Hz will be attenuated.
        nyq = 0.5 * fs

        # Butterworth Filter - a signal processing filter that aims for
        # as flat a frequency response as possible in the passband (aka band pass).
        b, a = butter(order, corner / nyq, btype='high', analog=False)
        dataDisplacementHP = filtfilt(b, a, dataDisplacement)

        # Since cumtrapz uses spacing of 0.01, we'll need to change the time vectors.
        tv = np.arange(len(dataVelocityHP)) / 100.
        td = np.arange(len(dataDisplacementHP)) / 100.

        maxDP = max(dataDisplacementHP)
        minDP = min(dataDisplacementHP)
        print('The max peak is ' + str(maxDP))
        print('The min peak is ' + str(minDP))

        fig = plt.figure(1)
        plt.subplot(2, 1, 1)
        plt.plot(tv, dataVelocityHP)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Velocity (m/s)')
        plt.title('Velocity and Displacement using cumptraz Integration')
        plt.subplot(2, 1, 2)
        plt.plot(td, dataDisplacementHP)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Displacement (m)')
        plt.savefig('AccelExample1.jpg')
        plt.close()

        return dataDisplacementHP

    def get_displacement_data2 (self):
        #############################
        # Main Loop to Integrate IMU
        #############################
        #
        data_indx = 1  # index of variable to integrate
        dt_stop = 5  # seconds to record and integrate

        plt.style.use('ggplot')
        plt.ion()
        fig, axs = plt.subplots(3, 1, figsize=(12, 9))
        break_bool = False
        while True:
            #
            ##################################
            # Reading and Printing IMU values
            ##################################
            #
            accel_array, t_array = [], []
            print("Starting Data Acquisition")
            [axs[ii].clear() for ii in range(0, 3)]
            t0 = time.time()
            loop_bool = False
            while True:
                try:
                    z = mpu6050_conv()  # read and convert mpu6050 data

                    t_array.append(time.time() - t0)
                    data_array = [z]
                    accel_array.append(accel_fit(data_array[data_indx],
                                                 *accel_coeffs[data_indx]))
                    if not loop_bool:
                        loop_bool = True
                        print("Start Moving IMU...")
                except:
                    continue
                if time.time() - t0 > dt_stop:
                    print("Data Acquisition Stopped")
                    break

            if break_bool:
                break
            #
            ##################################
            # Signal Filtering
            ##################################
            #
            Fs_approx = len(accel_array) / dt_stop
            b_filt, a_filt = signal.butter(4, 5, 'low', fs=Fs_approx)
            accel_array = signal.filtfilt(b_filt, a_filt, accel_array)
            #accel_array = np.multiply(accel_array, 9.80665)
            #
            ##################################
            # Print Sample Rate and Accel
            # Integration Value
            ##################################
            #
            print("Sample Rate: {0:2.0f}Hz".format(len(accel_array) / dt_stop))

            veloc_array = np.append(0.0, cumtrapz(accel_array, x=t_array))
            dist_approx = np.trapz(veloc_array, x=t_array)
            dist_array = np.append(0.0, cumtrapz(veloc_array, x=t_array))

            print("Displace in z-dir: {0:2.2f}m".format(dist_approx))
            axs[0].plot(t_array, accel_array, label="$" + mpu_labels[data_indx] + "$",
                        color=plt.cm.Set1(0), linewidth=2.5)
            axs[1].plot(t_array, veloc_array,
                        label="$v_" + mpu_labels[data_indx].split("_")[1] + "$",
                        color=plt.cm.Set1(1), linewidth=2.5)
            axs[2].plot(t_array, dist_array,
                        label="$d_" + mpu_labels[data_indx].split("_")[1] + "$",
                        color=plt.cm.Set1(2), linewidth=2.5)
            [axs[ii].legend() for ii in range(0, len(axs))]
            axs[0].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=16)
            axs[1].set_ylabel('Velocity [m$\cdot$s$^{-1}$]', fontsize=16)
            axs[2].set_ylabel('Displacement [m]', fontsize=16)
            axs[2].set_xlabel('Time [s]', fontsize=18)
            axs[0].set_title("MPU9250 Accelerometer Integration", fontsize=18)
            plt.pause(0.01)
            plt.savefig("accel_veloc_displace_integration2.png", dpi=300,
                        bbox_inches='tight', facecolor="#FCFCFC")
            return dist_array

    def get_displacement_data3(self):
        #############################
        # Main Loop to Integrate
        #############################
        #
        data_indx = 1  # index of variable to integrate
        dt_stop = 30  # seconds to record and integrate

        plt.style.use('ggplot')
        plt.ion()
        fig, axs = plt.subplots(3, 1, figsize=(12, 9))
        break_bool = False
        while True:
            #
            ##################################
            # Reading and Printing IMU values
            ##################################
            #
            accel_array, t_array = [], []
            print("Starting Data Acquisition")
            [axs[ii].clear() for ii in range(0, 3)]
            t0 = time.time()
            loop_bool = False
            while True:
                try:
                    z = mpu6050_conv()  # read and convert mpu6050 data

                    t_array.append(time.time() - t0)
                    data_array = [z]
                    accel_array.append(accel_fit(data_array[data_indx],
                                                 *accel_coeffs[data_indx]))
                    if not loop_bool:
                        loop_bool = True
                        print("Start Moving IMU...")
                except:
                    continue
                if time.time() - t0 > dt_stop:
                    print("Data Acquisition Stopped")
                    break

            if break_bool:
                break
            #
            ##################################
            # Signal Filtering
            ##################################
            #
            Fs = len(accel_array) / dt_stop
            b_filt, a_filt = signal.butter(4, 5, 'low', fs=Fs)
            accel_array = signal.filtfilt(b_filt, a_filt, accel_array)
            # accel_array = np.multiply(accel_array, 9.80665)
            #
            ##################################
            # Print Sample Rate and Accel
            # Integration Value
            ##################################
            #
            print("Sample Rate: {0:2.0f}Hz".format(len(accel_array) / dt_stop))

            veloc_array = np.zeros(len(accel_array))
            veloc_array [0] = 0

            for n in range (0, len(accel_array)):

                veloc_array[n]= veloc_array[n-1]+ accel_array [n] /Fs
                return veloc_array

            dist_approx = np.trapz(veloc_array, x=t_array)
            print ("distance is", dist_approx)


            order = 1  # Order is the order of the filter -
            fs = len(accel_array) / dt_stop
             # fs is the sampling rate, in Hz
            corner = 0.1  # corner is the frequency cut off, so we will keep all data less
            # than 0.1 Hz and everything greater than 0.1 Hz will be attenuated.
            nyq = 0.5 * fs

            # Butterworth Filter - a signal processing filter that aims for
            # as flat a frequency response as possible in the passband (aka band pass).
            b, a = butter(order, corner / nyq, btype='high', analog=False)
            veloc_arrayHP = filtfilt(b, a, veloc_array)

            disp_array = np.zeros(len(veloc_arrayHP))
            disp_array [0] = 0

            for n in range (0, len(veloc_arrayHP)):

                disp_array[n]= disp_array[n-1]+ veloc_arrayHP [n] /Fs
                return disp_array

            order = 1  # Order is the order of the filter -
            fs = len(accel_array) / dt_stop
            # fs is the sampling rate, in Hz
            corner = 0.1  # corner is the frequency cut off, so we will keep all data less
            # than 0.1 Hz and everything greater than 0.1 Hz will be attenuated.
            nyq = 0.5 * fs
            # Butterworth Filter - a signal processing filter that aims for
            # as flat a frequency response as possible in the passband (aka band pass).
            b, a = butter(order, corner / nyq, btype='high', analog=False)
            disp_arrayHP = filtfilt(b, a, disp_array)

            fig = plt.figure(1)
            plt.subplot(2, 1, 1)
            plt.plot(t_array, veloc_arrayHP)
            plt.xlabel('Time (seconds)')
            plt.ylabel('Velocity (m/s)')
            plt.title('Velocity and Displacement using euler Integration')
            plt.subplot(2, 1, 2)
            plt.plot(t_array, disp_arrayHP)
            plt.xlabel('Time (seconds)')
            plt.ylabel('Displacement (m)')
            plt.savefig('AccelExample3.jpg')
            plt.close()

            return disp_arrayHP

# create csv file to save the data
    file = open("/home/pi/Accelerometer_data2.csv", "a")
    i = 0
    if os.stat("/home/pi/Accelerometer_data2.csv").st_size == 0:
        file.write("Time,a, Z\n")

    # Create figure for plotting
    fig = plt.figure()
    ax = fig.add_subplot(1, 1, 1)
    xs = []
    ys = []

    def animate(i, xs, ys):

        # Read acceleration from MPU6050
        DisplacementData = mpu.get_displacement_data()
        #DisplacementData= mpu.get_displacement_data2()
        #DisplacementData= mpu.get_displacement_data3()

        # append data on the csv file
        #i = i + 1
        now = dt.now()
        file.write(
            str(now) + "," + str(get_accel_data['z']) +","+ str(cal_data()) + "," + str(DisplacementData()) + "\n")
        file.flush()

        # Add x and y to lists
        xs.append(dt.now().strftime('%H:%M:%S.%f'))
        ys.append(float(DisplacementData['z']))

        # Limit x and y lists to 20 items
        xs = xs[-10:]
        ys = ys[-10:]

        time.sleep(0.01)

        # Draw x and y lists
        ax.clear()
        ax.plot(xs, ys)

        # Format plot
        plt.xticks(rotation=45, ha='right')
        plt.subplots_adjust(bottom=0.30)
        plt.title('MPU6050 Acceleration over Time')
        plt.ylabel('-Acceleration')


    # show real-time graph
    ani = animation.FuncAnimation(fig, animate, fargs=(xs, ys), interval=1000)
    plt.show()


    def get_frequency (self):
        stopped= false
        while not stopped:

            data = get_displacement_data()
            # data= get_displacement_data2()
            # data= get_displacement_data3()
            t = []
            t0 = time.time()
            t.append(time.time() - t0)
            peak, _= find_peaks(data, height= none, treshold= none, distance=none, prominence=1)
            frequency= (len(peak)/t)*60
            print('frequency is ' + str(frequency))
            plt.plot(data)
            plt.plot(peaks, data[peaks], "ob")
            plt.show()


#Height: it can be a number or an array and it is used to specify the minimal height that a peak should have,
# in order to be identified;
#Threshold: is the required vertical distance between a peak and its neighboring, very useful in the case
# of noisy functions where we want to avoid selecting peaks from the noise;
#Distance: is the required minimal horizontal distance between neighboring peaks; it can be really useful
# in cases in which we have some knowledge about the periodicity of the peaks.

if __name__ == '__main__':

    mpu = Accelerometer(0x68)
    mpu.get_displacement_data()
    #mpu.get_displacement_data2(self)
    #mpu.get_displacement_data3()
    #mpu. get_frequency()


time.sleep(0.1)







