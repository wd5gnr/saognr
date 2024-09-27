import time
import neopixel
from machine import Pin, PWM, Timer
from Morse import Morse
from rp2 import bootsel_button
from config import Config  

# This class extends the base Morse class to include control of LEDs and a speaker (buzzer).
class MorseCode(Morse):

    def __init__(self, wpm=Config.DEFAULT_WPM, cspace_xtra=Config.DEFAULT_EXTRA_CHAR_SPACE, 
                 wspace_xtra=Config.DEFAULT_EXTRA_WORD_SPACE, cw_tone=Config.DEFAULT_CW_TONE):
        """
        Initialize the MorseCode class.
        - wpm: Words per minute for Morse code.
        - cspace_xtra: Extra space between characters.
        - wspace_xtra: Extra space between words.
        - cw_tone: Frequency of the CW tone in Hz.
        """
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.leds = neopixel.NeoPixel(Pin(Config.LED4_PIN), 4)  # Configure a NeoPixel with 4 LEDs on GP14
        self.speaker = PWM(Pin(Pin(Config.SPEAKER_PIN)))  # Configure PWM on GP0 for the speaker
        self.cw_tone = cw_tone  # Set the CW tone frequency
        self.led_active = True  # Flag to indicate if the LEDs should be active (used for menus)

    # Handle the LEDs and buzzer (speaker) for Morse code elements
    def setup(self, element):
        """
        Setup the LED and speaker for the current Morse element.
        - element: Morse.STOP, Morse.DOT, or Morse.DASH.
        """
        if element == Morse.STOP:  # Stop all outputs (both LED and sound)
            self.speaker.duty_u16(0)  # Stop the speaker
            if self.led_active:
                # Turn off all the LEDs
                self.leds.fill((0, 0, 0))  # Set all 4 LEDs to off (black)
                self.leds.write()  # Apply the changes to the LEDs
        else:
            # Handle the sound output (CW tone)
            if self.cw_tone != 0:  # Only play the tone if cw_tone is set
                self.speaker.freq(self.cw_tone)  # Set the frequency for the speaker
                self.speaker.duty_u16(1000)  # Start the speaker (low duty cycle for quieter tone)

            # Handle the LED output
            if self.led_active:
                # Set base color for the outer LEDs
                self.leds[3]=self.leds[0] = (128, 128, 128)  # Gray for LED 0/3

                # Set colors for the inner LEDs based on whether it's a dot or dash
                if element == Morse.DOT:
                    self.leds[2]=self.leds[1] = (128, 0, 0)  # Red for DOT on LED 1/2
                else:  # Dash case
                    self.leds[2]=self.leds[1] = (0, 128, 0)  # Green for DASH on LED 1/2
                self.leds.write()  # Apply the changes to the LEDs
