import time
from machine import Timer

# This class doesn't know about audio or LEDs or anything else
# It just does code and you have to override setup and/or proc_input to do what you really want
# That means you could use this in many places
# The setup has to set up whatever you are doing to send a dot or a dash
# That might mean keying a transmitter or a light or a buzzer or whatever you do to make dots and dashes

class Morse:
    # code sounds a little more natural with some extra spaces, but you can change that if you like
    def __init__(self, wpm=13, cspace_xtra=1, wspace_xtra=1):
        self.timer=Timer(-1)
        self.timer.init(period=1, mode=Timer.PERIODIC, callback=lambda t: self.timer_callback(t))
        self.sequence=[]
        self.wpm=wpm
        self.setscale()
        self.cspace_xtra=cspace_xtra
        self.wspace_xtra=wspace_xtra
 # constants
    DOT=1
    DASH=2
    STOP=0
    
    # every time the WPM changes, we need to recalculate the delayscale (see http://www.kent-engineers.com/codespeed.htm)
    def setscale(self):
        self.delayscale=int(1200/self.wpm+0.5)
    
    # do we have more things to send?
    def sending(self):
        return self.sequence!=[]
    
    # stop sending things now
    def abort(self):
        self.setup(0)
        self.sequence=[]
    
    def proc_input(self):     # a place to process inputs
        pass
        
    # set up output
    def setup(self,element):  # This is a stupid function but you will override it
        if element==Morse.DOT:
            print(".")
        elif element==Morse.DASH:
            print("-")
        
    # The timer processes tuples ( count, element, in_progressflag)
    # The count will work down to zero, the element is DOT/DASH/SPACE, in progress is always false until
    # the callback changes it to True
    # the countdown is in milliseconds
    def timer_callback(self, timer):
        self.proc_input()
        if not self.sequence:
            return  # No more items to process, exit the callback

        # Get the first tuple in the list
        item = self.sequence[0]
        duration, element, in_progress = item

        if not in_progress:
            # First time seeing this item, call setup and mark as in progress
            self.setup(element)
            self.sequence[0] = (duration - 1, element, True)
        else:
            # Item is already in progress, just decrement the tick count
            self.sequence[0] = (duration - 1, element, True)
            # If the duration has reached zero, remove the item from the list
            # Note we will still handle the case where duration is 1
            if self.sequence[0][0] <= 0:
                self.sequence.pop(0)
                self.setup(0)  # everything off

    # queue up a dot, dash, or one of the space types             
    def dot(self):
        self.sequence.append((self.delayscale,1,False))
        self.sequence.append((self.delayscale,0,False))

    def dash(self):
        self.sequence.append((3*self.delayscale,2,False))
        self.sequence.append((self.delayscale,0,False))

    def cspace(self):
        self.sequence.append((self.delayscale+self.cspace_xtra,0,False))
        
    def wspace(self): # note: the 7th delay is the previous cspace!
        self.sequence.append((6*self.delayscale+self.wspace_xtra,0,False))
    
    # queue an arbitrary delay in seconds
    def delay(self,n=1):  # delay some number of seconds
        for i in range(n):
            self.sequence.append((1000,0,False))

# the Morse code table (note all uppercase)
    morse = {
        "A":".-",
        "B":"-...",
        "C":"-.-.",
        "D":"-..",
        "E":".",
        "F":"..-.",
        "G":"--.",
        "H":"....",
        "I":"..",
        "J":".---",
        "K":"-.-",
        "L":".-..",
        "M":"--",
        "N":"-.",
        "O":"---",
        "P":".--.",
        "Q":"--.-",
        "R":".-.",
        "S":"...",
        "T":"-",
        "U":"..-",
        "V":"...-",
        "W":".--",
        "X":"-..-",
        "Y":"-.--",
        "Z":"--..",
        "0":"-----",
        "1":".----",
        "2":"..---",
        "3":"...--",
        "4":"....-",
        "5":".....",
        "6":"-....",
        "7":"--...",
        "8":"---..",
        "9":"----.",
        ".":".-.-.-",
        ",":"-.-.",
        "=":"-...-",   # BT
        "/":"-..-.",
        "#":".-.-."    # AR
    }

# send a string. Spaces/CR/LF are OK. ~ delays 1 second
# control characters are ignored, but others issue a warning
# that you will probably never see and keeps going
# characters can be upper/lower
    def send(self,input_string):
        for char in input_string:
            if char == " " or char=='\r' or char=='\n':
                self.wspace()  # Call wspace() for word space
                continue
            if char == "~":
                self.delay()
                continue
            if char < ' ':
                continue   # ignore control characters
            char = char.upper()  # Convert character to upper case
            if char not in self.morse:
                print(f"Warning: '{char}' not found in Morse dictionary")
                continue
            morse_code = self.morse[char]  # Lookup in the morse dictionary
            # queue the dots and dashes
            for symbol in morse_code:
                if symbol == ".":
                    self.dot()  # Call dot() for a period
                elif symbol == "-":
                    self.dash()  # Call dash() for a dash
            
            self.cspace()  # Call cspace() after processing the character
