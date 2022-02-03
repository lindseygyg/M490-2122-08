import smbus
import time
import os
import matplotlib.animation as animation
import numpy as np  # This is the package needed for functions.
from scipy.integrate import cumtrapz
from scipy.signal import detrend
import matplotlib
import matplotlib.pyplot as plt

import csv

# matplotlib.use('Agg')   #This is required to run matplotlib on Google Chrome.

# NEW PLAN: OUTPUT DATA TO CSV FILE. READ AND UPDATE CSV FILE AT EVERY POINT.

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

    def get_displacement(self):
        accel_data = {'t': [], 'z': []}
        displacement_data = {'t': [], 'z': []}

        count = 0
        stopped = False

        while not stopped:
            a_data = self.get_accel_data()
            if a_data is not None:
                if count == 0:
                    t0 = time.time()
                accel_data['t'].append(time.time()-t0)
                #accel_data['t'].append(time.time())
                accel_data['z'].append(a_data)
                count += 1

            if count % 125 == 0:
                # get displacement based on the next ten datapoints
                data = self.get_displacement_data(accel_data)

                displacement_data['z'].append(data)

                #displacement_data['t'].append(accel_data['t'])
                td = np.arange(len(displacement_data['z']))/100.
                displacement_data['t'] = td

                accel_data = {'t': [], 'z': []}

            # TODO: CHECK HOW SENSITIVE ACCELEROMETER IS
            #if accel_data['z'][-5] is not None and accel_data['z'][-1]== accel_data['z'][-5]:
             #       stopped = True

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
           
    def get_displacement_data(self, accel_data):
        data = accel_data['z']
        
        time_span = accel_data['t'][0] - accel_data['t'][-1]
        
        t = np.arange(len(data))/100.
    
        # We should remove the linear trend because there is an off-set.
        data = detrend(data)    # detrend removes the mean value or linear trend from a vector or matrix
        
        maxP = max(data)
        minP = min(data)
        #print('The max peak is ' + str(maxP))
        #print('The min peak is ' + str(minP))
        
        # So the peak to peak would be
        #print('P to P: ' + str(abs(minP) + abs(maxP))) # this is the peak to peak accel
        
        # The function cumtrapz calculates the area under the curve.
        # The area under the acceleration curve, using the trapezoidal rule
        # is velocity, and the area under the velocity curve is displacment.
        dataVelocity = cumtrapz(data, x=None, dx=0.01)
        dataDisplacement = cumtrapz(dataVelocity, x=None, dx=0.01)
        # Check what cumtrapz returns.  Notice we need a different time vector.
        # cumtrapz computes an approximation of the cumulative integral of
        # Y via the trapezoidal method with unit spacing
        
        # Since cumtrapz uses spacing of 0.01, we'll need to change the time vectors.
        tv = np.arange(len(dataVelocity))/100.
        td = np.arange(len(dataDisplacement))/100. 
        return dataDisplacement

    def get_displacement_test(self):
        accel_data = {'t': [], 'z': []}
        displacement_data = {'t': [], 'a': [], 'z': []}
        
        print('Ctl-C to exit the test')

        try:
            count = 0
            while 1:
                a_data = self.get_accel_data()

                if a_data is not None:
                    if count == 0:
                        t0 = time.time()
                    accel_data['t'].append(time.time()-t0)
                    #print("t", accel_data['t'])
                    
                    # offset by -9.47 to -9.52)
                    accel_data['z'].append(a_data)
                    #print("a", accel_data['z'])
                    count += 1

                if count % 125 == 0:
                    # get displacement based on the next ten datapoints
                    data = self.get_displacement_data(accel_data)

                    displacement_data['z'].extend(data)
                    #print("z", displacement_data['z'])
                    
                    displacement_data['a'].extend(accel_data['z'])

                    displacement_data['t'].extend(accel_data['t'])
                    #td = np.arange(len(displacement_data['z']))/100.
                    #displacement_data['t'] = td
                    
                    #print(displacement_data['z'])
                    #print(displacement_data['t'])
                    
                    # rewrite it from scratch 
                    with open('data.csv', mode='w') as csv_file:
                        header = ['t', 'a', 'z']
                        writer = csv.DictWriter(csv_file, fieldnames=header)

                        writer.writeheader()

                        for i in range(len(displacement_data['t'])-1):
                            try:
                                #print(i)
                                writer.writerow({'t': displacement_data['t'][i], 'a': displacement_data['a'][i], 'z': 1000*round(displacement_data['z'][i], 5)})
                            # print(displacement_data['t'][i], ", ", displacement_data['z'][i])
                            except IndexError:
                                pass

                    self.plot_from_csv(displacement_data['t'], displacement_data['z'])
                    accel_data = {'t': [], 'z': []}

        except KeyboardInterrupt:
            #self.plot_from_csv(displacement_data['t'], displacement_data['z'])
            return
            #return accel_data

    def plot_from_csv1(self):
        AnimateDisplacement

    def plot_from_csv(self, xs, ys):
        fig = plt.figure()
        ax1 = fig.add_subplot(1,1,1)

        #plt.axis([0, 10, 0, 1])
        
        for i in range(len(xs)):
            try:
                x = xs[i]
                y = ys[i]  # maybe take average of every 10 data points
                plt.scatter(x, y)
                plt.pause(0.05) # too slow?
            except IndexError:
                pass

        plt.show()

    def get_displacement_2(self):
        """
        with cumtrapz
        :return:
        """
        t = []
        zdd = []
        zd = []
        z = []

        count = 0
        stopped = False

        while not stopped:
            a_data = self.get_accel_data()

            if a_data is not None:
                if count == 0:
                    t0 = time.time()
                t.append(time.time()-t0)
                zdd.append(a_data)
                count += 1

            if count % 125 == 0:
                zd = cumtrapz(zdd, t, initial=0)
                z = cumtrapz(zd, t, initial=0)
                print("zd", zd)
                print("z", z)
                
                plt.plot(t, z, 'ro')
                plt.draw()
                plt.pause(0.5)

            #if zdd[-1] == zdd[-5]:
            if count > 1000000:
                stopped = True


            """
            Alternative?
            plt.ion()
            fig = plt.figure()
            ax = fig.add_subplot(111)
            line1, = ax.plot(x, y, 'b-')
  
            # for loop
            line1.set_ydata(y)
            fig.canvas.draw()
            fig.canvas.flush_events()
            """


if __name__ == '__main__':
    # TEST IMMOBILE (SHOULD BE 0; CHECK FOR DRIFT)
    # TEST FREEFALL - SHOULD BE GRAVITY (THEN RECORD COMPLETE FALL - IMMOBILE, FALL, REST)
    # TEST: PENDULUM STYLE

    mpu = Accelerometer(0x68)
    
    data = mpu.get_displacement_2()
    
    
    #data = mpu.get_displacement_test()
    
    #print("csv1 AnimateDisplacement")
    #import AnimateDisplacement
    
    #mpu.plot_from_csv_1()
        
    #for i in range(len(data['z'])):
    #    print(data['t'][i], "\t", data['z'][i])
            
    #fig = plt.figure(1)
    #plt.subplot(1, 1, 1)
    #plt.plot(data['t'], data['z'])
    #plt.xlabel('x-axis')
    #plt.ylabel('displacement')
    #plt.title('output')
    #plt.show()

    print("Testing complete.")
