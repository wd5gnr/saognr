import time
import neopixel
from machine import Pin, PWM, Timer
from utime import sleep

p = machine.Pin.board.GP13
leds = neopixel.NeoPixel(p, 25)
SPEAKER_PIN = machine.Pin.board.GP26
speaker = PWM(Pin(SPEAKER_PIN))


def get_btn():
    return rp2.bootsel_button()


time.sleep(0.1) # Wait for USB to become ready
print("Ready")


def LEDSet(color,setarray=None):
    global leds
    if setarray==None:
        return
    for i in range(4):
        if setarray[i]:
            leds[i]=color
    leds.write()

# so maybe
# element countdown (in ticks)
# when element reaches 0, turn off LEDs and buzzer
# main sets it
# also button count up
# when button active, add one otherwise nothing (main zeros it)

# could make element countdown a circular buffer/list
# each time it inverts the LED and buzzer
# So to send ABC you would  set list to
# [ DOT, DOTSP, DASH, DASHSP, DASH, DOTSP, DOT, DOTSP, DOT, DOTSP, DOT, DASHSP, etc....]
# might as well put tone and colors inside

btn_count=0
btn_off=0

# Example setup function
def setup(frequency,colors):
    global leds
    if frequency==0:
        speaker.duty_u16(0)
    else:
        speaker.duty_u16(1000)
        speaker.freq(frequency)
    for i in range(4):
        if colors[i]:
            leds[i]=colors[i]
    leds.write()

def timer_callback(timer, sequence):
    global btn_count, btn_off
    if get_btn():
        btn_count=btn_count+1   # user sets to zero
        btn_off=0
    else:
        btn_off=1
    if not sequence:
        return  # No more items to process, exit the callback

    # Get the first tuple in the list
    item = sequence[0]
    duration, frequency, colors, in_progress = item

    if not in_progress:
        # First time seeing this item, call setup and mark as in progress
        setup(frequency,colors)
        sequence[0] = (duration - 1, frequency, colors, True)
    else:
        # Item is already in progress, just decrement the tick count
        sequence[0] = (duration - 1, frequency, colors, True)
        # If the duration has reached zero, remove the item from the list
        # Note we will still handle the case where duration is 1
        if sequence[0][0] <= 0:
            sequence.pop(0)
            speaker.duty_u16(0)  # speaker off
            LEDSet((0,0,0),[True,True,True,True])

# Create a list of tuples: (duration, frequency, in_progress)
sequence = []


cw_tone=800
wpm=13
wpmdelay=1200/wpm  # in milliseconds
delayscale=int(wpmdelay+0.5)
cspace_xtra=1
wspace_xtra=2

# Set up a Timer with the callback, adjust the period as necessary
# 13 WPM is about 90ms per element for the record (92.31 from http://www.kent-engineers.com/codespeed.htm)
timer = Timer(-1)
timer.init(period=1, mode=Timer.PERIODIC, callback=lambda t: timer_callback(t, sequence))




def dot():
    global sequence
    sequence.append((delayscale,cw_tone,[(128,128,128),(128,0,0),(128,0,0),(128,128,128)],False))
    sequence.append((delayscale,0,[(0,0,0),(0,0,0),(0,0,0),(0,0,0)],False))

def dash():
    global sequence
    sequence.append((3*delayscale,cw_tone,[(128,128,128),(0,128,0),(0,128,0),(128,128,128)],False))
    sequence.append((delayscale,0,[(0,0,0),(0,0,0),(0,0,0),(0,0,0)],False))

def cspace():
    global sequence
    sequence.append((delayscale+cspace_xtra,0,[(0,0,0),(0,0,0),(0,0,0),(0,0,0)],False))
    
def wspace(): # note: the 7th delay is the previous cspace!
    global sequence
    sequence.append((6*delayscale+wspace_xtra,0,[(0,0,0),(0,0,0),(0,0,0),(0,0,0)],False))

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
    "4":"...._",
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

def send(input_string):
    for char in input_string:
        if char == " ":
            wspace()  # Call wspace() for word space
            continue
        
        char = char.upper()  # Convert character to upper case
        if char not in morse:
            print(f"Warning: '{char}' not found in Morse dictionary")
            continue
        
        morse_code = morse[char]  # Lookup in the morse dictionary
        
        for symbol in morse_code:
            if symbol == ".":
                dot()  # Call dot() for a period
            elif symbol == "-":
                dash()  # Call dash() for a dash
        
        cspace()  # Call cspace() after processing the character

repeat_every=30
countdown=0

def button_push():
    global countdown
    countdown=0
    
def button_long():
    print("Enter menu")
    
def button_hold():
    print("OK you got my attention")

menu_lock=False

def menu(count):
    global menu_lock
    if menu_lock:
        return
    if count<10:
        menu_lock=True
        button_push()
        menu_lock=False
    elif count<300:
        menu_lock=True
        button_long()
        menu_lock=False
    else:
        menu_lock=True
        button_hold()
        while btn_off==0:
            time.sleep(0.01)
        menu_lock=False
        



while True:
    if countdown==0:
        send("CQ es 73 de wd5gnr =")
        countdown=repeat_every
    else:
        countdown=countdown-1
 # if btn_count!=0 then the button is or has been down
 # if btn_off==0 then the button is still down
 # if btn_off==1 then the button is up and you can read the count and figure out how long the press is
 # note the units are "ticks" of the main timer (1ms unless you've changed it)
    if btn_count!=0 and (btn_off!=0 or btn_count>30000):     # don't wait for super long press
        print(f"menu @{btn_count}")
        menu(int(btn_count/100))
        btn_count=0
    time.sleep(1) 

