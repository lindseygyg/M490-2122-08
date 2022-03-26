import time
import RPi.GPIO as GPIO

class MagneticSwitch:
    def __init__(self, pin1, pin2=None):
        self.magPIN = pin1
        self.magPIN2 = pin2
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.magPIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.magPIN2, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

    def testSwitch(self):
        count = 0
        print("Testing magnetic contact for 10 seconds:")
        while count < 10:
            print(GPIO.input(self.magPIN))
            count += 1
            time.sleep(1)
        print("Finished testSwitch function.")

    def testSwitches(self):
        count = 0
        arr = []
        print("Testing magnetic contact for 10 seconds:")
        while count < 10:
            strng = "first pin:" + str(GPIO.input(self.magPIN)) + " & second pin:" + str(GPIO.input(self.magPIN2))
            arr.append(strng)
            count += 1
            time.sleep(1)
        print("Finished testSwitches function.")
        return arr

    def checkSwitch(self, t=30):
        """
        Use this if only one reed switch is connected
        :return:
        """
        count = 0
        while count < t:
            if GPIO.input(self.magPIN):
                return True
            count += 1
            time.sleep(1)
        return False

    def checkSwitches(self, t=30):
        """
        Use this if BOTH switches are connected
        :return: Returns true if magnets have been activated
        """
        count = 0
        while count < t:
            if GPIO.input(self.magPIN) and GPIO.input(self.magPIN2):
                return True
            count += 1
            time.sleep(1)
        return False

if __name__ == '__main__':
    ms = MagneticSwitch(17, 18)  
            #print(ms.testSwitch())
    print(ms.checkSwitches())

    
     






