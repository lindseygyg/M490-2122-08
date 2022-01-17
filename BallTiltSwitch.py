import time
from RPi.GPIO import GPIO

class BallTiltSwitch:
    def __init__(self, pin):
        self.tiltPIN = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.tiltPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def testSwitch(self):
        count = 0
        while count < 10:
            print(GPIO.input(self.tiltPIN))
            count += 1

    def checkSwitch(self):
        # Returns true if ball tilt switch is tilted
        # Flat returns 1; tilted returns 0
        if not GPIO.input(self.tiltPIN):
            return True
        else:
            return False
