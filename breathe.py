import machine
from math import sin

# Class to create a breathing LED effect using Neopixels
# - led: Neopixel array
# - color: the color (will be clipped at (127,127,127))
# - cycle: The cycle time in milliseconds
# - index: First Neopixel to affect
# - count: Number of Neopixels to affect (not used in this code)

class Breathe():
    def __init__(self, led, color, cycle=60, index=0, count=1):
        self.tm = machine.Timer(-1)  # Initialize a timer
        self.led = led  # Store the Neopixel object
        # could validate color for being (r, g, b) but what to do if not???
        self.color = tuple(value % 128 for value in color)  # Clip color values to max of 127
        self.index = index  # Store the starting index for the Neopixel
        self.count = count  # Store the count of Neopixels to affect
        self.breathe_counter = 0  # Counter for breathing effect
        self.set_led(self.color)  # Set the initial color of the LED
        # Initialize the timer to call breathe_callback at a regular interval
        self.tm.init(period=cycle, mode=machine.Timer.PERIODIC, callback=lambda t: self.breathe_callback(t))

    def set_led(self, newcolor):  
        # Method to update the color of the specified Neopixel
        for i in range(self.count):
            self.led[self.index+i] = newcolor  # Set the color for the LED at the specified index
        self.led.write()  # Write the updated color to the Neopixel

    def breathe_callback(self, t):
        # Method called by the timer to update the LED color
        self.breathe_counter += 10  # Increment the counter (effectively 0.1 since divided by 100 later)
        if self.breathe_counter > 628:  # Reset after a full sine wave (2*pi*100)
            self.breathe_counter = 0
        modulate = sin(float(self.breathe_counter) / 100.0) + 1.0  # Calculate modulation factor (range: 0 to 2)
        mcolor = tuple(int(x * modulate) for x in self.color)  # Modulate the base color for breathing effect
        self.set_led(mcolor)  # Update the LED with the modulated color

def main():
    import neopixel
    # Create a Breathe object to control a single Neopixel with a green color and a cycle of 60ms
    b = Breathe(neopixel.NeoPixel(machine.Pin(16), 1), (0, 127, 0), 60)
    while True:
        pass  # Keep the program running indefinitely

if __name__ == "__main__":
    print("Test main")  
    main()  # Call the main function to execute the program
