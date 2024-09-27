from machine import Timer
from rp2 import bootsel_button

DEF_SCAN_TIME=10  # button scan time in milliseconds (default)

# Generic button that measures how long the button was pushed and if it 
# is currently pushed. The calling program has to zero the count 
# this is the base class and doesn't actually work (see BSButton, below)
class Button:
    def __init__(self,scantime=DEF_SCAN_TIME):   # by default, scan every 10 ms
        self.btn_count=0   # counts how long button has been pressed (main program resets)
        self.btn_off=0     # 1 when button was on but now off. So 0, 0 means nothing 0, 1 means already read
        self.timer=Timer(-1)   # 8, 0 (example) means button is still down and 12,1 means button was held down for 12 counts but is up now
        self.scantime=scantime

   # subclass defines this to tell us current state of button whatever that is     
    def get_btn(self):
        return 0   # you should override this
    
    def timer_callback(self,t):
        if self.get_btn():
            self.btn_count=self.btn_count+1   # user sets to zero
            self.btn_off=0
        else:
            self.btn_off=1

    # Button won't work until you start it    
    def start(self):
        self.btn_count=0
        self.btn_off=0
        self.timer.init(period=self.scantime, mode=Timer.PERIODIC, callback=lambda t: self.timer_callback(t))


    # Stop the button
    def stop(self):
        self.timer.deinit()


# This is a real button that uses the Pico Bootsel button
# Note this has some bad effects since you have to disconnect
# the flash to get it to read, but that's not so bad
class BSButton(Button):
    def get_btn(self):
        return bootsel_button()
    
        
