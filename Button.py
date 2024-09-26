from machine import Timer
from rp2 import bootsel_button

class Button:
    def __init__(self):
        self.btn_count=0
        self.btn_off=0
        self.timer=Timer(-1)
        self.timer.init(period=10, mode=Timer.PERIODIC, callback=lambda t: self.timer_callback(t))
        
    def get_btn(self):
        return 0   # you should override this
    
    def timer_callback(self,t):
        if self.get_btn():
            self.btn_count=self.btn_count+1   # user sets to zero
            self.btn_off=0
        else:
            self.btn_off=1
        
    def stop(self):
        self.timer.deinit()
        
class BSButton(Button):
    def __init__(self):
        super().__init__()
    
    def get_btn(self):
        return bootsel_button()
    
        
