import time
from BallTiltSwitch import BallTiltSwitch
from MagneticSwitch import MagneticSwitch
from TouchSwitch import TouchSwitch
from PressureSwitch import PressureSwitch
from mpu6050 import mpu6050

class RunCPR:

    def __init__(self):
        self.touchSensor = TouchSwitch()
        self.tiltSensor = BallTiltSwitch(16)
        self.pressureSensor = PressureSwitch()
        self.accelerometer = mpu6050(0x68)
        self.magneticSensor = MagneticSwitch(18)

    def checkPulse(self):
        # Check pulse - verify 10 seconds (acceptable range: 9-12 seconds)
        pulseTime = self.touchSensor.checkTouch() # 25s max time to complete this
        if 9 < pulseTime < 12:
            return True
        else:
            return False

    def checkHeadTilt(self):
        return self.tiltSensor.checkSwitch()

    def checkBreathing(self):
        return self.pressureSensor.checkSwitch() # 10 second time limit for each breath

    def compressions(self):
        # Verify compressions: number=30, frequency, depth
        # prints # compressions, frequency, correct depth
        return

    def checkAEDPadPlacement(self):
        return self.magneticSensor.checkSwitch()

    def EasyCPR(self, rounds=2):
        print("CHECK SURROUNDING (look for open wires, electricity, flood, animals, etc)")
        print("IF SOMEONE IS NEXT TO YOU, POINT TO THEM AND TELL THEM TO CALL 911. SAY: \"YOU CALL 911\"")
        print("IF SOMEONE ELSE IS NEXT TO YOU, POINT TO THEM AND TELL THEM TO GET YOU AN AED. SAY: \"YOU GET ME AN AED\"")
        print("Once the surrounding has been deemed safe, go the person and shake them by the shoulders to make sure they are not sleeping.")

        print("Now, check the pulse.")
        # TWO OPTIONS: PUT INPUTS FOR EASY/MEDIUM/HARD IN THE INPUT FOR THE FUNCTION ITSELF OR DO IT ALL HERE
        print("Put two fingers on the top side of the neck - left or right - and feel for the pulse.")

        pulseChecked = self.checkPulse()
        while not pulseChecked:
            pulseChecked = self.checkPulse()

        print("Assume there is no pulse. Since the person is not breathing and has no pulse, we will begin CPR.")

        round = 1
        while round <= rounds:
            if round == rounds:
                print("Now let us begin round 2 of CPR.")

            print("For compressions, it helps to count out loud.")
            print("Place your hands one on top of the other and interlace your fingers. Place them on the sternum (middle of chest).")
            print("Ensure your arms remain straight and locked - begin compressions!")
            self.compressions()

            print("Now that the compressions are done, we'll move onto the breathing aspect.")
            print("Put yourself behind the head, put your hands and fingers under the head and gently tilt it to open the airways.")

            headTilted = self.checkHeadTilt()
            while not headTilted:
                headTilted = self.checkHeadTilt()

            print("Place yourself beside the head now.")
            print("Open the mouth slightly and breathe twice into the manikin's mouth.")

            breathingChecked = self.checkBreathing()
            while not breathingChecked():
                breathingChecked = self.checkBreathing()

            round += 1

        print("Someone has arrived with an AED!")
        print("Open the AED kid and place the pads on the manikin.")

        placedAED = self.checkAEDPadPlacement()
        while not placedAED:
            placedAED = self.checkAEDPadPlacement()

        print("Follow the instructions of the AED until EMS arrives and takes over.")

    def DifficultCPR(self, rounds=2):
        print("Begin CPR.")

        self.checkPulse()

        round = 1
        while round <= rounds:
            self.compressions()
            self.checkHeadTilt()
            self.checkBreathing()

            round += 1

        self.checkAEDPadPlacement()
