import smbus
import time

# for animation
from time import sleep
import os
from datetime import datetime as dt
import matplotlib.pyplot as plt
import matplotlib.animation as animation

# for displacement
import numpy as np # This is the package needed for functions.
from scipy.integrate import cumtrapz
from scipy.signal import detrend
import math
import sys
import matplotlib
matplotlib.use('Agg') #This is required to run matplotlib on Google Chrome.
import matplotlib.pyplot as plt

class mpu6050:

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
        self.bus.write_byte_data(self.address, self.PWR_MGMT_1, 0x00)
        # I2C communication methods

    def read_i2c_word(self, register):
        # Read the data from the registers
        high = self.bus.read_byte_data(self.address, register)
        low = self.bus.read_byte_data(self.address, register + 1)

        value = (high << 8) + low

        if (value >= 0x8000):
            return -((65535 - value) + 1)
        else:
            return value

    def set_accel_range(self, accel_range):
        # First change it to 0x00 to make sure we write the correct value later
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, 0x00)

        # Write the new range to the ACCEL_CONFIG register
        self.bus.write_byte_data(self.address, self.ACCEL_CONFIG, accel_range)

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

    def start_accel_data(self):
        accel_data = {'x': [], 'y': [], 'z': []}
          
        tm = time.time()
        current_tm = 0

        #TODO: MODIFY TO COUNT TO 30 PEAKS OR SOMETHING
        while (current_tm < tm + 10):
            a_data = mpu.get_accel_data()
            accel_data['x'].append(a_data['x'])
            accel_data['y'].append(a_data['y'])
            accel_data['z'].append(a_data['z'])

            current_tm = time.time()
         
        return accel_data
      
    def get_accel_data(self, g=False):
        x = self.read_i2c_word(self.ACCEL_XOUT0)
        y = self.read_i2c_word(self.ACCEL_YOUT0)
        z = self.read_i2c_word(self.ACCEL_ZOUT0)

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

        x = x / accel_scale_modifier
        y = y / accel_scale_modifier
        z = z / accel_scale_modifier

        if g is True:
            return {'x': x, 'y': y, 'z': z}
        elif g is False:
            x = x * self.GRAVITIY_MS2
            y = y * self.GRAVITIY_MS2
            z = z * self.GRAVITIY_MS2
            return {'x': x, 'y': y, 'z': z}

    def set_filter_range(self, filter_range=FILTER_BW_5):
        """Sets the low-pass bandpass filter frequency"""
        # Keep the current EXT_SYNC_SET configuration in bits 3, 4, 5 in the MPU_CONFIG register
        EXT_SYNC_SET = self.bus.read_byte_data(self.address, self.MPU_CONFIG) & 0b00111000
        return self.bus.write_byte_data(self.address, self.MPU_CONFIG, EXT_SYNC_SET | filter_range)

    def get_all_data(self):
        accel = self.get_accel_data()
        return [accel]

    def plot_acceleration(self):
        #create csv file to save the data
        file = open("/home/pi/Accelerometer_data2.csv", "a")
        i = 0
        if os.stat("/home/pi/Accelerometer_data2.csv").st_size == 0:
                file.write("Time,X,Y,Z\n")

        # Create figure for plotting
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        xs = []
        ys = []

        #show real-time graph
        #TODO: add while loop or i counter
        ani = animation.FuncAnimation(fig, self.animate(file, i, ax, xs, ys), fargs=(xs, ys), interval=1000)
        plt.show()

    def animate(self, file, i, ax, xs, ys):
        # Read acceleration from MPU6050
        accel_data = mpu.get_accel_data()

        #append data on the csv file
        i=i+1
        now = dt.now()
        file.write(str(now)+","+str(accel_data['x'])+","+str(accel_data['y'])+","+str(accel_data['z'])+"\n")
        file.flush()

        # Add x and y to lists
        xs.append(dt.now().strftime('%H:%M:%S.%f'))
        ys.append(float(accel_data['z']))

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

    def get_displacement(self, acceleration_data=None):
        if acceleration_data is None:
            accel_data = mpu.start_accel_data()
            data = accel_data['z']
        else:
            if 'z' in acceleration_data:
                data = acceleration_data['z']
            else:
                data = acceleration_data

        # The data is sampled at 100 Hz.  What is the time length of the file?
        # One Hz is 1/sec, so that means we are taking 100 samples every second.
        print('Here is the time span: ' + str(float(len(data))/100.) + ' seconds')
        # Here is the time span: 855.7 seconds

        # Let's print the number of samples:
        print('There are ' + str(float(len(data))) + ' samples.')
        # Result - There are 85570.0 samples.

        # Now plot your data to see what you have.
        # Grab a time vector (t).

        # Why are we dividing by 100? Think sample rate. The data is sampled at 100Hz.
        t = np.arange(len(data))/100.

        fig = plt.figure()
        plt.plot(t,data)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Acceleration (m/s^2)')
        plt.title('Acceleration vs. Time')
        plt.savefig('AccelExample1.jpg')
        plt.close()

        # What is the peak to peak acceleration?
        maxP = max(data)
        minP = min(data)
        print('The max peak is ' + str(maxP))
        print('The min peak is ' + str(minP))

        # We should remove the linear trend because there is an off-set.
        data = detrend(data)
        # detrend removes the mean value or linear trend from a vector or matrix

        # Okay find the min and max again.
        maxP = max(data)
        minP = min(data)
        print('The max peak is ' + str(maxP))
        print('The min peak is ' + str(minP))

        # So the peak to peak would be
        print('P to P: ' + str(abs(minP) + abs(maxP)))
        print('This is the peak to peak acceleration.')

        #The function cumtrapz calculates the
        # area under the curve.  The area under the acceleration curve, using the
        # trapezoidal rule, is velocity, and the area under the velocity curve, using
        # the trapezoidal rule, is displacment.
        dataVelocity = cumtrapz(data, x=None, dx=0.01)
        dataDisplacement = cumtrapz(dataVelocity, x=None, dx=0.01)
        # Check what cumtrapz returns.  Notice we need a different time vector.
        # cumtrapz computes an approximation of the cumulative integral of
        # Y via the trapezoidal method with unit spacing
        # Since cumtrapz uses spacing of 0.01, we'll need to change the time vectors.

        tv = np.arange(len(dataVelocity))/100.
        td = np.arange(len(dataDisplacement))/100.

        fig = plt.figure(1)
        plt.subplot(2, 1, 1)
        plt.plot(tv, dataVelocity)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Velocity (m/s)')
        plt.title('Velocity and Displacement using cumptraz Integration')
        plt.subplot(2, 1, 2)
        plt.plot(td, dataDisplacement)
        plt.xlabel('Time (seconds)')
        plt.ylabel('Displacement (m)')
        plt.savefig('AccelExample5.jpg')
        plt.close()

if __name__ == "__main__":
    mpu = mpu6050(0x68)

    accel_data = {}
    try:
        while 1:
            accel_data = mpu.start_accel_data()
            #print("Ax:{:.4f}\tAy:{:.4f}\tAz:{:.4f}".format(accel_data['x'], accel_data['y'], accel_data['z']))
            print(accel_data)
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("Testing complete.")

    mpu.get_displacement(accel_data)

