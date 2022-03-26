import time
import RPi.GPIO as GPIO
from BallTiltSwitch import BallTiltSwitch
from MagneticSwitch import MagneticSwitch
from TouchSwitch import TouchSwitch
from PressureSwitch import PressureSwitch
#from mpu6050 import mpu6050
from Accelerometer import Accelerometer
from datetime import timedelta
import multiprocessing as mp

class RunCPR:

    def __init__(self):
        #GPIO.cleanup()
        #GPIO.setmode(GPIO.BOARD) # does not let us change this? 
        #print(GPIO.getmode()) # output: 11 so it is BCM (broadcom)
        self.tiltSensor = BallTiltSwitch(24)    # board: 18
        self.magneticSensor = MagneticSwitch(25, 27)    # board: 20, 13
        self.touchSensor = TouchSwitch(pin1=22, pin2=23)    # board: 15, 16 (left and right)
        
        self.pressureSensor = PressureSwitch()
        self.accelerometer = Accelerometer(0x68) 

    def checkPulse(self, level):
        if level <= 4:
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
        if level >= 3 and level <= 4: 
            print("When you are beside the head, gently tilt the head towards the back.")
            print("This opens the airway for the rescue breaths.")

        return self.tiltSensor.checkSwitch()

    def checkBreathing(self, level):
        if level >= 3 and level <= 4:
            print("Place yourself beside the head now.")
            print("Open the mouth slightly: place your fingers just below the ear, behind the jaw.")
            print("Breathe twice into the manikin's mouth making sure the chest rises.")

        return self.pressureSensor.checkSwitch()    # 10 second time limit for each breath

    def beginCompressions(self, level):
        if level <= 4:
            print("Now, it's time for compressions - it helps to count out loud.")
            print("Place your hands one on top of the other and interlace your fingers. Place them on the sternum (middle of chest).")
            print("Ensure your arms remain straight and locked - begin compressions!")
            print("The arms should remain straight, so make sure the movement comes from the body.")

        # Verify compressions: number=30, frequency, depth
        # prints # compressions, frequency, correct depth
        return

    def checkAEDPadPlacement(self, level):
        if level == 4:
            print("Open the AED kid and place the pads on the manikin.")

        return self.magneticSensor.checkSwitches()  # default time limit is 30 seconds

    def start_CPR(self, inputLevel, rounds, component):
        """
        Selection of levels or CPR components
        :param inputLevel: level at which we are performing (integer)
        :param rounds: number of rounds of CPR
        :param component: test individual CPR components (string)
        """
        str_check = component.isspace() # checks for whitespace
        if str_check:
            component = ""

        if inputLevel is not None:
            level = int(inputLevel)
        else:
            level = 0

        if rounds is None and not component:
            rounds = 2
        
        if component == 'Pulse':
            print("Check for Pulse.")
            self.touchSensor.testSwitch()
            print('Pulse Test finished.')
            return
        elif component == 'Head':
            print("Check for Head Tilt.")
            self.tiltSensor.testSwitch()
            print('Head Tilt Test finished.')
            return
        elif component == 'Chest': 
            #TODO include the option to do freq, depth or both
            print("Check Chest Compressions.")
            #TODO add chest compression function
            print('Chest Compression Test finished.')
            return
        elif component == "Breath":
            print("Check for Rescue Breaths.")
            self.pressureSensor.testSwitch()
            print("Rescue Breath Test finished.")
            return
        elif component == "AED":
            print("Check AED Pads Placement")
            self.magneticSensor.testSwitch()
            print("AED Placement Test finished.")
            return

        if level <= 4 and level > 0:
            # Starts CPR Course
            print(f'CPR Level {level} has been selected.')
            print('CPR run beginning in:')
            for i in range(3):
                print(f'{3-i}')
                time.sleep(1)
            print('Start')
            start_time = time.time()
            self.performCPR(level,rounds)
            end_time = time.time()
            duration = start_time - end_time
            print(f'Duration: {str(timedelta(seconds=duration))}')

        elif level == 6:
            full_time = int(rounds) * 3 * 60    # seconds
            # Starts CPR Course
            print(f'CPR Level {level} has been selected.')
            print('Begin CPR in...')
            for i in range(3):
                print(f'{3-i}')
                time.sleep(1)
            print('START CPR')
            p = mp.Process(target=self.perform_CPR,args=(level,rounds))
            p.start()
            start_time = time.time()
            p.join(full_time)
            if p.is_alive():
                print('Timer ran out, nice try. Do better the next time! (^.^)/')
                p.terminate()
            else:
                print('Great job, you finished before the timer')
            end_time = time.time()
            duration = end_time-start_time
            print(f'Duration: {str(timedelta(seconds=duration))}')

    def perform_CPR(self, inputLevel, rounds):
        """
        Runs different levels depending on the inputlevel and number of rounds.
        :param inputLevel: level at which we are performing (integer)
        :param rounds: number of rounds of CPR
        """
        if inputLevel <= 4:
            print("REMEMBER TO CHECK SURROUNDINGS (look for open wires, electricity, flood, animals, etc)")

            print("Once the surrounding has been deemed safe, go the person.")
            print("Shake them by the shoulders to make sure they are not sleeping. "
                  "Check if they are breathing. Check if they are injured.")

        # Pulse 
        pulseChecked = self.checkPulse(level=inputLevel)
        while not pulseChecked:
            pulseChecked = self.checkPulse()
        if pulseChecked:    # ? should we include this only for instructed levels or all levels?
            print('Pulse check has been completed')

        if inputLevel <= 4:
            print("Assume there is no pulse. Since the person is not breathing and has no pulse, we will begin CPR.")
            print("IF SOMEONE IS NEXT TO YOU, POINT TO THEM AND TELL THEM TO CALL 911. SAY: \"YOU CALL 911\"")
            print("IF SOMEONE ELSE IS NEXT TO YOU, POINT TO THEM AND TELL THEM TO GET YOU AN AED. SAY: \"YOU GET ME AN AED\"")
        
        if inputLevel > 1:
            round = 1
            start_round = False
            while round <= rounds:
                if start_round:
                    print(f"Now let us begin round {round} of CPR.")

                # Chest Compression
                self.beginCompressions(inputLevel)
                # TODO include frequency and depth/split for both levels 2 and 3
                print("The chest compressions have been completed.")

                if inputLevel >= 3 and inputLevel <= 4:
                    print('Now we will perform rescue breaths.')
                
                if inputLevel >= 3:
                    headTilted = self.checkHeadTilt(inputLevel)
                    while not headTilted:
                        headTilted = self.checkHeadTilt(inputLevel)
                    if headTilted:
                        print('Head tilt has been completed.')

                    # TODO: WHILE BREATHING: VERIFY SELF.TILTSENSOR.CHECKPOSITION() SINCE PERSON NEEDS TO HOLD HEAD TILT
                    breathingChecked = self.checkBreathing(inputLevel)
                    while not breathingChecked:
                        breathingChecked = self.checkBreathing(inputLevel)
                    if breathingChecked:
                        print('Rescue breaths have been completed.')
                
                print(f'Round {round} completed.')
                round += 1

                if not start_round:
                    start_round = True
           
        if inputLevel >= 4:
            if inputLevel == 4:
                print("Someone has arrived with an AED!")

            placedAED = self.checkAEDPadPlacement(inputLevel)
            while not placedAED:
                placedAED = self.checkAEDPadPlacement(inputLevel)
            if placedAED:
                print('Placement of AED Pads are correct.')
            if inputLevel == 4:
                print("Follow the instructions of the AED until EMS arrives and takes over.")
        
        print(f'CPR Level {inputLevel} has been complete!')

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
        self.magneticSensor.testSwitches()
        print("Testing complete.")


if __name__ == '__main__':
    cpr_test = RunCPR()

    cpr_test.test_trial()


