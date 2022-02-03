import time
import RPi.GPIO as GPIO
from BallTiltSwitch import BallTiltSwitch
from MagneticSwitch import MagneticSwitch
from TouchSwitch import TouchSwitch
from PressureSwitch import PressureSwitch
#from mpu6050 import mpu6050
from Accelerometer import Accelerometer

class RunCPR:

    def __init__(self):
        #GPIO.cleanup()
        #GPIO.setmode(GPIO.BOARD) # does not let us change this? 
        #print(GPIO.getmode()) # output: 11 so it is BCM (broadcom)
        self.tiltSensor = BallTiltSwitch(24)    # board: 18
        self.magneticSensor = MagneticSwitch(25)    # board: 20
        self.touchSensor = TouchSwitch(pin1=22, pin2=23)    # board: 15, 16 (left and right)
        
        self.pressureSensor = PressureSwitch()
        self.accelerometer = Accelerometer(0x68) 

    def checkPulse(self, level):
        if level < 4:
            print("Now, check the pulse.")
            print("With your index finger and your middle finger together, place them gently on the carotid artery of the neck.")
            print("Either side is acceptable.")
            print("Feel for the pulse for 10 seconds.")

        # Check pulse - verify 10 seconds (acceptable range: 9-12 seconds)
        pulseTime = self.touchSensor.checkTouch()   # 25s max time (default) to complete this
        if 8.75 < pulseTime < 12:
            return True
        else:
            return False

    def checkHeadTilt(self, level):
        if level < 4:
            print("When you are beside the head, gently tilt the head towards the back.")
            print("This opens the airway for the rescue breaths.")

        return self.tiltSensor.checkSwitch()

    def checkBreathing(self, level):
        if level < 4:
            print("Place yourself beside the head now.")
            print("Open the mouth slightly: place your fingers just below the ear, behind the jaw."
            print("Breathe twice into the manikin's mouth making sure the chest rises.")

        return self.pressureSensor.checkSwitch()    # 10 second time limit for each breath

    def beginCompressions(self, level):
        if level < 4:
            print("Now, it's time for compressions - it helps to count out loud.")
            print("Place your hands one on top of the other and interlace your fingers. Place them on the sternum (middle of chest).")
            print("Ensure your arms remain straight and locked - begin compressions!")
            print("The arms should remain straight, so make sure the movement comes from the body.")

        # Verify compressions: number=30, frequency, depth
        # prints # compressions, frequency, correct depth
        return

    def checkAEDPadPlacement(self, level):
        if level < 4:
            print("Open the AED kid and place the pads on the manikin.")

        return self.magneticSensor.checkSwitch()

    def performCPR(self, inputLevel, rounds=2):
        """
        Everything printed here must be shown as part of the CPR process (for all levels).
        :param inputLevel: level at which we are performing (integer)
        :param rounds: number of rounds of CPR
        """
        print("REMEMBER TO CHECK SURROUNDINGS (look for open wires, electricity, flood, animals, etc)")
        print("IF SOMEONE IS NEXT TO YOU, POINT TO THEM AND TELL THEM TO CALL 911. SAY: \"YOU CALL 911\"")
        print("IF SOMEONE ELSE IS NEXT TO YOU, POINT TO THEM AND TELL THEM TO GET YOU AN AED. SAY: \"YOU GET ME AN AED\"")
        print("Once the surrounding has been deemed safe, go the person and shake them by the shoulders to make sure they are not sleeping.")

        pulseChecked = self.checkPulse(level=inputLevel)
        while not pulseChecked:
            pulseChecked = self.checkPulse()

        if inputLevel < 4:
            print("Assume there is no pulse. Since the person is not breathing and has no pulse, we will begin CPR.")
        else:
            print("Assume the person is not breathing and does not have a pulse.")

        round = 1
        while round <= rounds:
            if round == rounds:
                if inputLevel < 4:
                    print("Now let us begin round 2 of CPR.")

            self.beginCompressions(inputLevel)

            if inputLevel < 4:
                print("Now that the compressions are done, we'll move onto the breathing aspect.")

            headTilted = self.checkHeadTilt(inputLevel)
            while not headTilted:
                headTilted = self.checkHeadTilt(inputLevel)

            breathingChecked = self.checkBreathing(inputLevel)
            while not breathingChecked:
                breathingChecked = self.checkBreathing(inputLevel)

            round += 1

        print("Someone has arrived with an AED!")

        placedAED = self.checkAEDPadPlacement(inputLevel)
        while not placedAED:
            placedAED = self.checkAEDPadPlacement(inputLevel)

        print("Follow the instructions of the AED until EMS arrives and takes over.")

    def output_string(self, statement):
        # html = r'<div class="instruction">'+statement+r'</div>'
        # html = r'<div class="feedback">'+statement+r'</div>'
        # return HttpResponse(html)
        return

    def test_trial(self):
        print("Begin Testing:")
        print("Testing Pulse (TOUCH SENSOR):")
        self.touchSensor.testSwitch()
        time.sleep(2)
        print("Testing Head Tilt (BALL TILT SWITCH):")
        self.tiltSensor.testSwitch()
        time.sleep(2)
        print("Testing Breathing (PRESSURE SENSOR):")
        self.pressureSensor.testSwitch()
        time.sleep(2)
        # print("Testing Compressions (ACCELEROMETER):")
        # self.accelerometer.testSwitch()
        # time.sleep(2)
        print("Testing AED Pad Placement (MAGNETIC SWITCH):")
        self.magneticSensor.testSwitch()
        print("Testing complete.")

if __name__ == '__main__':
    # CONNECT THROUGH LAN CABLE - WHEN NO INTERNET

    cpr_test = RunCPR()

    cpr_test.test_trial()


