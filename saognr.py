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

    
    def setall(self,setup=(0,30, 13, 800)):
        (self.message, self.repeat_every, self.wpm, self.cw_tone)=setup
        self.setscale()
        
    def button_push(self):
        if self.sending():
            self.abort()
            countdown=30
        else:
            self.countdown=0
            
    def button_long(self):
        self.abort()
        self.doMenu=True
        
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
        choice=[ 800, 440, 1000, 1200 ]
        self.cw_tone=choice[menu.menu(choice.index(self.cw_tone),3)]
    
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
           
    def save(self, data):
        # Write the list to the file
        with open('/saocw.cfg', 'w') as file:
            for item in data:
                file.write(str(item) + '\n')

    def load(self,default):
        # Open the file and read the contents into a list
        try:
            with open('/saocw.cfg', 'r') as file:
                data = [line.strip() for line in file]
                return ( int(data[0]), int(data[1]), int(data[2]), int(data[3]))
        except OSError:
            return default
   
    def showmenu(self,btn):
        menu=MenuSystem(btn,self.leds,self)
        cmd=menu.menu(0,6)
        menu.mcolor=(0,0,255)  # blue for 2nd level menu if any
        if cmd==1:
            self.cmd1(menu)
        if cmd==2:
            self.cmd2(menu)
        if cmd==3:
            self.cmd3(menu)
        if cmd==4:
            self.cmd4(menu)
        if cmd==5:
            self.cmd5(menu)
        if cmd==6:
            self.cmd6((menu))
    
    def getFile(self,number=0):
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
            return content
        except OSError:
            return "73"
        except Exception as e:
            return "EEEE"

    def do_i2c(self):
        c=self.i2cin.get()
        print(c)
        if c>0 and c<127:
            s=bytes([c]).decode()
            print(f"* {s}")
            self.send(bytes([c]).decode())
        else:
            # command 8X is a real command
            # CX is a "second digit" for all commands
            # so all commands are 8X CN where X is the command # and N is 0-9 
            if c>=0xC0:
                # out of sync! Ignore
                print("IGN")
                return
            c=c&0xF
            print(f"cmd {c}")
            if c==1:
                self.cmd1(self.i2cin)
            if c==2:
                self.cmd2(self.i2cin)
            if c==3:
                self.cmd3(self.i2cin)
            if c==4:
                self.cmd4(self.i2cin)
            if c==5:
                self.cmd5(self.i2cin)
            if c==6:
                self.cmd6(self.i2cin)
            if c==0xe:
                self.abort()
            if c==0xf:     # special command TBD
                pass
    def play(self):
        self.send(self.getFile(self.message))
        
    def main(self):
        while True:
            if self.countdown==0:
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
            if self.doMenu:
                self.led_active=False
                btn=BSButton()
                self.showmenu(btn)
                self.led_active=True
                btn.stop()
                self.doMenu=False
            if self.i2cin.any():
                # an i2c command is pending
                print("I2C")
                self.do_i2c()
            time.sleep(0.1)

def main():
    time.sleep(0.1) # Wait for USB to become ready
    mcode=MorseMain().main()


if __name__ == "__main__":
    main()






