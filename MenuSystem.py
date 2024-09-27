import time

# Menu system for selecting options using buttons and providing feedback via LEDs and optional Morse code
# - buttons: the button object to handle user input
# - leds: an optional LED strip or display for visual feedback (can show menu levels and values)
# - feedback: an optional Morse class instance for audio feedback (e.g., sending digits in Morse code)
# - mcolor: the color for the first LED to indicate the menu level (default is purple)

MENU_SCAN_TIME = 0.05  # How often to scan the buttons (in seconds)

class MenuSystem:
    def __init__(self, buttons, leds=None, feedback=None, mcolor=(127, 0, 255)):
        self.buttons = buttons  # Button input handler
        self.leds = leds  # LED strip or LED display (optional)
        self.fb = feedback  # Feedback system (optional, for sending Morse code)
        self.mcolor = mcolor  # Default color for the first LED (menu level indicator)
    
    # Resistor color codes (approximate RGB values for each color)
    # Black is excluded, and some colors (brown, orange, gray) are approximate.
    colors = [
        (10, 0, 10),  # Not really black
        (34, 17, 0),  # Brown (not exact)
        (255, 0, 0),  # Red
        (255, 165, 0),  # Orange (sort of)
        (255, 255, 0),  # Yellow
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (127, 0, 255),  # Violet
        (64, 64, 64),  # Gray (sort of)
        (255, 255, 255)  # White
    ]
    
    # Main menu logic
    # - value: the current selected value (default 0)
    # - max: the maximum selectable value (default 9)
    def menu(self, value=0, max=9):
        if self.fb:  # If feedback is enabled, stop any active feedback and send the current value
            self.fb.abort()
            self.fb.send(str(value))

        while True:
            # Update the LEDs with the current menu level and value
            if self.leds:
                self.leds[0] = self.mcolor  # Set the color of the first LED (menu level indicator)
                self.leds[1] = self.colors[value]  # Set the color of the second LED (current value indicator)
                self.leds.write()  # Write the changes to the LEDs

            # Handle button input
            if self.buttons.btn_count != 0 and self.buttons.btn_off != 0:  # Check for valid button press
                if self.buttons.btn_count > 100:  # Long press (threshold respected)
                    self.buttons.btn_count = 0  # Reset button count
                    if self.fb:  # If feedback is enabled, stop any active feedback
                        self.fb.abort()
                    return value  # Return the selected value and exit the menu

                self.buttons.btn_count = 0  # Reset for short press
                value += 1  # Increment the value
                if value > max:  # If value exceeds max, wrap around to 0
                    value = 0

                # Send feedback (new value) if enabled
                if self.fb:
                    self.fb.abort()  # Stop any ongoing Morse code feedback
                    self.fb.send(str(value))  # Send the new value as Morse code

            time.sleep(MENU_SCAN_TIME)  # Wait briefly before checking buttons again
