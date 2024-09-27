from machine import mem32, Pin

# Poll and receive data from the I2C hardware.
# This class interacts with the I2C hardware via memory-mapped registers on the RP2040.
# Adapted from https://forums.raspberrypi.com/viewtopic.php?t=302978
# There is also memory-style code on the forum that hasn't been tested.

class I2CTarget:
    I2C0_BASE = 0x40044000  # Base address for I2C0
    I2C1_BASE = 0x40048000  # Base address for I2C1
    IO_BANK0_BASE = 0x40014000  # Base address for GPIO configuration
    
    # Memory operation modes
    mem_rw =  0x0000  # Read/Write mode
    mem_xor = 0x1000  # XOR mode
    mem_set = 0x2000  # Set bits mode
    mem_clr = 0x3000  # Clear bits mode
    
    # I2C register offsets
    IC_CON = 0x00
    IC_TAR = 0x04
    IC_SAR = 0x08
    IC_DATA_CMD = 0x10
    IC_RX_TL = 0x38
    IC_TX_TL = 0x3C
    IC_CLR_INTR = 0x40
    IC_ENABLE = 0x6C
    IC_STATUS = 0x70
    
    # Write to a specific I2C register using the specified memory operation method
    def write_reg(self, reg, data, method=0):
        mem32[self.i2c_base | method | reg] = data
        
    # Set specific bits in a register
    def set_reg(self, reg, data):
        self.write_reg(reg, data, method=self.mem_set)
        
    # Clear specific bits in a register
    def clr_reg(self, reg, data):
        self.write_reg(reg, data, method=self.mem_clr)
                
    def __init__(self, i2c_id=0, sda=0, scl=1, address=0x73):
        """
        Initialize the I2C target device.
        - i2c_id: 0 for I2C0, 1 for I2C1.
        - sda: GPIO pin for SDA (data).
        - scl: GPIO pin for SCL (clock).
        - address: 7-bit address of the I2C target device.
        """
        self.scl = scl
        self.sda = sda
        self.address = address
        self.i2c_id = i2c_id

        # Set base address based on I2C instance (I2C0 or I2C1)
        self.i2c_base = self.I2C0_BASE if i2c_id == 0 else self.I2C1_BASE
        
        # 1. Disable the I2C controller
        self.clr_reg(self.IC_ENABLE, 1)
        
        # 2. Set the I2C target address
        # Clear the address bits (bit 0-9) and set the new address
        self.clr_reg(self.IC_SAR, 0x1FF)
        self.set_reg(self.IC_SAR, self.address & 0x1FF)
        
        # 3. Configure the I2C control register for 7-bit addressing, target mode
        self.clr_reg(self.IC_CON, 0b01001001)
        
        # Configure the GPIO pins for SDA and SCL
        # Set SDA pin
        mem32[self.IO_BANK0_BASE | self.mem_clr | (4 + 8 * self.sda)] = 0x1F
        mem32[self.IO_BANK0_BASE | self.mem_set | (4 + 8 * self.sda)] = 3
        
        # Set SCL pin
        mem32[self.IO_BANK0_BASE | self.mem_clr | (4 + 8 * self.scl)] = 0x1F
        mem32[self.IO_BANK0_BASE | self.mem_set | (4 + 8 * self.scl)] = 3
        
        # 4. Enable the I2C controller
        self.set_reg(self.IC_ENABLE, 1)

    # Check if data is available in the receive FIFO
    def any(self):
        """
        Check if the I2C receive FIFO (buffer) is not empty.
        - Returns True if data is available, otherwise False.
        """
        status = mem32[self.i2c_base | self.IC_STATUS]
        # RFNE (Receive FIFO Not Empty) is bit 3 (mask 0x08)
        return bool(status & 0x08)
    
    # Block until data is available, then retrieve a byte from the receive FIFO.
    # Use the `any()` method to avoid blocking if no data is available.
    def get(self):
        """
        Retrieve a byte from the I2C receive FIFO. Will block until data is available.
        - Returns the received byte (0-255).
        """
        while not self.any():  # Wait until data is available
            pass
        return mem32[self.i2c_base | self.IC_DATA_CMD] & 0xFF  # Return only the lower 8 bits

# i2cmenutarget is a subclass of i2ctarget, used to handle I2C-driven menu requests.
# If integrated with a command handler, it passes menu options via I2C.
class I2CMenuTarget(I2CTarget):
    def menu(self, dummy1, dummy2):
        """
        Handle I2C input as a menu request.
        - Returns the 4-bit command encoded in the received I2C byte.
        - If the received byte doesn't match the expected command prefix (0xC0), returns dummy1.
        """
        c = self.get()  # Get the byte from the I2C bus
        if (c & 0xF0) != 0xC0:  # Check if the upper 4 bits match the expected command prefix
            return dummy1  # If not, return the first dummy parameter (likely to avoid changing the state)
        return c & 0x0F  # Return the lower 4 bits (command number)
