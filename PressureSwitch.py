import time
import board
import adafruit_mprls

class PressureSwitch:

    def __init__(self):
        i2c = board.I2C()
        self.mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)
        self.update_atm()

    def update_atm(self, printout=None):
        self.atm = self.adjust_p(self.mpr.pressure)
        if printout is not None:
            print("Atmospheric pressure updated:", self.atm)

    def adjust_p(self, pressure_value):
        # Adjust pressure reading to for easier manipulation
        # Blowing only changes pressure in units of 1/10-1/100
        return ((pressure_value/68.947572932-14)*100)

    def checkSwitch(self, t=10):
        """
        Requires a time(sec) input that determines how long it should check for the rescue
        breaths to be completed. Check if the first and second rescue breath are completed
        :param t: time limit
        :return: True if rescue breaths completed
        """
        self.update_atm(printout=1)
        first_breath = self.pressure_check(t)
        time.sleep(2)
        self.update_atm(printout=1)
        sec_breath = self.pressure_check(t)

        if first_breath and sec_breath:
            return True
        else:
            return False
    
    def pressure_check(self, t):
        """
        Requires a time(sec) input that determine how long it should check
        for the rescue breath to be completed. Check if the pressure has increased.
        :param t: time limit (int)
        :return: True if pressure change is greater than 10
        """
        while t:
            pressure_value = self.adjust_p(self.mpr.pressure)
            if (self.atm - pressure_value) > 10:
                return True
            time.sleep(1)
            # print(t)
            t -= 1
        return False

    def testSwitch(self):
        self.update_atm(printout=1)
        print("Get ready to blow (see pressure change)")
        time.sleep(5)
        print("Updating p reading (1st blow)...")
        self.update_atm(printout=1)
        print("Blow one more time.")
        time.sleep(7)
        print("Updating p reading (2nd blow)...")
        self.update_atm(printout=1)
        print("Finished testSwitch function.")


if __name__ == '__main__':
    ps = PressureSwitch()
    #ps.testSwitch()
    #if ps.checkSwitch(10):
    #    print('It worked')
    #else:
    #    print("It did not work")
    try:
        while 1:
            ps.update_atm()
            print(ps.atm)
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("done.")
