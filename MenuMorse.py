import time
from MorseCode import MorseCode
from Button import BSButton

# This is like MorseCode but watches the bootsel button
# Override button_push for a short push
# Override button_long for a long push
# If you hold for a long time (15s) the LEDs turn dim red
# Then when you release it calls button_hold
class MenuMorse(MorseCode):
    def __init__(self,wpm=13, cspace_xtra=1, wspace_xtra=1, thresh1=10, thresh2=150):
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.menu_lock=False
        self.thresh1=thresh1
        self.thresh2=thresh2
        self.button=BSButton()
        
    def button_push(self):
        print("Push")
        
    def button_long(self):
        print("Long")
        
    def button_hold(self):
        print("Hold")
        
    def basemenu(self,count):
        if self.menu_lock:
            return
        if count<self.thresh1:
            self.menu_lock=True
            self.button_push()
            self.menu_lock=False
        elif count<self.thresh2:
            self.menu_lock=True
            self.button_long()
            self.menu_lock=False
        else:
            self.menu_lock=True
            self.leds[0]=(10,0,0)
            self.leds[1]=(10,0,0)
            self.leds[2]=(10,0,0)
            self.leds[3]=(10,0,0)
            self.leds.write()
            while get_btn()==1:
               time.sleep(0.01)
            self.button_hold()
            self.menu_lock=False
 
    def proc_input(self):
        super().proc_input()
        if self.button.btn_count!=0 and self.button.btn_off!=0:
            self.basemenu(int(self.button.btn_count/10))
            self.button.btn_count=0
                               

