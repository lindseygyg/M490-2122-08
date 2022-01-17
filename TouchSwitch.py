import time
import RPi.GPIO as GPIO

class TouchSwitch():
    
    def __init__(self, pin):
        self.pad_pin = pin
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.pad_pin, GPIO.IN)

    def checkTouch(self, t=25):
        already_pressed = False
        st = None
        countdown = 0
        while countdown < t: # max time in this portion: 30 seconds
            
            ch = False
            st1 = None
            count = 0
            
            if GPIO.input(self.pad_pin) and not already_pressed:
                print("touch sensed")
                st = time.time()
                already_pressed = True
            
            while not GPIO.input(self.pad_pin) and count < 1:
                if not ch:
                    st1 = time.time()
                    ch = True
                count += 0.25
                time.sleep(.25)
                
            et1 = time.time()
            
            if ch and st1 is not None and st is not None and (et1-st1 > .8):
                #print("st1 - st")
                timeTaken = st1 - st
                print(timeTaken)
                return timeTaken
            
            countdown += 1
            time.sleep(1)
                    
        et = time.time()
        #print("et - st") #exceeded time to check pulse
        timeTaken = et - st
        print(timeTaken)
        return timeTaken

if __name__ == '__main__':
    ts = TouchSwitch(16)
    pulseTime = ts.checkTouch(20)
    if pulseTime > 9 and pulseTime < 12:
        print('it worked')
    else:
        print("it didn't work")

