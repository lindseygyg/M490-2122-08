import time
import RPi.GPIO as GPIO

class BallTiltSwitch:
    def __init__(self, pin, test=False):
        self.tiltPIN = pin
        if test is not False:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.tiltPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def testSwitch(self):
        """
        Test function: checks output of ball tilt switch
        """
        count = 0
        print("Testing tilt switch for 10 seconds:")
        while count < 10:
            print(GPIO.input(self.tiltPIN))
            count += 1
            time.sleep(1)

    def checkSwitch(self):
        """
        Returns output of ball tilt switch sensor which represents head tilt
        :return: True (boolean) if ball tilt switch is tilted
        """
        # Returns true if ball tilt switch is tilted
        # Flat returns 1; tilted returns 0
        if not GPIO.input(self.tiltPIN):
            return True
        else:
            return False

if __name__ == '__main__':
    ts = BallTiltSwitch(26, test=True)
    print("Testing ball tilt switch:")
    try:
        while 1:
            ts.testSwitch()
            time.sleep(1)

    except KeyboardInterrupt:
        print("Testing complete.")
