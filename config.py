# configuration things
from machine import Pin

class config:
    TIME_SCALE=10   # how many ticks in a second for main loop
    # default things
    DEF_WPM=13
    DEF_CSPACE_XTRA=1
    DEF_WSPACE_XTRA=1
    DEF_REPEAT_EVERY=30
    DEF_CW_TONE=800

    I2C_SDA=4
    I2C_SCL=5
    I2C_ADD=0x73
    CPU_LED=Pin.board.GP16
    CPU_LED_BASE_COLOR=(0, 64, 0)   # note, will be multipled by up to 2!
    CPU_LED_BREATHE_TIME=60

    BTN_THRESH=10  # how long is a long press (100 millisecond ticks)?