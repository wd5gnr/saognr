import time
from MorseCode import MorseCode
from Button import BSButton
from config import config

# This is like MorseCode but watches the bootsel button
# Override button_push for a short push
# Override button_long for a long push
# If you hold for a long time (15s) the LEDs turn dim red
# Then when you release it calls button_hold
class MenuMorse(MorseCode):
    def __init__(self,wpm=config.DEF_WPM, cspace_xtra=config.DEF_CSPACE_XTRA, wspace_xtra=config.DEF_WSPACE_XTRA, 
                 thresh1=config.BTN_THRESH, thresh2=0):   # super long hold is not used so thresh2==0
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.menu_lock=False   # allow menu processing
        self.thresh1=thresh1
        self.thresh2=thresh2
        self.button=BSButton()   # create and start button
        self.button.start()
        
    def button_push(self):   # short press
        print("Push")
        
    def button_long(self):   # long press 
        print("Long")
        
    def button_hold(self):  # button hold down isn't a great idea (very long press)
        print("Hold")

  # process button lengths and call the right place for subclasses      
    def basemenu(self,count):
        if self.menu_lock:    # menu disabled
            return
        if count<self.thresh1:   # sort out how long the button was downn
            self.menu_lock=True
            self.button_push()
            self.menu_lock=False
        elif self.thresh2==0 or count<self.thresh2:
            self.menu_lock=True
            self.button_long()
            self.menu_lock=False
        else:
            self.menu_lock=True
            self.leds.write()
            while self.button.get_btn()==1:   # since super long presses don't wait for release, we should wait for one here
               time.sleep(0.01)
            self.button_hold()
            self.menu_lock=False
 
 # Base class calls us periodically so we can scan for inputs
 # the button works where btn_count is how long the button has 
 # been pressed (so far). btn_off is False if the button is still
 # down. So, nominally, you want to wait for btn_off is 1
 # and btn_count is non-zero to read a button then reset btn_count
 # yourself
    def proc_input(self):
        super().proc_input()
        if self.button.btn_count!=0 and self.button.btn_off!=0:
            self.basemenu(int(self.button.btn_count/10))
            self.button.btn_count=0
                               

