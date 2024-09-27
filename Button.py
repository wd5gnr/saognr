from machine import Timer
from rp2 import bootsel_button

DEF_SCAN_TIME = 10  # Button scan time in milliseconds (default)

# Generic button class that measures how long a button is pressed and whether it has been released.
# This is a base class; it does not work directly (see BSButton below for a functional implementation).
# The calling program must reset the `btn_count` after processing a press.
class Button:
    def __init__(self, scantime=DEF_SCAN_TIME):
        """
        Initialize the Button class.
        - scantime: Time interval for polling the button state (in milliseconds).
        """
        self.btn_count = 0  # Tracks how long the button has been pressed (in scan periods)
        self.btn_off = 0  # 0 = no change, 1 = button was pressed but is now released
        self.timer = Timer(-1)  # Create a Timer instance (not active yet)
        self.scantime = scantime  # Polling interval for the button

    # This method should be overridden by subclasses to return the current state of the button.
    # It should return 1 if the button is pressed, 0 if not.
    def get_btn(self):
        return 0  # Placeholder, override in subclass
    
    # Timer callback function that runs at each scan interval.
    # It checks the button state and updates `btn_count` and `btn_off` accordingly.
    def timer_callback(self, t):
        if self.get_btn():  # Button is currently pressed
            self.btn_count += 1  # Increment the count (button held)
            self.btn_off = 0  # Button is still pressed, so reset `btn_off`
        else:  # Button is not pressed
            self.btn_off = 1  # Mark that the button was released

    # Start polling the button at the specified interval (scantime).
    def start(self):
        """
        Start the button monitoring.
        Resets the `btn_count` and `btn_off` values, then starts the timer.
        """
        self.btn_count = 0  # Reset press count
        self.btn_off = 0  # Reset button release flag
        self.timer.init(period=self.scantime, mode=Timer.PERIODIC, callback=lambda t: self.timer_callback(t))

    # Stop polling the button (deactivate the timer).
    def stop(self):
        """
        Stop the button monitoring by deinitializing the timer.
        """
        self.timer.deinit()

# A real implementation of the Button class using the Raspberry Pi Pico's Bootsel button.
# Note: This button reads from the Bootsel button, which disconnects the flash to function.
# This can have side effects, but it's not typically an issue for short presses.
class BSButton(Button):
    def get_btn(self):
        """
        Get the state of the Pico Bootsel button.
        - Returns 1 if the Bootsel button is pressed, 0 if not.
        """
        return bootsel_button()

