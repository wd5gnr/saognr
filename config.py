# Configuration settings for the entire program

class Config:
    TIME_SCALE = 10  # Number of ticks per second for the main loop

    # Menu choices for repeat delay (in seconds); 0 means no automatic repeat
    DELAY_TABLE = [30, 60, 90, 300, 600, 900, 1800, 3600, 7200, 0]
    
    # Menu choices for Words Per Minute (WPM) settings
    WPM_TABLE = [13, 5, 20, 25, 50] 
    
    # Menu choices for Continuous Wave (CW) tone frequencies in Hz; 0 means no tone
    TONE_TABLE = [800, 440, 1000, 1200, 0]

    # Default configuration values
    DEFAULT_WPM = 13  # Default WPM, must be a value from WPM_TABLE
    DEFAULT_EXTRA_CHAR_SPACE = 1  # Extra space between characters
    DEFAULT_EXTRA_WORD_SPACE = 1  # Extra space between words
    DEFAULT_REPEAT_DELAY = 60  # Default repeat delay, must be from DELAY_TABLE
    DEFAULT_CW_TONE = 800  # Default CW side tone, must be from TONE_TABLE

    # Character that causes a 1-second delay in transmitted messages
    DELAY_CHAR = "~"

    # I2C bus configuration
    I2C_SDA_PIN = 4  # Pin for I2C data (SDA)
    I2C_SCL_PIN = 5  # Pin for I2C clock (SCL)
    I2C_ADDRESS = 0x73  # I2C target address
    LED4_PIN = 14   # Array of 4 Neopixels
    SPEAKER_PIN = 0  # Speaker

    # Onboard NeoPixel configuration
    CPU_LED_PIN = 16  # Pin controlling onboard NeoPixel
    CPU_LED_BASE_COLOR = (0, 64, 0)  # Base color for the NeoPixel (R, G, B)
    CPU_LED_BREATHE_TIME = 60  # Rate at which the onboard NeoPixel "breathes" (in milliseconds)

    # Button press threshold configuration
    LONG_PRESS_THRESHOLD = 10  # Threshold for a long press (in 100 ms ticks)
