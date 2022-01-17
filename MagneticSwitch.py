import time
from RPi.GPIO import GPIO

class MagneticSwitch:
    def __init__(self, pin):
        self.magPIN = pin
        GPIO.setmode(GPIO.BOARD) # broadcom
        GPIO.setup(self.magPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def testSwitch(self):
        # Verify the switch works
        count = 0
        while count < 10:
            print(GPIO.input(self.magPIN))
            count += 1

    def checkSwitch(self):
        # Returns true if magnet has been activated
        if GPIO.input(self.magPIN):
            return True
        else:
            return False
