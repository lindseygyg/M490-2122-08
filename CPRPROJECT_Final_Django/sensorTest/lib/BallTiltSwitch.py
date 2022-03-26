import time
import RPi.GPIO as GPIO

class BallTiltSwitch:
    def __init__(self, pin):
        self.tiltPIN = pin
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.tiltPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def testSwitch(self):
        """
        Test function: checks output of ball tilt switch
        """
        arr = []
        count = 0
        print("Testing tilt switch for 10 seconds:")
        while count < 10:
            print(GPIO.input(self.tiltPIN))
            arr.append(GPIO.input(self.tiltPIN))
            count += 1
            time.sleep(1)
        print (arr)
        return arr

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
    ts = BallTiltSwitch(26)
    print("Testing ball tilt switch:")
    
    ts.testSwitch()
    time.sleep(1)


