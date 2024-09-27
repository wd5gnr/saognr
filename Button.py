from machine import Timer
from rp2 import bootsel_button

# Generic button that measures how long the button was pushed and if it 
# is currently pushed. The calling program has to zero the count 
# this is the base class and doesn't actually work
class Button:
    def __init__(self,scantime=10):
        self.btn_count=0
        self.btn_off=0
        self.timer=Timer(-1)
        self.scantime=scantime
        
    def get_btn(self):
        return 0   # you should override this
    
    def timer_callback(self,t):
        if self.get_btn():
            self.btn_count=self.btn_count+1   # user sets to zero
            self.btn_off=0
        else:
            self.btn_off=1
        
    def start(self):
        self.btn_count=0
        self.btn_off=0
        self.timer.init(period=self.scantime, mode=Timer.PERIODIC, callback=lambda t: self.timer_callback(t))



    def stop(self):
        self.timer.deinit()


# This is a real button that uses the Pico Bootsel button
# Note this has some bad effects since you have to disconnect
# the flash to get it to read, but that's not so bad
class BSButton(Button):
    def get_btn(self):
        return bootsel_button()
    
        
