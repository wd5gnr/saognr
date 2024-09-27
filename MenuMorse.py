import time
from MorseCode import MorseCode
from Button import BSButton
from config import Config  

# This class extends MorseCode but adds functionality for handling button presses (bootsel button).
# - Override button_push for a short button press.
# - Override button_long for a long button press.
# - If the button is held for an extended period (15s), the LEDs turn dim red,
#   and the button_hold method is called once the button is released.
class MenuMorse(MorseCode):
    def __init__(self, wpm=Config.DEFAULT_WPM, cspace_xtra=Config.DEFAULT_EXTRA_CHAR_SPACE, 
                 wspace_xtra=Config.DEFAULT_EXTRA_WORD_SPACE, thresh1=Config.LONG_PRESS_THRESHOLD, thresh2=0):
        """
        Initialize the MenuMorse class.
        - wpm: Words per minute for Morse code.
        - cspace_xtra: Extra space between characters.
        - wspace_xtra: Extra space between words.
        - thresh1: Threshold for detecting a long button press.
        - thresh2: Threshold for detecting a super-long button hold (set to 0 if not used).
        """
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.menu_lock = False  # Flag to allow or block menu processing
        self.thresh1 = thresh1  # Threshold for a long press
        self.thresh2 = thresh2  # Threshold for a super-long press (0 if not used)
        self.button = BSButton()  # Create a button instance
        self.button.start()  # Start the button monitoring

    # Override this method to define behavior for a short button press
    def button_push(self):
        print("Short Press Detected")

    # Override this method to define behavior for a long button press
    def button_long(self):
        print("Long Press Detected")

    # Override this method to define behavior for a very long button hold
    def button_hold(self):
        print("Hold Detected")

    # Handle button press durations and call appropriate actions based on thresholds
    def basemenu(self, count):
        """
        Determine the type of button press based on the duration (count).
        - Short press if duration < thresh1.
        - Long press if duration >= thresh1 and < thresh2.
        - Very long press if duration >= thresh2.
        """
        if self.menu_lock:  # If menu is locked, do nothing
            return

        if count < self.thresh1:  # Short press
            self.menu_lock = True
            self.button_push()  # Call short press action
            self.menu_lock = False
        elif self.thresh2 == 0 or count < self.thresh2:  # Long press
            self.menu_lock = True
            self.button_long()  # Call long press action
            self.menu_lock = False
        else:  # Very long press (super-long hold)
            self.menu_lock = True
            self.leds.write()  # Turn on dim red LEDs to indicate hold
            while self.button.get_btn() == 1:  # Wait for button release
                time.sleep(0.01)  # Poll every 10ms to check for button release
            self.button_hold()  # Call the hold action
            self.menu_lock = False

    # Periodically scan for button inputs
    # The button works with btn_count representing the duration the button has been pressed (in ms).
    # btn_off is 0 while the button is still pressed and 1 when the button is released.
    # We process the button only when btn_off is 1 (button released).
    def proc_input(self):
        super().proc_input()  # Call parent class proc_input (in case it has functionality)
        if self.button.btn_count != 0 and self.button.btn_off != 0:
            self.basemenu(int(self.button.btn_count / 10))  # Convert ms to 100ms units
            self.button.btn_count = 0  # Reset button count after processing
