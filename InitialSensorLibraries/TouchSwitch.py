import time
import RPi.GPIO as GPIO


class TouchSwitch:
    def __init__(self, pin1, pin2=None, test=False):
        self.padPIN = pin1
        self.padPIN2 = pin2
        if test is not False:
            GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.padPIN, GPIO.IN)
        if self.padPIN2 is not None:
            GPIO.setup(self.padPIN2, GPIO.IN)

    def testSwitch(self):
        count = 0
        print("Testing touch switch for 10 seconds:")
        print(GPIO.getmode())
        
        while count < 10:
            if GPIO.input(self.padPIN) or GPIO.input(self.padPIN2):
                print("True")
            else:
                print("False")
            count += 1
            time.sleep(1)
        print("Finished testSwitch function.")

    def checkTouch1(self, t=25):
        """
        Time the user checks pulse (contacts touch sensor)
        :param t: time limit for checking pulse
        :return: time of checking pulse (contact with touch sensor)
        """
        already_pressed = False
        start = None
        countdown = 0
        
        # max time in this portion: input of 25 seconds
        while countdown < t:

            count = 0
            ch = False  # initialize check variable
            start1 = None  # start time of NOT touching
            
            if GPIO.input(self.padPIN) and not already_pressed:
                #print("start touch sensed")
                start = time.time()     # start time of touching
                already_pressed = True  # registers as having started counting for pulse
            
            while not GPIO.input(self.padPIN) and count < 1:
                # check time of "flicker" for when not touching
                if not ch:
                    start1 = time.time()   # start time of NOT touching
                        #print("start1")
                    ch = True   # change check variable to true so it does not restart
                count += 0.25
                time.sleep(.25)

            if ch:
                    #print("ch and end1")
                end1 = time.time()

                # makes sure all are doubles and time of NOT touching > 0.8 s -> finished checking pulse
            if ch and start1 is not None and start is not None and (end1-start1 > .8): # and (start1-start) < 7:
                    # TODO: if time remaining > 10 s, ignore this and restart timing of pulse check
                timeCheck = t - countdown
                    #print("time left: ", timeCheck)
                if timeCheck > 10:
                        #print("current pulse time:", start1 - start)
                        #print("check pulse again for 10 s")
                    ch = False
                    already_pressed = False
                else:
                    timeTaken = start1 - start
                    #("st1 - st returning")
                    return timeTaken
            countdown += 1
            time.sleep(1)

        end = time.time() # actual end time if time limit exceeds and continuously touching
        #print("et - st") #nexceeded time to check pulse
        timeTaken = end - start
        # print(timeTaken)
        return timeTaken

    def checkTouch2(self, t=25):
        """
        Time the user checks pulse (contacts touch sensor)
        :param t: time limit for checking pulse
        :return: time of checking pulse (contact with touch sensor)
        """
        already_pressed = False
        start = None
        countdown = 0

        # max time in this portion: 25 seconds
        while countdown < t:

            count = 0
            ch = False  # initialize check variable
            start1 = None  # start time of NOT touching

            if (GPIO.input(self.padPIN) or GPIO.input(self.padPIN2)) and not already_pressed:
                start = time.time()     # start time of touching
                already_pressed = True  # registers as having started counting for pulse

            while (not GPIO.input(self.padPIN) and not GPIO.input(self.padPIN2)) and count < 1:
                # check time of "flicker" for when not touching
                if not ch:
                    start1 = time.time()   # start time of NOT touching
                    ch = True   # change check variable to true so it does not restart
                count += 0.25
                time.sleep(.25)

            if ch:
                end1 = time.time()

            # makes sure all are doubles and time of NOT touching > 0.8 s -> finished checking pulse
            if ch and start1 is not None and start is not None and (end1-start1 > .8):
                timeCheck = t - countdown
                if timeCheck > 10:
                    already_pressed = False
                else:
                    timeTaken = start1 - start
                    return timeTaken
            countdown += 1
            time.sleep(1)

        end = time.time()   # actual end time if time limit exceeded and continuously touching
        timeTaken = end - start
        return timeTaken


    def checkTouch2(self, t=25):
        """
        Time the user checks pulse (contacts touch sensor)
        :param t: time limit for checking pulse
        :return: time of checking pulse (contact with touch sensor)
        """
        already_pressed = False
        start = None
        countdown = 0
        
        # max time in this portion: 25 seconds
        while countdown < t:

            count = 0
            ch = False  # initialize check variable
            start1 = None  # start time of NOT touching
            
            if (GPIO.input(self.padPIN) or GPIO.input(self.padPIN2)) and not already_pressed:
                #print("start touch sensed")
                start = time.time()     # start time of touching
                already_pressed = True  # registers as having started counting for pulse
            
            while (not GPIO.input(self.padPIN) and not GPIO.input(self.padPIN2)) and count < 1:
                # check time of "flicker" for when not touching
                if not ch:
                    start1 = time.time()   # start time of NOT touching
                    #print("start1")
                    ch = True   # change check variable to true so it does not restart
                count += 0.25
                time.sleep(.25)

            if ch:
                #print("ch and end1")
                end1 = time.time()

            # makes sure all are doubles and time of NOT touching > 0.8 s -> finished checking pulse
            if ch and start1 is not None and start is not None and (end1-start1 > .8): # and (start1-start) < 7:
                # if time remaining > 10 s, ignore this and restart timing of pulse check
                timeCheck = t - countdown
                #print("time left: ", timeCheck)
                if timeCheck > 10:
                    #print("current pulse time:", start1 - start)
                    #print("check pulse again for 10 s")
                    ch = False
                    already_pressed = False
                else:
                    timeTaken = start1 - start
                    #("st1 - st returning")
                    return timeTaken
            countdown += 1
            time.sleep(1)

        end = time.time() # actual end time if time limit exceeds and continuously touching
        #print("et - st") #nexceeded time to check pulse
        timeTaken = end - start
        # print(timeTaken)
        return timeTaken

if __name__ == '__main__':
    print("Testing capacitive touch sensor")
    #ts = TouchSwitch(16, test=True) # BCM 23
    ts = TouchSwitch(15, 16, test=True)    # BCM 22, 23
    
    ts.testSwitch()
    """
    #ts.testSwitch()
    pulseTime = ts.checkTouch2(t=20)
    #pulseTime = ts.checkTouch2(t=20)
    
    if pulseTime > 9 and pulseTime < 12:
        print('It worked:', pulseTime)
    else:
        print("It did not work", pulseTime)
    """

