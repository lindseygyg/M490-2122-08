import time
import board
import adafruit_mprls

class PressureSwitch:

    def __init__(self):
        i2c = board.I2C()
        self.mpr = adafruit_mprls.MPRLS(i2c, psi_min=0, psi_max=25)
        self.update_atm()

    def udpate_atm(self, printout=None):
        self.atm = (self.mpr.pressure/68.947572932-14)*100
        if printout is not None:
            print("atmospheric pressure updated:", self.atm)

    def checkSwitch(self, t=10):
        """
        Description: 
            Requires a time(sec) input that determine how long it should check for the rescue
            breath to be completed. Check if the first and second rescue breath are completed

        Returns:
            It return True if both rescue breath are completed else returns False
            if the both rescue breaths are not completed
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
        Description:
            Requires a time(sec) input that determine how long it should check for the rescue
            breath to be completed. Check if the pressure has increase.
        
        Returns:
            Returns True if the pressure was greater than the pressure 1 second ago
            else it returns False if pressure was not greater than previous pressure value

        Called from:
            PressureCheck
        """
        while t:
            pressure_value = (self.mpr.pressure/68.947572932-14)*100
            if (self.atm - pressure_value) > 10:
                return True
            time.sleep(1)
            #print(t)
            t -= 1
        return False
    
# Check
if __name__ == '__main__':
    ps = PressureSwitch()
    if ps.checkSwitch(10):
        print('it worked')
    else:
        print("it didn't work")
