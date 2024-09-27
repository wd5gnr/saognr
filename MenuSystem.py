import time

# handle a menu... 
# buttons is the button object to use
# leds are where to control the leds
# feedback is optional and is the Morse sending class to send feedback (digits)
# mcolor is the color of the first LED initially
# the idea is you can use the first LED to indicate which level of menu you are on.
# one color for level 1, another for level 2
# Or you could set one color for level 1 
# and then set the color to the command "color" for level 2

class MenuSystem:
    def __init__(self,buttons,leds=None,feedback=None,mcolor=(127,0,255)):
        self.buttons=buttons
        self.leds=leds
        self.fb=feedback
        self.mcolor=mcolor
    # resistor color codes 
    # with some concessions to reality
    # black (not really), brown (sort of), red, orange (sort of), yellow, green, blue, violet, gray (sort of), white
    colors=[(10,0,10),(34,17,0),(255,0,0),(255,165,0),(255,255,0),(0,255,0),(0,0,255),(127,0,255),(64,64,64),(255,255,255)]
    def menu(self,value=0,max=9):
        if self.fb:
            self.fb.abort()
            self.fb.send(str(value))
        while True:
            if self.leds:
                self.leds[0]=self.mcolor   # show menu level to 
                self.leds[1]=self.colors[value]  # show current value
                self.leds.write()
            if self.buttons.btn_count!=0 and self.buttons.btn_off!=0:     # don't care about super long press
                if self.buttons.btn_count>100:  # should respect threshold (long press)
                    self.buttons.btn_count=0
                    if self.fb:   # if feedback, stop beeping
                        self.fb.abort()
                    return value   # done
                self.buttons.btn_count=0  # short press
                value=value+1
                if value>max:
                    value=0
                if self.fb:
                    self.fb.abort()
                    self.fb.send(str(value))  # send this value
            time.sleep(0.05)  # fast wait

