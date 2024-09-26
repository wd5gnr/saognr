import time
class MenuSystem:
    def __init__(self,buttons,leds=None,feedback=None,mcolor=(127,0,255)):
        self.buttons=buttons
        self.leds=leds
        self.fb=feedback
        self.mcolor=mcolor
        
    colors=[(10,0,10),(34,17,0),(255,0,0),(255,165,0),(255,255,0),(0,255,0),(0,0,255),(127,0,255),(64,64,64),(255,255,255)]
    def menu(self,value=0,max=9):
        if self.fb:
            self.fb.abort()
            self.fb.send(str(value))
        while True:
            if self.leds:
                self.leds[0]=self.mcolor   # violet means we are in menu
                self.leds[1]=self.colors[value]
                self.leds.write()
            if self.buttons.btn_count!=0 and self.buttons.btn_off!=0:     # don't wait for super long press
                if self.buttons.btn_count>100:  # should respect threshold
                    self.buttons.btn_count=0
                    if self.fb:
                        self.fb.abort()
                        self.fb.send("E")
                        time.sleep(0.2)
                    return value
                self.buttons.btn_count=0
                value=value+1
                if value>max:
                    value=0
                if self.fb:
                    self.fb.abort()
                    self.fb.send(str(value))
            time.sleep(0.05)

