import time
import RPi.GPIO as GPIO

class MagneticSwitch:
    def __init__(self, pin, test=False):
        self.magPIN = pin
        if test:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.magPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def testSwitch(self):
        count = 0
        print("Testing touch contact for 10 seconds:")
        while count < 10:
            print(GPIO.input(self.magPIN))
            count += 1
            time.sleep(1)
        print("Finished testSwitch function.")

    def checkSwitch(self):
        # Returns true if magnet has been activated
        if GPIO.input(self.magPIN):
            return True
        else:
            return False

if __name__ == '__main__':
    ms = MagneticSwitch(22, True) # BCM 25
    try:
        while 1:
            print(ms.testSwitch())

    except KeyboardInterrupt:
        print("Testing complete.")


