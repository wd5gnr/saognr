import os
import gc
from machine import Pin, PWM, Timer
import neopixel

from time import sleep
from re import sub
import breathe

# Custom modules
from MenuMorse import MenuMorse
from MenuSystem import MenuSystem
from Button import BSButton
from i2ctarget import I2CMenuTarget
from config import Config

# 13 WPM is about 90ms per element (Source: http://www.kent-engineers.com/codespeed.htm)

class MorseMain(MenuMorse):
    # Config file name
    config_filename = "/saognr.cfg"  # Configuration file name

    def __init__(self, wpm=Config.DEFAULT_WPM, cspace_xtra=Config.DEFAULT_EXTRA_CHAR_SPACE, 
                 wspace_xtra=Config.DEFAULT_EXTRA_WORD_SPACE, repeat_every=Config.DEFAULT_REPEAT_DELAY * Config.TIME_SCALE):
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.countdown = 0
        self.repeat_every = repeat_every
        self.message = 0  # Start with Message0.txt unless overridden by config file
        self.do_menu = False
        self.setall()  # Set default values

        # Load settings from file, if available
        self.setall(self.load((self.message, self.repeat_every, self.wpm, self.cw_tone)))

        # I2C input configuration
        self.i2c_in = I2CMenuTarget(0, sda=Config.I2C_SDA_PIN, scl=Config.I2C_SCL_PIN, address=Config.I2C_ADDRESS)

        # Onboard NeoPixel LED configuration
        # note onboard LED is GRB not RGB
        lclr=Config.CPU_LED_BASE_COLOR
        self.breather=breathe.Breathe(neopixel.NeoPixel(Pin(Config.CPU_LED_PIN), 1),
                                      (lclr[1], lclr[0], lclr[2]),Config.CPU_LED_BREATHE_TIME)
        self.autorepeat = False  # Auto-repeat is set by a special message


    # Set all configuration values and scale them
    def setall(self, setup=(0, Config.DEFAULT_REPEAT_DELAY * Config.TIME_SCALE, Config.DEFAULT_WPM, Config.DEFAULT_CW_TONE)):
        self.message, self.repeat_every, self.wpm, self.cw_tone = setup
        self.setscale()

    # Called when button is quickly pressed
    def button_push(self):
        if self.sending():
            self.abort()
            self.countdown = self.repeat_every
        else:
            self.countdown = 0

    # Called when button is long pressed
    def button_long(self):
        self.abort()  # Stop sending the current message
        self.do_menu = True  # Trigger the menu

    # Command handlers triggered by the menu or I2C
    def cmd1(self, menu):
        # Select the message file (0-9)
        self.message = menu.menu(self.message)

    def cmd2(self, menu):
        # Select the delay from DELAY_TABLE
        choice = Config.DELAY_TABLE
        self.repeat_every = choice[menu.menu(choice.index(self.repeat_every), len(choice) - 1)] * Config.TIME_SCALE
        self.countdown = 1 if self.repeat_every == 0 else 0

    def cmd3(self, menu):
        # Select the WPM speed from WPM_TABLE
        choice = Config.WPM_TABLE
        self.wpm = choice[menu.menu(choice.index(self.wpm), len(choice) - 1)]
        self.setscale()

    def cmd4(self, menu):
        # Select the CW tone from TONE_TABLE
        choice = Config.TONE_TABLE
        self.cw_tone = choice[menu.menu(choice.index(self.cw_tone), len(choice) - 1)]

    def cmd5(self, menu):
        # Save configuration to file
        yes_no = menu.menu(0, 2)
        if yes_no == 2:  # Erase config file
            try:
                os.remove(self.config_filename)
            except OSError:  # If file doesn't exist, we don't care
                return
        if yes_no == 1:
            self.save([self.message, self.repeat_every, self.wpm, self.cw_tone])

    def cmd6(self, menu):
        # Reset to default values without saving
        yes_no = menu.menu(0, 1)
        if yes_no == 1:
            self.setall()

    def cmd7(self, menu):
        # Reset message counter
        yes_no = menu.menu(0, 1)
        if yes_no == 1:
            self.msg_ctr = 1

    def save(self, data):
        # Write configuration data to file
        with open(self.config_filename, 'w') as file:
            for item in data:
                file.write(str(item) + '\n')

    def load(self, default):
        # Load configuration from file, or use default if file doesn't exist
        try:
            with open(self.config_filename, 'r') as file:
                data = [line.strip() for line in file]
                return int(data[0]), int(data[1]), int(data[2]), int(data[3])
        except OSError:
            return default

    # Get a list of available commands
    def get_cmd_list(self):
        return [self.cmd1, self.cmd2, self.cmd3, self.cmd4, self.cmd5, self.cmd6, self.cmd7]

    # Display the menu
    def show_menu(self, btn):
        cmds = self.get_cmd_list()
        max_cmd = len(cmds)
        menu = MenuSystem(btn, self.leds, self)
        cmd = menu.menu(0, max_cmd)
        menu.mcolor = (0, 0, 255)  # Blue for second-level menu
        if cmd != 0:
            cmd -= 1
            if cmd < max_cmd:
                cmds[cmd](menu)

    # Retrieve a file based on number (0-9)
    def get_file(self, number=0):
        if number < 0 or number > 9:
            raise ValueError("Number must be between 0 and 9")

        file_name = f"/Message{number}.txt"
        try:
            with open(file_name, 'r') as file:
                content = file.read()
                content = sub("\r\n", "\n", content)  # Normalize line endings
                content = sub("#.*?([\r\n]|$)", "", content)  # Remove comments
                content = sub("[\r\n]", " ", content)  # Replace newlines with spaces
            return content
        except OSError:
            return "73"
        except Exception as e:
            return "EEEE"

    # Handle I2C input
    def do_i2c(self):
        c = self.i2c_in.get()
        if 0 < c < 127:
            self.send(bytes([c]).decode())  # Send normal characters
        elif c < 0xC0:
            c &= 0xF
            cmds = self.get_cmd_list()
            if 0 < c <= len(cmds):
                cmds[c - 1](self.i2c_in)
            elif c == 0xE:
                self.abort()

    # Play the current message
    msg_ctr = 1  # Message counter (use _ in message to substitute this value)

    def play(self):
        s = self.get_file(self.message)
        s = sub("_", f"{self.msg_ctr}", s)
        self.autorepeat = (s[0] == Config.DELAY_CHAR)
        self.send(s)
        self.msg_ctr = (self.msg_ctr + 1) if self.msg_ctr < 9999 else 1  # Roll over at 9999

    # Main loop
    def main(self):
        while True:
            if self.countdown == 0 or (self.autorepeat and not self.sequence):
                if not self.do_menu:
                    self.play()
                    gc.collect()
                self.countdown = self.repeat_every if self.repeat_every != 0 else 1
            else:
                if self.repeat_every != 0:
                    self.countdown -= 1

            if self.do_menu:
                gc.collect()
                self.led_active = False  # Turn off LEDs to allow menu to use them
                menu_button = BSButton()
                self.button.stop()
                menu_button.start()
                self.show_menu(menu_button)
                menu_button.stop()
                self.button.start()
                self.led_active = True
                self.leds.fill((0, 0, 0))  # Turn off LEDs
                self.leds.write()
                self.do_menu = False

            if self.i2c_in.any():
                self.do_i2c()

            sleep(1.0 / Config.TIME_SCALE)

def main():
    sleep(0.1)  # Wait for USB to become ready
    MorseMain().main()

if __name__ == "__main__":
    main()


