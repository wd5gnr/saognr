import time
import neopixel
from machine import Pin, PWM, Timer
from Morse import Morse
from rp2 import bootsel_button

from config import config

# This class knows how to drive LEDs and the speaker
class MorseCode(Morse):

    def __init__(self,wpm=config.DEF_WPM, cspace_xtra=config.DEF_CSPACE_XTRA, wspace_xtra=config.DEF_WSPACE_XTRA, 
                 cw_tone=config.DEF_CW_TONE):
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.leds=neopixel.NeoPixel(Pin.board.GP14,4)
        self.speaker=PWM(Pin(Pin.board.GP0))
        self.cw_tone=cw_tone
        self.led_active=True   # we need to turn off the LEDs when sending code for menus

        
# handle the LED and buzzer for morse elements
    def setup(self,element):  
        if element==Morse.STOP:  # all stop
            self.speaker.duty_u16(0)
            if self.led_active:
                self.leds[0]=(0,0,0)
                self.leds[1]=(0,0,0)
                self.leds[2]=(0,0,0)
                self.leds[3]=(0,0,0)
                self.leds.write()
        else:
            if self.cw_tone!=0:
                self.speaker.freq(self.cw_tone)
                self.speaker.duty_u16(1000)    # make a tone
            if self.led_active:            # if leds on, manage them, too
                self.leds[0]=(128,128,128)
                self.leds[3]=(128,128,128)
                if element==Morse.DOT:
                    self.leds[1]=(128,0,0)
                    self.leds[2]=(128,0,0)
                else:
                    self.leds[1]=(0,128,0)
                    self.leds[2]=(0,128,0)
                self.leds.write()

