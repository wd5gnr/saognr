from machine import mem32,Pin

# Poll and receive from the I2C hardware
# adapted from https://forums.raspberrypi.com/viewtopic.php?t=302978
# there is also memory-style code there that I have not tested

class i2ctarget:
    I2C0_BASE = 0x40044000
    I2C1_BASE = 0x40048000
    IO_BANK0_BASE = 0x40014000
    
    mem_rw =  0x0000
    mem_xor = 0x1000
    mem_set = 0x2000
    mem_clr = 0x3000
    
    IC_CON = 0
    IC_TAR = 4
    IC_SAR = 8
    IC_DATA_CMD = 0x10 
    IC_RX_TL = 0x38
    IC_TX_TL = 0x3C
    IC_CLR_INTR = 0x40
    IC_ENABLE = 0x6c
    IC_STATUS = 0x70
    
    def write_reg(self, reg, data, method=0):
        mem32[ self.i2c_base | method | reg] = data
        
    def set_reg(self, reg, data):
        self.write_reg(reg, data, method=self.mem_set)
        
    def clr_reg(self, reg, data):
        self.write_reg(reg, data, method=self.mem_clr)
                
    def __init__(self, i2cID = 0, sda=0,  scl=1, address=0x73):
        self.scl = scl
        self.sda = sda
        self.address = address
        self.i2c_ID = i2cID
        if self.i2c_ID == 0:
            self.i2c_base = self.I2C0_BASE
        else:
            self.i2c_base = self.I2C1_BASE
        
        # 1 Disable DW_apb_i2c
        self.clr_reg(self.IC_ENABLE, 1)
        # 2 set address
        # clr bit 0 to 9
        # set address
        self.clr_reg(self.IC_SAR, 0x1ff)
        self.set_reg(self.IC_SAR, self.address &0x1ff)
        # 3 write IC_CON  7 bit, enable in target-only
        self.clr_reg(self.IC_CON, 0b01001001)
        # set SDA PIN
        mem32[ self.IO_BANK0_BASE | self.mem_clr |  ( 4 + 8 * self.sda) ] = 0x1f
        mem32[ self.IO_BANK0_BASE | self.mem_set |  ( 4 + 8 * self.sda) ] = 3
        # set SCL PIN
        mem32[ self.IO_BANK0_BASE | self.mem_clr |  ( 4 + 8 * self.scl) ] = 0x1f
        mem32[ self.IO_BANK0_BASE | self.mem_set |  ( 4 + 8 * self.scl) ] = 3
        # 4 enable i2c 
        self.set_reg(self.IC_ENABLE, 1)

# see if anything is available
    def any(self):
        # get IC_STATUS
        status = mem32[ self.i2c_base | self.IC_STATUS]
        # check RFNE receive fifio not empty
        if (status &  8) :
            return True
        return False
    
    # Get will block if nothing is there (use any() first if you don't want to block)
    # Note that the RP2040 hardware has a 16-element buffer for receive
    def get(self):
        while not self.any():
            pass
        return mem32[ self.i2c_base | self.IC_DATA_CMD] & 0xff


# If you want to feed a menu request from I2C, you can pass
# an i2cmenutarget reference instead of a normal menu
# If you don't want to use menu, call any() to see if anything is available
# then call get
class i2cmenutarget(i2ctarget):
    def menu(self,dummy1,dummy2):   # this lets me be passed to a cmd handler that normally uses the menu
        c=self.get()
        if (c&0xF0)!=0xc0:
            return dummy1    # ugh, some kind of phase error so try not to change anything
        return c&0xF

