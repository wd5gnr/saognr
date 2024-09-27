import time
import neopixel
import os
import gc
from machine import Pin, PWM, Timer
from utime import sleep

# 13 WPM is about 90ms per element for the record (92.31 from http://www.kent-engineers.com/codespeed.htm)

from MenuMorse import MenuMorse
from MenuSystem import MenuSystem
from Button import BSButton
from i2ctarget import i2cmenutarget
from math import sin

TIME_SCALE=10

class MorseMain(MenuMorse):
    def __init__(self, wpm=13, cspace_xtra=1, wspace_xtra=2, repeat_every=30*TIME_SCALE):
        super().__init__(wpm, cspace_xtra, wspace_xtra)
        self.countdown=0
        self.repeat_every=repeat_every
        self.message=0
        self.doMenu=False
        self.setall(self.load(( self.message, self.repeat_every, self.wpm, self.cw_tone)))
        self.i2cin=i2cmenutarget(0,sda=4,scl=5,address=0x73)
        self.led=neopixel.NeoPixel(Pin.board.GP16,1)
        self.setLED((0,64,0))
        self.bTimer=Timer(-1)
        self.bTimer.init(period=60, mode=Timer.PERIODIC, callback=lambda t: self.breathe_callback(t))

# set the RP2040-Zero onboard GRB LED (pass RGB, we will untangle it)
    def setLED(self,color):
        self.led[0]=( color[1], color[0], color[2])
        self.led.write()

# make the onboard LED "breathe"
    bcounter=0
    def breathe_callback(self,t):
        self.bcounter=self.bcounter+10
        if self.bcounter>628:
            self.bcounter=0
        modulate=sin(float(self.bcounter)/100.0)+1.0   # now 0-2
        self.setLED((0,int(64*modulate),0))  # green goes from 0 to 128

# set all config values and scale
    def setall(self,setup=(0,30, 13, 800)):
        (self.message, self.repeat_every, self.wpm, self.cw_tone)=setup
        self.setscale()

# here when button is pushed (quick)
    def button_push(self):  # if sending, pause otherwise trigger
        if self.sending():
            self.abort()
            countdown=self.repeat_every
        else:
            self.countdown=0

# here when button is long pushed            
    def button_long(self):
        self.abort()           # stop sending 
        self.doMenu=True       # do menu

# commands can be triggered by menu or by I2C
# most commands take a second entry (see help.txt)
# 0 - Exit menu (do nothing)
# 1 - Select file 0-9
# 2 - Select delay
# 3 - Select speed
# 4 - Select tone
# 5 - Save configuration (0=no, 1=yes, 2=erase)
# 6 - Reset to default (1=yes) does not save
        
    def cmd1(self,menu):  # select file
        self.message=menu.menu(self.message)
    
    def cmd2(self,menu):  # select delay
        choice=[ 30, 60, 90, 300, 600, 900, 1800, 3600, 7200 ,0 ]
        self.repeat_every=choice[menu.menu(choice.index(self.repeat_every),9)]*TIME_SCALE
        if self.repeat_every==0:
            self.countdown=1
        else:
            self.countdown=0
    
    def cmd3(self,menu):   # select speed
        choice=[13, 5, 20, 25, 50]
        self.wpm=choice[menu.menu(choice.index(self.wpm),4)]
        self.setscale()
        
    
    def cmd4(self,menu):    # select tone
        choice=[ 800, 440, 1000, 1200, 0 ]
        self.cw_tone=choice[menu.menu(choice.index(self.cw_tone),4)]
    
    def cmd5(self,menu):   # save config for reboot
        yesno=menu.menu(0,2)
        if yesno==2:
            try:
                os.remove('/saocw.cfg')
            except OSError:
                return
        if yesno==1:
            self.save([ self.message, self.repeat_every, self.wpm, self.cw_tone])
    
    def cmd6(self, menu):    # reset to defaults
       yesno=menu.menu(0,1)
       if yesno==1:
           self.setall()
           
    fn="/saognr.cfg"    # config file name

    def save(self, data):
        # Write the list to the file
        with open(self.fn, 'w') as file:
            for item in data:
                file.write(str(item) + '\n')

    def load(self,default):
        # Open the file and read the contents into a list
        try:
            with open(self.fn, 'r') as file:
                data = [line.strip() for line in file]
                return ( int(data[0]), int(data[1]), int(data[2]), int(data[3]))
        except OSError:
            return default
   
# get command array
    def getcmdlist(self):
        return [self.cmd1, self.cmd2, self.cmd3, self.cmd4, self.cmd5, self.cmd6 ]
# show a menu
    def showmenu(self,btn):
        cmds=self.getcmdlist()
        maxcmd=len(cmds)
        menu=MenuSystem(btn,self.leds,self)
        cmd=menu.menu(0,maxcmd)
        menu.mcolor=(0,0,255)  # blue for 2nd level menu if any
        if cmd!=0:
            cmd=cmd-1
            if cmd<maxcmd:
                cmds[cmd](menu)
    
    def getFile(self,number=0):
        from re import sub
    # Ensure the number is between 0 and 9
        if number < 0 or number > 9:
            raise ValueError("Number must be between 0 and 9")
    
    # Construct the file name using the number
        file_name = f"/Message{number}.txt"
    
        try:
        # Open the file, read its contents, and close it
            with open(file_name, 'r') as file:
                content = file.read()
                file.close()
                content=sub("\r\n","\n",content)  # fold new lines
                content=sub("#.*?([\r\n]|$)","",content)   # remove comments
                content=sub("[\r\n]"," ",content)    # newlines are spaces
            return content
        except OSError:
            return "73"
        except Exception as e:
            return "EEEE"

# handle i2C input
    def do_i2c(self):
        c=self.i2cin.get()
        if c>0 and c<127:
            s=bytes([c]).decode()
            self.send(bytes([c]).decode())   # send normal characters
        else:
            # command 8X is a real command
            # CX is a "second digit" for all commands
            # so all commands are 8X CN where X is the command # and N is 0-9 
            if c>=0xC0:
                # out of sync! Ignore
                return
            c=c&0xF
            cmds=self.getcmdlist()
            if c>0 and c<=len(cmd):
                cmds[c-1](self.i2cin)
            elif c==0xe:
                self.abort()

# play the curent message
    def play(self):
        self.send(self.getFile(self.message))


# start here
    def main(self):
        while True:
            if self.countdown==0:   # time to send?
                if self.doMenu==False:
                    self.play()
                    gc.collect()
                if self.repeat_every!=0:
                    self.countdown=self.repeat_every
                else:
                    self.countdown=1   # just in case you manual trigger when repeat every is set to 0
            else:
                if self.repeat_every!=0:
                    self.countdown=self.countdown-1
            if self.doMenu:   # check for menu
                gc.collect()
                self.led_active=False  # turn off LEDs so menu can send code and still use them
                mbutton=BSButton()   # get button (and turn off menu system's button)
                self.button.stop()
                mbutton.start()
                self.showmenu(mbutton)
                mbutton.stop()
                self.button.start()
                self.led_active=True
                self.doMenu=False
            if self.i2cin.any():       # check for I2C
                # an i2c command is pending
                self.do_i2c()
            time.sleep(0.1)

def main():
    time.sleep(0.1) # Wait for USB to become ready
    mcode=MorseMain().main()


if __name__ == "__main__":
    main()






