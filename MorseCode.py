import time
import neopixel
from machine import Pin, PWM, Timer
from Morse import Morse
from rp2 import bootsel_button

# Read the BOOTSEL button
#def get_btn():
#    return bootsel_button()

# This class knows how to drive LEDs and the speaker
class MorseCode(Morse):

    def __init__(self,wpm=13, cspace_xtra=1, wspace_xtra=1, cw_tone=800):
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.btn_count=0
        self.btn_off=0
        self.leds=neopixel.NeoPixel(Pin.board.GP14,4)
        self.speaker=PWM(Pin(Pin.board.GP0))
        self.cw_tone=cw_tone
        self.led_active=True

        
 #   def proc_input(self):
 #
 #       if get_btn():
 #           self.btn_count=self.btn_count+1   # user sets to zero
 #           self.btn_off=0
 #       else:
 #           self.btn_off=1

    def setup(self,element):  # move to override
        if element==Morse.STOP:
            self.speaker.duty_u16(0)
            if self.led_active:
                self.leds[0]=(0,0,0)
                self.leds[1]=(0,0,0)
                self.leds[2]=(0,0,0)
                self.leds[3]=(0,0,0)
                self.leds.write()
        else:
            self.speaker.duty_u16(1000)
            self.speaker.freq(self.cw_tone)
            if self.led_active:
                self.leds[0]=(128,128,128)
                self.leds[3]=(128,128,128)
                if element==Morse.DOT:
                    self.leds[1]=(128,0,0)
                    self.leds[2]=(128,0,0)
                else:
                    self.leds[1]=(0,128,0)
                    self.leds[2]=(0,128,0)
                self.leds.write()

