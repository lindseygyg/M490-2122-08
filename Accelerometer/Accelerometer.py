import smbus
import time

import numpy as np  # This is the package needed for functions.

import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.integrate import cumtrapz, trapz
from scipy import signal

#from mpu9250_i2c import *   # TRY THIS ONE????????

class Accelerometer:

    def __init__(self, address, bus=1):
        self.address = address
        self.bus = smbus.SMBus(bus)

        self.GRAVITIY_MS2 = 9.80665
        self.ACCEL_RANGE_2G = 0x00

        self.ACCEL_SCALE_MODIFIER_2G = 16384.0

        self.ACCEL_XOUT0 = 0x3B
        self.ACCEL_YOUT0 = 0x3D
        self.ACCEL_ZOUT0 = 0x3F

        self.PWR_MGMT_1 = 0x6B
        self.FILTER_BW_5 = 0x06

        # Wake up the MPU-6050 since it starts in sleep mode
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, self.FILTER_BW_5)

        self.offsets = None

        # TODO: TEST IF THIS WORKS HERE
        # Because if it is in the manikin, will already be "face-up" in position
        # self.accel_coeffs = self.calibration()

    def read_i2c_word(self, register):
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    def get_accel_data(self, g=False):
        try:
            ax = self.read_i2c_word(self.ACCEL_XOUT0)
            ay = self.read_i2c_word(self.ACCEL_YOUT0)
            az = self.read_i2c_word(self.ACCEL_ZOUT0)
        except OSError:
            print("Disconnected")
            return

        accel_scale_modifier = self.ACCEL_SCALE_MODIFIER_2G

        ax = ax / accel_scale_modifier
        ay = ay / accel_scale_modifier
        az = az / accel_scale_modifier

        if g is True:
            return ax, ay, az
        elif g is False:
            ax = ax * self.GRAVITIY_MS2
            ay = ay * self.GRAVITIY_MS2
            az = az * self.GRAVITIY_MS2

            return ax, ay, az

    def get_manual_offsets(self):
        # TODO: GET MANUAL OFFSETS FROM CURVE-FITTING FUNCTION POTENTIALLY

        og_data = {'x': [], 'y': [], 'z': []}

        for i in range(0, 10):
            ax, ay, az = self.get_accel_data(True)
            og_data['x'].append(ax)
            og_data['y'].append(ay)
            og_data['z'].append(az)

        x_offset = np.mean(og_data['x'])
        y_offset = np.mean(og_data['y'])
        z_offset = np.mean(og_data['z'])

        # offsets to ADD to data
        return -x_offset, -y_offset, -z_offset

    def set_offsets(self, arr=[[1.02497024, 0.03154761], [0.99279874, 0.05816404], [0.98322386, 0.01987004]]):
        """Shortcut: inputting offsets from saved calibration"""
        self.offsets = arr

    #####################################
    # NEW: Accel Calibration (gravity)
    #####################################
    def accel_fit(self, x_input, m_x, b):
        #print("x_input:", x_input, "m:", m_x, "b", b)
        return (m_x*x_input) - b  # fit equation for accel calibration

    def accel_fit_sin(self, x_input, amp, w, p, o):
        return amp * np.sin(w*x_input + p) + o  # std sin fit equation for accel calibration

    def get_raw_accel_data(self, g=False):
        """
        Testing purposes; outputs data every second
        :param g: if g is true, outputs in units of gravity instead of m/s^2
        """
        imu_devs = ["ACCELEROMETER"]
        imu_labels = ["x-dir","y-dir","z-dir"]

        if g is True:
            imu_units = ["g","g","g"]  #,"degC"]
        else:
            imu_units = ["m/ss","m/ss","m/ss"]

        ax, ay, az = self.get_accel_data(g)

        # Reading and Printing IMU values
        print(50*"-")
        for imu_ii,imu_val in enumerate([ax,ay,az]):
            if imu_ii%3==0:
                print(20*"_"+"\n"+imu_devs[int(imu_ii/3)]) # print sensor header

            # Print Data
            print("{0}: {1:3.2f} {2}".format(imu_labels[imu_ii%3],imu_val,imu_units[imu_ii]))

        time.sleep(1)

    def calibration(self, cal_size=1000):
        """
        Calibrating acceleration data from get_accel;
        From: https://makersportal.com/blog/calibration-of-an-inertial-measurement-unit-imu-with-raspberry-pi-part-ii#accel
        Call set_offsets to avoid doing this every time
        :param cal_size: number of data points
        :return: offsets
        """
        print("-"*50)
        print("Accelerometer Calibration")
        mpu_offsets = [[], [], []]    # offset array to be printed
        axis_vec = ['z', 'y', 'x']    # axis labels
        cal_directions = ["upward", "downward", "perpendicular to gravity"]   # direction for IMU cal
        cal_indices = [2, 1, 0]   # axis indices

        for xyz_index, xyz in enumerate(axis_vec):
            ax_offsets = [[], [], []]
            print("-"*50)

            for direc_ii, direc in enumerate(cal_directions):   # index direction and direction
                input("-"*8+" Press Enter and Keep IMU Steady to Calibrate the Accelerometer with the "+xyz+"-axis pointed "+direc)
                # [mpu6050_conv() for ii in range(0, cal_size)]    # clear buffer between readings - cannot do this
                mpu_array = []
                while len(mpu_array) < cal_size:
                    try:
                        ax, ay, az = self.get_accel_data(True)
                        mpu_array.append([ax, ay, az])  # append to array
                    except:
                        continue
                ax_offsets[direc_ii] = np.array(mpu_array)[:, cal_indices[xyz_index]]  # offsets for direction

            # Use three calibrations (+1g, -1g, 0g) for linear fit
            popts, _ = curve_fit(self.accel_fit, np.append(np.append(ax_offsets[0], ax_offsets[1]), ax_offsets[2]),
                                 np.append(np.append(1.0*np.ones(np.shape(ax_offsets[0])), -1.0*np.ones(np.shape(ax_offsets[1]))), 0.0*np.ones(np.shape(ax_offsets[2]))),
                                 maxfev=10000)

            mpu_offsets[cal_indices[xyz_index]] = popts    # place slope and intercept in offset array

        print(mpu_offsets)
        print('Accelerometer Calibrations Complete')
        self.offsets = mpu_offsets
        return mpu_offsets

    def calibrated_data(self, z_data=True, cal_size=1000):
        """
        Outputs calibrated data for testing purposes
        - calibration from self.calibration() otherwise from saved offsets
        :param cal_size: number of data points
        :param z_data: True to return data from this test
        :return:
        """
        # Accelerometer Gravity Calibration
        accel_labels = ['a_x', 'a_y', 'a_z']      # labels for plots

        if self.offsets is None:
            accel_coeffs = self.calibration(cal_size)   # grab accel coefficients
        else:
            accel_coeffs = self.offsets

        print(accel_coeffs)

        off = self.get_manual_offsets()

        # get new accel data
        data = np.array([self.get_accel_data(True) for ii in range(0, cal_size)])    # new values

        # Plot with and without offsets
        plt.style.use('ggplot')
        fig, axs = plt.subplots(2, 1, figsize=(12,9))

        for ind in range(0, 3):
            axs[0].plot(data[:,ind], label='${}$, Uncalibrated'.format(accel_labels[ind]))
            #axs[1].plot(self.accel_fit(data[:, ind], *accel_coeffs[ind]), label='${}$, Calibrated'.format(accel_labels[ind]))
            axs[1].plot(data[:, ind]+off[ind], label='${}$, Calibrated'.format(accel_labels[ind]))

        axs[0].legend(fontsize=14); axs[1].legend(fontsize=14)
        axs[0].set_ylabel('$a_{x,y,z}$ [g]', fontsize=18)
        axs[1].set_ylabel('$a_{x,y,z}$ [g]', fontsize=18)
        axs[1].set_xlabel('Sample', fontsize=18)
        axs[0].set_ylim([-2, 2]); axs[1].set_ylim([-2, 2])
        axs[0].set_title('Accelerometer Calibration Calibration Correction', fontsize=18)

        fig.savefig('accel_calibration_output.png', dpi=300,
                    bbox_inches='tight', facecolor='#FCFCFC')
        fig.show()

        if z_data is True:
            return data     # calibrated data
        else:
            return

    def sine_curve_fitting(self, t=10):
        """
        # Rasha's link: https://www.mathworks.com/matlabcentral/answers/121579-curve-fitting-to-a-sinusoidal-function
        :param t: time limit
        :return:
        """
        # t_array = np.arange(0, 10, 0.1)     # np.linspace(-5, 5, num=50)
        # accel_array = np.sin(t_array)

        accel_array, t_array = [], []
        data_indx = 2  # index of variable to integrate (z)

        print("Starting Data Acquisition")
        t0 = time.time()
        dt = t0

        while dt < t:
            ax, ay, az = self.get_accel_data(True)

            t_array.append(time.time()-t0)
            data_array = [ax, ay, az]
            accel_array.append(data_array[data_indx])

            dt = time.time() - t0

        params, _ = curve_fit(self.accel_fit_sin, t_array, accel_array, maxfev=10000)

        print(params)

        fig, ax = plt.subplots()
        ax.plot(t_array, accel_array, '-o')     # original data points

        new_func = params[0] * np.sin(t_array*params[1] + params[2])
        ax.plot(t_array, new_func)

        ax.set_title('Test data plot')
        plt.show()

        # output trial frequency based on average peaks
        self.get_frequency(t_array, new_func)  # both should be arrays

    def integration_test(self, input_test_data=None):
        """
        Graphs with and without filter for visual/testing purposes
        :param input_test_data: None if get data from mpu, 1 to get numpy sine function
        """
        data_indx = 2  # index of variable to integrate
        dt_stop = 10  # seconds to record and integrate

        plt.style.use('ggplot')
        plt.ion()
        fig, axs = plt.subplots(3, 2, figsize=(12, 9))
        break_bool = False

        while True:
            ##################################
            # Reading and Printing IMU values
            ##################################
            accel_array, t_array = [], []

            print("Starting Data Acquisition")
            [axs[ii].clear() for ii in range(0, 3)]
            t0 = time.time()
            loop_bool = False

            if input_test_data is None:
                off = self.get_manual_offsets()     # todo: see if necessary
                while True:
                    ax, ay, az = self.get_accel_data(True)
                    t_array.append(time.time()-t0)
                    data_array = [ax, ay, az]
                    accel_array.append(data_array[data_indx]+off[data_indx])

                    if not loop_bool:
                        loop_bool = True
                        print("Start Moving IMU...")

                    if time.time() - t0 > dt_stop:
                        print("Data Acquisition Stopped")
                        break_bool = True
                        break

                if break_bool:
                    break

            elif input_test_data == 1:
                t_array = np.arange(0, 10, 0.1)     # np.linspace(-5, 5, num=50)
                accel_array = np.sin(t_array)

            else:
                t_array = input_test_data[0]
                accel_array = input_test_data[1]

        ##################################
        # Signal Filtering
        ##################################
        accel_arrayHP = np.multiply(accel_array, self.GRAVITIY_MS2)
        fs = len(accel_array) / dt_stop     # fs is the sampling rate, in Hz

        ##################################
        # Print Sample Rate and Accel
        # Integration Value
        ##################################
        print("Sample Rate: {0:2.0f}Hz".format(len(accel_arrayHP) / dt_stop))

        veloc_array = np.zeros(len(accel_arrayHP))

        for n in range(1, len(accel_array)):
            veloc_array[n] = veloc_array[n-1] + accel_arrayHP[n]/fs

        order = 1  # Order is the order of the filter -
        fs = len(accel_array) / dt_stop     # fs is the sampling rate, in Hz
        corner = 0.1  # corner is frequency cut off, so we will keep all data less
        nyq = 0.5 * fs

        # Butterworth Filter - a signal processing filter that aims for
        # as flat a frequency response as possible in the pass band (aka band pass).
        b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
        veloc_arrayHP = signal.filtfilt(b, a, veloc_array)

        disp_array = np.zeros(len(veloc_arrayHP))

        for n in range(1, len(veloc_arrayHP)):
            disp_array[n] = disp_array[n-1] + veloc_arrayHP[n]/fs

        order = 1  # Order is the order of the filter -
        fs = len(accel_array) / dt_stop
        # fs is the sampling rate, in Hz
        corner = 0.1  # corner is the frequency cut off, so we will keep all data less
        # than 0.1 Hz and everything greater than 0.1 Hz will be attenuated.
        nyq = 0.5 * fs
        # Butterworth Filter - a signal processing filter that aims for
        # as flat a frequency response as possible in the passband (aka band pass).
        b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
        disp_arrayHP = signal.filtfilt(b, a, disp_array)

        axs[0, 0].plot(t_array, accel_arrayHP, label="$"+mpu_labels[data_indx]+"$",
                    color=plt.cm.Set1(0), linewidth=2.5)

        axs[1, 0].plot(t_array, veloc_arrayHP,
                    label="$v_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(1), linewidth=2.5)

        axs[2, 0].plot(t_array, disp_arrayHP,
                    label="$d_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(2), linewidth=2.5)

        # UNFILTERED DATA
        axs[0, 1].plot(t_array, accel_array, label="$"+mpu_labels[data_indx]+"$",
                    color=plt.cm.Set1(0), linewidth=2.5)

        axs[1, 1].plot(t_array, veloc_array,
                    label="$v_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(1), linewidth=2.5)

        axs[2, 1].plot(t_array, disp_array,
                    label="$d_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(2), linewidth=2.5)

        [axs[ii].legend() for ii in range(0, len(axs))]
        axs[0, 0].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=12)
        axs[0, 1].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=12)

        axs[1, 0].set_ylabel('Vel [m$\cdot$s$^{-1}$]', fontsize=12)
        axs[1, 1].set_ylabel('Vel [m$\cdot$s$^{-1}$] NO FILTER', fontsize=12)

        axs[2, 0].set_ylabel('Displacement [m]', fontsize=12)
        axs[2, 1].set_ylabel('Displacement [m] NO FILTER', fontsize=12)

        axs[0, 0].set_title("MPU9250 Accelerometer Integration", fontsize=18)
        axs[0, 1].set_title("MPU9250 Accelerometer Integration NO FILTER", fontsize=18)

        axs[2, 0].set_xlabel('Time [s]', fontsize=18)
        axs[2, 1].set_xlabel('Time [s]', fontsize=18)

        plt.pause(0.01)
        plt.savefig("accel_veloc_displace_integ.png", dpi=300,
                    bbox_inches='tight', facecolor="#FCFCFC")

        return t_array, disp_arrayHP

    def get_displacement_data(self):
        """
        Rasha's test function - outputs 3 graphs (accel, vel, pos)
        Utilizes 2 high pass filters
        :return:
        """
        #############################
        # Main Loop to Integrate
        #############################
        data_indx = 2  # index of variable to integrate (z)
        dt_stop = 10  # seconds to record and integrate

        plt.style.use('ggplot')
        plt.ion()
        fig, axs = plt.subplots(3, 1, figsize=(12, 9))
        break_bool = False

        while True:
            ##################################
            # Reading and Printing IMU values
            ##################################
            accel_array, t_array = [], []

            print("Starting Data Acquisition")
            [axs[ii].clear() for ii in range(0, 3)]
            t0 = time.time()
            loop_bool = False

            off = self.get_manual_offsets()

            while True:
                try:
                    ax, ay, az = self.get_accel_data(True)
                    t_array.append(time.time()-t0)
                    data_array = [ax, ay, az]
                    accel_array.append(data_array[data_indx]+off[data_indx])

                    if not loop_bool:
                        loop_bool = True
                        print("Start Moving IMU...")
                except:
                    continue

                if time.time() - t0 > dt_stop:
                    print("Data Acquisition Stopped")
                    break_bool = True
                    break

            if break_bool:
                break

        ##################################
        # Signal Filtering
        ##################################
        accel_arrayHP = np.multiply(accel_array, self.GRAVITIY_MS2)
        fs = len(accel_array) / dt_stop     # fs is the sampling rate, in Hz

        ##################################
        # Print Sample Rate and Accel
        # Integration Value
        ##################################
        # print("Sample Rate: {0:2.0f}Hz".format(len(accel_arrayHP) / dt_stop))

        veloc_array = np.zeros(len(accel_arrayHP))

        for n in range(1, len(accel_array)):
            veloc_array[n] = veloc_array[n-1] + accel_arrayHP[n]/fs

        order = 1  # Order is the order of the filter -
        fs = len(accel_array) / dt_stop     # fs is the sampling rate, in Hz
        corner = 0.1  # corner is frequency cut off, so we will keep all data less
        nyq = 0.5 * fs

        # Butterworth Filter - a signal processing filter that aims for
        # as flat a frequency response as possible in the passband (aka band pass).
        b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
        veloc_arrayHP = signal.filtfilt(b, a, veloc_array)

        disp_array = np.zeros(len(veloc_arrayHP))

        for n in range(1, len(veloc_arrayHP)):
            disp_array[n] = disp_array[n-1] + veloc_arrayHP[n]/fs

        order = 1  # Order is the order of the filter -
        fs = len(accel_array) / dt_stop
        # fs is the sampling rate, in Hz
        corner = 0.1  # corner is the frequency cut off, so we will keep all data less
        # than 0.1 Hz and everything greater than 0.1 Hz will be attenuated.
        nyq = 0.5 * fs
        # Butterworth Filter - a signal processing filter that aims for
        # as flat a frequency response as possible in the passband (aka band pass).
        b, a = signal.butter(order, corner / nyq, btype='high', analog=False)
        disp_arrayHP = signal.filtfilt(b, a, disp_array)

        axs[0].plot(t_array, accel_arrayHP, label="$"+mpu_labels[data_indx]+"$",
                    color=plt.cm.Set1(0), linewidth=2.5)

        axs[1].plot(t_array, veloc_arrayHP,
                    label="$v_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(1), linewidth=2.5)

        axs[2].plot(t_array, disp_arrayHP,
                    label="$d_"+mpu_labels[data_indx].split("_")[1]+"$",
                    color=plt.cm.Set1(2), linewidth=2.5)

        [axs[ii].legend() for ii in range(0, len(axs))]
        axs[0].set_ylabel('Acceleration [m$\cdot$s$^{-2}$]', fontsize=16)
        axs[1].set_ylabel('Velocity [m$\cdot$s$^{-1}$]', fontsize=16)
        axs[2].set_ylabel('Displacement [m]', fontsize=16)
        axs[2].set_xlabel('Time [s]', fontsize=18)
        axs[0].set_title("MPU9250 Accelerometer Integration", fontsize=18)
        plt.pause(0.01)
        plt.savefig("accel_veloc_displace_integration.png", dpi=300,
                    bbox_inches='tight', facecolor="#FCFCFC")

        return t_array, disp_arrayHP

    def get_frequency(self, time_points, data_points):
        """
        Test function called by sine_curve_fitting to see if peaks work
        Output trial frequency based on average peaks
        :param time_points: t_array
        :param data_points: accel_array (or velocity, data)
        :return:
        """
        peaks, _ = signal.find_peaks(data_points, height=None, threshold=0.05, distance=50, prominence=1)
        print(peaks)

        total_tau = []

        for p in range(len(1, peaks)):
            tau = time_points[p-1] - time_points[p]
            total_tau.append(tau)

        if total_tau is not None:
            print(np.average(total_tau))
            print("frequency:", 1/total_tau)


if __name__ == '__main__':

    mpu = Accelerometer_LYG(0x68)

    #print("Reading raw data:")
    #for i in range(0,10):
    #    mpu.get_raw_accel_data(True)
    #    mpu.get_raw_accel_data()

    #print("manual offsets")
    #mpu.get_offsets()

    print("Now testing other new functions:")
    # REAL FUNCTION TESTS
    mpu_labels = ['a_x', 'a_y', 'a_z']   # accel labels for plots
    cal_size = 200     # number of points to use for calibration

    # accel_coeffs = mpu.calibration()  # grab accel coefficients (offsets)

    # mpu.set_offsets()

    # mpu.calibrated_data(cal_size=cal_size)

    # Record new data
    data = np.array([mpu.get_accel_data() for ii in range(0, cal_size)])     # new values

    # integration over time
    # mpu.integrate_acceleration_test(t=10, cal_size=1000)

    # mpu.get_displacement_data()
    mpu.get_frequency()

    # print("Trial within another function")
    # mpu.get_frequency()


# COEFFICIENTS FROM TESTS: [array([1.02497024, 0.03154761]), array([0.99279874, 0.05816404]), array([0.98322386, 0.01987004])]

