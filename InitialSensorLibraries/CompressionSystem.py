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

    def testSwitch(self, cycles=3):
        print("Testing compression system:")
        bottom_init = GPIO.input(self.bottomPIN)

        print("Do 3 rounds of compressions (push down 3 times)")

        bottomTimes = []
        cycle = 0
        hitBottom = False
        b_prev = bottom_init

        t0 = time.time()

        while cycle < cycles:
            b = GPIO.input(self.bottomPIN)

            if b != b_prev:
                bottomTimes.append(time.time() - t0)
                hitBottom = True
                b_prev = b

            if hitBottom:
                cycle += 1
                hitBottom = False

            #time.sleep(0.3)

        cycleTime = []
        for i in range(len(bottomTimes)-1):
            cycleTime.append(bottomTimes[i] - bottomTimes[i+1])
        print("Average frequency:", 1/np.mean(cycleTime))

        print("Finished testSwitch function for compressions.")

    def checkCompressions(self):
        """
        Check compressions depth and frequency.
        :return cycle: number of complete compressions completed
        """
        bottomTimes = []
        hitBottom = False

        cycle = 0
        cycling = True

        t0 = time.time()
        b_prev = GPIO.input(self.bottomPIN)
        while cycling:
            bottom = GPIO.input(self.bottomPIN)

            if bottom != b_prev:
                bottomTimes.append(time.time() - t0)
                hitBottom = True
                b_prev = bottom

            if hitBottom:
                #time.sleep(1)
                cycle += 1
                hitBottom = False

            if (time.time()-t0) - bottomTimes[-1] > 1.2:
                cycling = False

            #time.sleep(0.3)

        print("Number of compressions:", len(bottomTimes))

        cycleTime = []
        for i in range(len(bottomTimes)-1):
            cycleTime.append(bottomTimes[i] - bottomTimes[i+1])
        print("Average frequency:", 1/np.mean(cycleTime))

        print("Finished compressions.")

        return cycle


if __name__ == '__main__':
    # ms = MagneticSwitch(22, True)  # BCM 25
    cs = CompressionSystem(6)    # BCM 29, BCM 31

    cs.testSwitch(3)

    cs.checkCompressions()

    #try:
    #    while 1:
    #        cs.testSwitch(3)
    #except KeyboardInterrupt:
    #    print("Testing complete.")


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
