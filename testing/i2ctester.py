import machine
import time


i2c=machine.I2C(1,scl=machine.Pin(15),sda=machine.Pin(14))
byteval=0

def test():
    global byteval
    try:
        byteval=(byteval+1) & 0xff
        print(byteval)
        i2c.writeto(0x73,bytes([byteval]))
    except:
        pass



def main():
    led = machine.Pin(25,machine.Pin.OUT)
    while True:
        led.low()
        time.sleep(0.5)
        # test()
        i2c.writeto(0x73,bytes([0x8e, 0x83, 0xC0, 65, 66, 67]))
        time.sleep(2)
        led.high()
        time.sleep(10)

if __name__=="__main__":
    main()