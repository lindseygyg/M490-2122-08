import time
import RPi.GPIO as GPIO


class BallTiltSwitch:
    def __init__(self, pin, test=False):
        self.tiltPIN = pin
        if test:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.tiltPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def testSwitch(self):
        """
        Test function: checks output of ball tilt switch
        """
        count = 0
        print("Testing tilt switch for 10 seconds:")
        while count < 10:
            print(not GPIO.input(self.tiltPIN))
            count += 1
            time.sleep(1)
        print("Finished testSwitch function.")

    def checkSwitch(self, t=5):
        """
        Returns output of ball tilt switch sensor which represents head tilt
        :return: True (boolean) if ball tilt switch is tilted
        """
        count = 0
        while count < t:
            if not GPIO.input(self.tiltPIN):
                return True
            count += 1
            time.sleep(1)

        return False

    def switchPosition(self):
        return not GPIO.input(self.tiltPIN)


if __name__ == '__main__':
    bts = BallTiltSwitch(18, test=True) # BCM 24
    
    print("Testing ball tilt switch:")
    try:
        while 1:
            print(bts.checkSwitch())
            time.sleep(1)

    except KeyboardInterrupt:
        print("Testing complete.")
