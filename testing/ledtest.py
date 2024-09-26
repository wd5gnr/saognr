import machine
import time
led = machine.Pin(25,machine.Pin.OUT)

while True:
    led.low()
    time.sleep(0.5)
    led.high()
    time.sleep(0.5)