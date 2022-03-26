import time
import RPi.GPIO as GPIO
import numpy as np


class CompressionSystem:
    """
    Using two buttons/touch sensors
    "Top" button is activated when compression system is UP
    "Bottom" button is activated when compression system is DOWN.
    For now, one cycle is accepted if the compressions go all the way down and all the way up.
    """
    def __init__(self, pin):
        self.bottomPIN = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.bottomPIN, GPIO.IN)
        
    def testSwitch1(self):
        print("Testing sensor:")
        bottom_init = GPIO.input(self.bottomPIN)

        times = []
        count = 0
        prev = bottom_init
        print("initial:", prev)
        
        t0 = time.time()
        
        while count < 20:
            current = GPIO.input(self.bottomPIN)
            print(current)
            if current != prev:
                print("Status changed")
                times.append(time.time() - t0)
            count += 1
            time.sleep(1)
            prev = current
            
        print(times)
        
    def testSwitch2(self):
        """
        Outputs only if status changes
        """
        print("Testing sensor:")
        bottom_init = GPIO.input(self.bottomPIN)
        print(bottom_init)

        times = []
        count = 0
        prev = bottom_init
        
        t0 = time.time()
        
        while count < 100:
            current = GPIO.input(self.bottomPIN)
            if current != prev:
                times.append(time.time() - t0)
                print("Status changed at", times[-1])
            count += 1
            time.sleep(.25)
            prev = current
            
        print(times)

    def testSwitch(self, cycles=3):
        print("Testing compression system:")
        
        b_prev = GPIO.input(self.bottomPIN)
        print("initial:", b_prev)

        print("Do 3 rounds of compressions (push down 3 times)")

        bottomTimes = []
        cycle = 0

        # get initial time
        # starts at top so do not add to the bottomTimes
        t0 = time.time() 
        

        while cycle < cycles:
            b = GPIO.input(self.bottomPIN)

            if b != b_prev:
                b_prev = b
                t = time.time() - t0
                print("new changed prev:", b_prev, "at", t)
                bottomTimes.append(t)
                cycle += 1

            time.sleep(0.3)

        cycleTime = []
        for i in range(len(bottomTimes)-1):
            cycleTime.append(bottomTimes[i+1] - bottomTimes[i])
        print("Average frequency:", 1/np.mean(cycleTime))

        print("Finished testSwitch function for compressions.")

    def checkCompressions(self):
        """
        Check compressions depth and frequency.
        :return cycle: number of complete compressions completed
        :return freq: frequency in units of compressions per minute
        """
        bottomTimes = []
        hitBottom = False

        cycle = 0
        cycling = True

        t0 = time.time()
        b_prev = GPIO.input(self.bottomPIN)
        #print("initial:", b_prev)
        
        while cycling:
            bottom = GPIO.input(self.bottomPIN)
            
            try:
                if bottom != b_prev:
                    bottomTimes.append(time.time() - t0)
                    b_prev = bottom
                    cycle += 1
            
                elif (time.time()-t0) - bottomTimes[-1] > 2:
                    cycling = False
                    
            except IndexError:
                pass

            time.sleep(0.3)

        #print("Number of compressions:", len(bottomTimes))

        cycleTime = []
        for i in range(len(bottomTimes)-1):
            cycleTime.append(bottomTimes[i+1] - bottomTimes[i])
            
        entireTime = bottomTimes[-1] - bottomTimes[0] # s

        freq = cycle*60/entireTime
        
        print("frequency:", freq)
        print("Number of compressions:", cycle)

        # TODO: calculate standard deviation, remove outliers, etc.
        
        #print("Average frequency:", freq, "compressions per minute")
        #print("Finished compressions:", cycle, "at", freq)

        return cycle,freq


if __name__ == '__main__':
    # ms = MagneticSwitch(22, True)  # BCM 25
    cs = CompressionSystem(24)    # BCM 29, BCM 31

    #cs.testSwitch1()
    #cs.testSwitch2()
    #cs.testSwitch(3)
    
    cs.checkCompressions()

"""
# OBSOLETE FUNCTION:
    def CheckCompression_TopBottom
        top = GPIO.input(self.topPIN)
        bottom = GPIO.input(self.bottomPIN)

        bottomTimes = []
        topTimes = []

        hitBottominCycle = False
        hitBottom = False
        hitTop = False

        t0 = time.time()

        cycle = 0

        cycling = True
        while cycling:
            if bottom and not hitBottominCycle:
                bottomTimes.append(time.time() - t0)
                hitBottominCycle = True
                hitBottom = True
            # TODO: potential elif bottom and hitBottominCycle: output "decompress fully"

            if top and hitBottominCycle:
                topTimes.append(time.time() - t0)
                hitBottominCycle = True
                hitTop = True
            # TODO: potential elif here for cycling=False

            if hitBottom and hitTop:
                time.sleep(1)
                cycle += 1
                hitBottom = False
                hitBottominCycle = False
                hitTop = False

            if not hitTop and not hitBottom or hitTop and not hitBottom:
                t1 = time.time()
                while top:
                    t2 = time.time()
                    if t2 - t1 > 1:
                        cycling = False
                        break

            time.sleep(0.3)

        print("Number of compressions:", len(bottomTimes))

        cycleTime = []
        for i in range(len(bottomTimes)-1):
            cycleTime.append(bottomTimes[i] - bottomTimes[i+1])
        print("Average frequency:", 1/np.mean(cycleTime))
"""
