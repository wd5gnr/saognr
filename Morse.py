import time
from machine import Timer
from config import Config  

# This class handles Morse code timing and sequencing.
# It doesn't know about audio, LEDs, or other outputs.
# You must override `setup` and/or `proc_input` in a subclass
# to define what happens for a dot, dash, or stop (e.g., keying a transmitter, lighting a LED).

class Morse:
    # Morse code is slightly more readable with extra spaces between characters,
    # but you can adjust this using the cspace_xtra and wspace_xtra values.
    def __init__(self, wpm=Config.DEFAULT_WPM, cspace_xtra=Config.DEFAULT_EXTRA_CHAR_SPACE, 
                 wspace_xtra=Config.DEFAULT_EXTRA_WORD_SPACE):
        self.timer = Timer(-1)  # 1 ms timer
        self.timer.init(period=1, mode=Timer.PERIODIC, callback=lambda t: self.timer_callback(t))
        self.sequence = []  # List of scheduled events (dots, dashes, spaces)
        self.wpm = wpm
        self.setscale()  # Calculate delays based on words per minute (WPM)
        self.cspace_xtra = cspace_xtra  # Extra character space
        self.wspace_xtra = wspace_xtra  # Extra word space

    # Constants to represent the elements of Morse code
    DOT = 1
    DASH = 2
    STOP = 0

    # Recalculate delays based on WPM (Words Per Minute)
    def setscale(self):
        # Calculate delay scale in milliseconds per dot (from WPM)
        self.delayscale = int(1200 / self.wpm + 0.5)  # 1200ms per word, rounded

    # Check if there are more Morse code elements to send
    def sending(self):
        return bool(self.sequence)

    # Stop sending Morse code
    def abort(self):
        self.setup(Morse.STOP)  # Turn off any active signal
        self.sequence.clear()  # Clear the sequence list

    # Process input (override this in a subclass if needed)
    def proc_input(self):
        pass

    # Setup the output (override this in a subclass)
    def setup(self, element):
        # For testing purposes, print the dots and dashes to the console.
        if element == Morse.DOT:
            print(".")  # Represents a dot
        elif element == Morse.DASH:
            print("-")  # Represents a dash
        # Normally you'd handle Morse.STOP (0) here too, but for now, we ignore it.

    # Timer callback to process the next Morse element
    def timer_callback(self, timer):
        self.proc_input()  # Process input in case there's user interaction (e.g., button press)

        if not self.sequence:
            return  # No more Morse code to send, so exit

        # Get the current item in the sequence
        duration, element, in_progress = self.sequence[0]

        if not in_progress:
            # If not already in progress, start the new Morse element
            self.setup(element)
            self.sequence[0] = (duration - 1, element, True)  # Mark it as in progress
        else:
            # If in progress, decrement the duration and continue
            self.sequence[0] = (duration - 1, element, True)

            if self.sequence[0][0] <= 0:
                # Remove the item from the sequence if its duration is complete
                self.sequence.pop(0)
                self.setup(Morse.STOP)  # Stop the signal when the duration ends

    # Queue a dot in the sequence
    def dot(self):
        self.sequence.append((self.delayscale, Morse.DOT, False))  # Append dot duration
        self.sequence.append((self.delayscale, Morse.STOP, False))  # Append space after the dot

    # Queue a dash in the sequence
    def dash(self):
        self.sequence.append((3 * self.delayscale, Morse.DASH, False))  # Append dash duration (3x longer than dot)
        self.sequence.append((self.delayscale, Morse.STOP, False))  # Append space after the dash

    # Queue a character space
    def cspace(self):
        self.sequence.append((self.delayscale + self.cspace_xtra, Morse.STOP, False))  # Append character space

    # Queue a word space (note: the previous character space counts as the first unit of the word space)
    def wspace(self):
        self.sequence.append((6 * self.delayscale + self.wspace_xtra, Morse.STOP, False))  # Append word space

    # Queue an arbitrary delay in seconds
    def delay(self, n=1):
        for _ in range(n):
            self.sequence.append((1000, Morse.STOP, False))  # Delay for `n` seconds

    # Morse code dictionary (uppercase characters)
    morse = {
        "A": ".-",
        "B": "-...",
        "C": "-.-.",
        "D": "-..",
        "E": ".",
        "F": "..-.",
        "G": "--.",
        "H": "....",
        "I": "..",
        "J": ".---",
        "K": "-.-",
        "L": ".-..",
        "M": "--",
        "N": "-.",
        "O": "---",
        "P": ".--.",
        "Q": "--.-",
        "R": ".-.",
        "S": "...",
        "T": "-",
        "U": "..-",
        "V": "...-",
        "W": ".--",
        "X": "-..-",
        "Y": "-.--",
        "Z": "--..",
        "0": "-----",
        "1": ".----",
        "2": "..---",
        "3": "...--",
        "4": "....-",
        "5": ".....",
        "6": "-....",
        "7": "--...",
        "8": "---..",
        "9": "----.",
        ".": ".-.-.-",
        ",": "--..--",
        "=": "-...-",  # BT
        "/": "-..-.",
        "?": "..--..",
        ":": "---...",
        "-": "-....-",
        "!": "-.-.--",
        "+": ".-.-."  # AR
    }

    # Send a string in Morse code
    def send(self, input_string):
        for char in input_string:
            if char == " " or char == '\r' or char == '\n':
                self.wspace()  # Call wspace() for word space
                continue
            if char == Config.DELAY_CHAR:
                self.delay()  # Delay 1 second for special delay character
                continue
            if char < ' ':  # Ignore control characters
                continue
            char = char.upper()  # Convert to uppercase
            if char not in self.morse:
                print(f"Warning: '{char}' not found in Morse dictionary")  # Warn for unknown characters
                continue
            morse_code = self.morse[char]  # Get Morse code for character

            # Queue dots and dashes for the Morse code of this character
            for symbol in morse_code:
                if symbol == ".":
                    self.dot()  # Queue a dot
                elif symbol == "-":
                    self.dash()  # Queue a dash

            self.cspace()  # Append a character space after the letter
