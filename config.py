# configuration things
from machine import Pin

class config:
    TIME_SCALE=10   # how many ticks in a second for main loop
    # menu choices for repeat delay (0 means don't automatically repeat)
    DELAY_TABLE=[ 30, 60, 90, 300, 600, 900, 1800, 3600, 7200 ,0 ]
    # menu choices for WPM
    WPM_TABLE=[13, 5, 20, 25, 50]
    # menu choices for CW_TONE
    TONE_TABLE=[ 800, 440, 1000, 1200, 0 ]

    DEF_WPM=13      # default words per minute (must be value from WPM_TABLE)
    DEF_CSPACE_XTRA=1   # extra character space
    DEF_WSPACE_XTRA=1   # extra word space
    DEF_REPEAT_EVERY=30  # default time to repeat (needs to be a value from DELAY TABLE)
    DEF_CW_TONE=800      #  default side tone (must be from TONE_TABLE)
    DELAY_CHAR="~"      # character that causes 1 second delay in messages

    I2C_SDA=4     # I2C target SDA/SCL and address
    I2C_SCL=5
    I2C_ADD=0x73

    # onboard neopixel
    CPU_LED=Pin.board.GP16
    # base color for onboard neopixel (elements will be multipled by up to 2 so 127 max per color)
    CPU_LED_BASE_COLOR=(0, 64, 0)   
    # onboard LED will "breathe" at this rate
    CPU_LED_BREATHE_TIME=60

    BTN_THRESH=10  # how long is a long press (100 millisecond ticks)?