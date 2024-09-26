import time
from machine import Timer

# This class doesn't know about audio or LEDs or anything else
# It just does code and you have to override setup and/or proc_input to do what you really want
class Morse:
    def __init__(self, wpm=13, cspace_xtra=1, wspace_xtra=1):
        self.timer=Timer(-1)
        self.timer.init(period=1, mode=Timer.PERIODIC, callback=lambda t: self.timer_callback(t))
        self.sequence=[]
        self.wpm=wpm
        self.delayscale=int(1200/wpm+0.5)
        self.cspace_xtra=cspace_xtra
        self.wspace_xtra=wspace_xtra
 # constants
    DOT=1
    DASH=2
    STOP=0
    
    def setscale(self):
        self.delayscale=int(1200/self.wpm+0.5)
    
    def sending(self):
        return self.sequence!=[]
    
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
    
    def delay(self,n=1):  # delay some number of seconds
        for i in range(n):
            self.sequence.append((1000,0,False))

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

    def send(self,input_string):
        for char in input_string:
            if char == " ":
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
            
            for symbol in morse_code:
                if symbol == ".":
                    self.dot()  # Call dot() for a period
                elif symbol == "-":
                    self.dash()  # Call dash() for a dash
            
            self.cspace()  # Call cspace() after processing the character
