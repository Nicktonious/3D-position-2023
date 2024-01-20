import time
import struct

__version__ = '0.0.6'

CHIP_ID = 0xEA
I2C_ADDR = 0x68
I2C_ADDR_ALT = 0x69
ICM20948_BANK_SEL = 0x7f

ICM20948_I2C_MST_ODR_CONFIG = 0x00
ICM20948_I2C_MST_CTRL = 0x01
ICM20948_I2C_MST_DELAY_CTRL = 0x02
ICM20948_I2C_SLV0_ADDR = 0x03
ICM20948_I2C_SLV0_REG = 0x04
ICM20948_I2C_SLV0_CTRL = 0x05
ICM20948_I2C_SLV0_DO = 0x06
ICM20948_EXT_SLV_SENS_DATA_00 = 0x3B

ICM20948_GYRO_SMPLRT_DIV = 0x00
ICM20948_GYRO_CONFIG_1 = 0x01
ICM20948_GYRO_CONFIG_2 = 0x02

# Bank 0
ICM20948_WHO_AM_I = 0x00
ICM20948_USER_CTRL = 0x03
ICM20948_LP_CONFIG = 0x05
ICM20948_PWR_MGMT_1 = 0x06
ICM20948_PWR_MGMT_2 = 0x07
ICM20948_INT_PIN_CFG = 0x0F

ICM20948_ACCEL_SMPLRT_DIV_1 = 0x10
ICM20948_ACCEL_SMPLRT_DIV_2 = 0x11
ICM20948_ACCEL_INTEL_CTRL = 0x12
ICM20948_ACCEL_WOM_THR = 0x13
ICM20948_ACCEL_CONFIG = 0x14
ICM20948_ACCEL_XOUT_H = 0x2D
ICM20948_GRYO_XOUT_H = 0x33

ICM20948_TEMP_OUT_H = 0x39
ICM20948_TEMP_OUT_L = 0x3A

# Offset and sensitivity - defined in electrical characteristics, and TEMP_OUT_H/L of datasheet
ICM20948_TEMPERATURE_DEGREES_OFFSET = 21
ICM20948_TEMPERATURE_SENSITIVITY = 333.87
ICM20948_ROOM_TEMP_OFFSET = 21

ODR_ALIGN_EN = 0x09

AK09916_I2C_ADDR = 0x0c
AK09916_CHIP_ID = 0x09
AK09916_WIA = 0x01
AK09916_ST1 = 0x10
AK09916_ST1_DOR = 0b00000010   # Data overflow bit
AK09916_ST1_DRDY = 0b00000001  # Data self.ready bit
AK09916_HXL = 0x11
AK09916_ST2 = 0x18
AK09916_ST2_HOFL = 0b00001000  # Magnetic sensor overflow bit
AK09916_CNTL2 = 0x31
AK09916_CNTL2_MODE = 0b00001111
AK09916_CNTL2_MODE_OFF = 0
AK09916_CNTL2_MODE_SINGLE = 1
AK09916_CNTL2_MODE_CONT1 = 2
AK09916_CNTL2_MODE_CONT2 = 4
AK09916_CNTL2_MODE_CONT3 = 6
AK09916_CNTL2_MODE_CONT4 = 8
AK09916_CNTL2_MODE_TEST = 16
AK09916_CNTL3 = 0x32


class ICM20948:
    def write(self, reg, value):
        """Write byte to the sensor."""
        self._bus.write_byte_data(self._addr, reg, value)
        time.sleep(0.0001)

    def read(self, reg):
        """Read byte from the sensor."""
        return self._bus.read_byte_data(self._addr, reg)

    def trigger_mag_io(self):
        user = self.read(ICM20948_USER_CTRL)
        self.write(ICM20948_USER_CTRL, user | 0x20)
        time.sleep(0.005)
        self.write(ICM20948_USER_CTRL, user)

    def read_bytes(self, reg, length=1):
        """Read byte(s) from the sensor."""
        return self._bus.read_i2c_block_data(self._addr, reg, length)

    def bank(self, value):
        """Switch register self.bank."""
        if not self._bank == value:
            self.write(ICM20948_BANK_SEL, value << 4)
            self._bank = value

    def mag_write(self, reg, value):
        """Write a byte to the slave magnetometer."""
        self.bank(3)
        self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR)  # Write one byte
        self.write(ICM20948_I2C_SLV0_REG, reg)
        self.write(ICM20948_I2C_SLV0_DO, value)
        self.bank(0)
        self.trigger_mag_io()

    def mag_read(self, reg):
        """Read a byte from the slave magnetometer."""
        self.bank(3)
        self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR | 0x80)
        self.write(ICM20948_I2C_SLV0_REG, reg)
        self.write(ICM20948_I2C_SLV0_DO, 0xff)
        self.write(ICM20948_I2C_SLV0_CTRL, 0x80 | 1)  # Read 1 byte

        self.bank(0)
        self.trigger_mag_io()

        return self.read(ICM20948_EXT_SLV_SENS_DATA_00)

    def mag_read_bytes(self, reg, length=1):
        """Read up to 24 bytes from the slave magnetometer."""
        self.bank(3)
        self.write(ICM20948_I2C_SLV0_CTRL, 0x80 | 0x08 | length)
        self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR | 0x80)
        self.write(ICM20948_I2C_SLV0_REG, reg)
        self.write(ICM20948_I2C_SLV0_DO, 0xff)
        self.bank(0)
        self.trigger_mag_io()

        return self.read_bytes(ICM20948_EXT_SLV_SENS_DATA_00, length)
        """Read up to 24 bytes from the slave magnetometer."""
        self.bank(3)
        self.write(ICM20948_I2C_SLV0_ADDR, AK09916_I2C_ADDR | 0x80) # переключить 7 бит в режим чения
        self.write(ICM20948_I2C_SLV0_REG, reg)
        self.write(ICM20948_I2C_SLV0_DO, 0xff) # не нужна
        self.write(ICM20948_I2C_SLV0_CTRL, 0x80 | (0xF & length)) # считать length байт, но не больше 15ти
        time.sleep(0.005)
        self.bank(0)
        # self.trigger_mag_io()

        return self.read_bytes(ICM20948_EXT_SLV_SENS_DATA_00, length)

    def magnetometer_ready(self):
        """Check the magnetometer status self.ready bit."""
        return self.mag_read(AK09916_ST1) & 0x01

    def mag_reset(self):
        self.bank(3)
        self.mag_write(AK09916_CNTL3, 0b01)

    def i2c_master_reset(self):
        self.bank(0)
        temp = self.read(ICM20948_USER_CTRL)
        self.write(ICM20948_USER_CTRL, temp | 0b10) # |0x02
        time.sleep(0.1)
    
    def i2c_master_enable(self):
        # Master I2C enable
        self.bank(0)
        temp = self.read(ICM20948_USER_CTRL)
        self.write(ICM20948_USER_CTRL, temp | 0x20)  # С этой строкой можно удалить trigger_io
        time.sleep(0.01)
        # Master clock set | 0x07 - 400kHz, page 68
        self.bank(3)
        self.write(ICM20948_I2C_MST_CTRL, 0b111)   #0x7
        time.sleep(0.01)
        self.bank(0)
        self.write(ICM20948_LP_CONFIG, 0b00010000)
        time.sleep(0.01)
        self.bank(3)
        # I2C_MST_ODR_CONFIG: 1.1kHz, page 80
        self.write(ICM20948_I2C_MST_ODR_CONFIG, 0b11)   
        time.sleep(0.01)

    def resetIMU(self):
        # Включаем ресет и ждём
        self.write(ICM20948_PWR_MGMT_1, 0x80)
        time.sleep(0.01)
        # Выбираем наиболее подходящий цикл процессора
        self.write(ICM20948_PWR_MGMT_1, 0x01)
        # Включаем все оси акселерометра и гироскопа
        self.write(ICM20948_PWR_MGMT_2, 0x00)

    def setupICM(self):
        self.bank(0)
        if not self.read(ICM20948_WHO_AM_I) == CHIP_ID:
            raise RuntimeError("Unable to find ICM20948")
        self.resetIMU()

        self.bank(2)
        # вкл выравнивание
        self.write(ODR_ALIGN_EN, 0x01)        
        # установка ODR и dlpf гиро - стр 59
        self.write(ICM20948_GYRO_SMPLRT_DIV, 0x15) # 50Hz = (1125 / (1+21))
        self.write(ICM20948_GYRO_CONFIG_1, 0x58|0x02|0x01) # 500dps, GYRO_DLPFCFG = 7 dlpf on
        # установка ODR и dlpf акселерометра - стр 63
        self.write(ICM20948_ACCEL_SMPLRT_DIV_1, 0x00) # Страший байт - пустой
        self.write(ICM20948_ACCEL_SMPLRT_DIV_2, 0x15) # Младший байт - 50Hz = (1125 / (1+21))
        self.write(ICM20948_ACCEL_CONFIG, 0x18|0x00|0x01) #2g, ACCEL_DLPFCFG = 3, dlpf on

    def setupAK(self):
        self.bank(0)
        self.write(ICM20948_INT_PIN_CFG, 0x30) # Disable interupt bypass

        # Ресетим мастера I2C
        self.i2c_master_reset()
        time.sleep(0.1)
        self.i2c_master_enable()
        time.sleep(0.05)

        # mag reset
        self.mag_reset()
        time.sleep(0.1)
        self.trigger_mag_io()
        print(str(bin(self.read(ICM20948_USER_CTRL))))
        mag_id = self.mag_read(AK09916_WIA)
        print(mag_id) 
        if not mag_id == AK09916_CHIP_ID:
            raise RuntimeError("Unable to find AK09916")

        self.write(ICM20948_LP_CONFIG, 0x10) # работаем по циклу гироскопа

        
        # set mode
        self.mag_write(AK09916_CNTL2, AK09916_CNTL2_MODE_CONT3)
        time.sleep(0.0001)




        

    # SPARKFUN  

    def i2cMasterPassthrough(self, passthrough):
        """ 
            Enables or disables I2C Master Passthrough

            :return: Returns true if the setting write was successful, otherwise False.
            :rtype: bool

        """

        # Read the AGB0_REG_INT_PIN_CONFIG, store in local variable "register"
        self.bank(0)
        register = self.read(ICM20948_INT_PIN_CFG)

        # Set/clear the BYPASS_EN bit [1] as needed
        if passthrough:
            register |= (1<<1) # set bit
        else:
            register &= ~(1<<1) # clear bit

        # Write register
        self.bank(0)
        return self.write(ICM20948_INT_PIN_CFG, register)	
    
    def i2cMasterEnable(self, enable):      
        """ 
            Enables or disables I2C Master

            :return: Returns true if the setting write was successful, otherwise False.
            :rtype: bool

        """

        self.i2cMasterPassthrough(False) # Disable BYPASS_EN

        # Setup Master Clock speed as 345.6 kHz, and NSP (aka next slave read) to "stop between reads"
        # Read the AGB3_REG_I2C_MST_CTRL, store in local variable "register"
        self.bank(3)
        register = self.read(ICM20948_I2C_MST_CTRL)

        register &= ~(0x0F) # clear bits for master clock [3:0]
        register |= (0x07) # set bits for master clock [3:0], 0x07 corresponds to 345.6 kHz, good for up to 400 kHz
        register |= (1<<4) # set bit [4] for NSR (next slave read). 0 = restart between reads. 1 = stop between reads.

        # Write register
        self.bank(3)
        self.write(ICM20948_I2C_MST_CTRL, register)

        # enable/disable Master I2C
        # Read the AGB0_REG_USER_CTRL, store in local variable "register"
        self.bank(0)
        register = self.read(ICM20948_I2C_MST_CTRL)

        # Set/clear the I2C_MST_EN bit [5] as needed
        if enable:
            register |= (1<<5) # set bit
        else:
            register &= ~(1<<5) # clear bit

        # Write register
        self.bank(0)
        return self.write(ICM20948_USER_CTRL, register)
    # /SPARKFUN
    def read_magnetometer_data(self, timeout=1.0):
        # t_start = time.time()
        # while not self.magnetometer_ready():
        #     if time.time() - t_start > timeout:
        #         raise RuntimeError("Timeout waiting for Magnetometer Ready")
        #     time.sleep(0.00001)

        data = self.mag_read_bytes(AK09916_HXL, 8)

        # Read ST2 to confirm self.read finished,
        # needed for continuous modes
        # self.mag_read(AK09916_ST2)

        x, y, z, _ = struct.unpack("<hhhh", bytearray(data))

        # Scale for magnetic flux density "uT"
        # from section 3.3 of the datasheet
        # This value is constant
        x *= 0.15
        y *= 0.15
        z *= 0.15

        return x, y, z

    def read_accelerometer_gyro_data(self):
        self.bank(0)
        data = self.read_bytes(ICM20948_ACCEL_XOUT_H, 12)

        ax, ay, az, gx, gy, gz = struct.unpack(">hhhhhh", bytearray(data))

        self.bank(2)

        # Read accelerometer full scale range and
        # use it to compensate the self.reading to gs
        scale = (self.read(ICM20948_ACCEL_CONFIG) & 0x06) >> 1

        # scale ranges from section 3.2 of the datasheet
        gs = [16384.0, 8192.0, 4096.0, 2048.0][scale]

        ax /= gs
        ay /= gs
        az /= gs

        # Read back the degrees per second rate and
        # use it to compensate the self.reading to dps
        scale = (self.read(ICM20948_GYRO_CONFIG_1) & 0x06) >> 1

        # scale ranges from section 3.1 of the datasheet
        dps = [131, 65.5, 32.8, 16.4][scale]

        gx /= dps
        gy /= dps
        gz /= dps

        return ax, ay, az, gx, gy, gz

    def set_accelerometer_sample_rate(self, rate=50):
        """Set the accelerometer sample rate in Hz."""
        self.bank(2)
        # 125Hz - 1.125 kHz / (1 + rate)
        rate = int((1125.0 / rate) - 1)
        # TODO maybe use struct to pack and then write_bytes
        self.write(ICM20948_ACCEL_SMPLRT_DIV_1, (rate >> 8) & 0xff)
        self.write(ICM20948_ACCEL_SMPLRT_DIV_2, rate & 0xff)

    def set_accelerometer_full_scale(self, scale=2):
        """Set the accelerometer fulls cale range to +- the supplied value."""
        self.bank(2)
        value = self.read(ICM20948_ACCEL_CONFIG) & 0b11111001
        value |= {2: 0b00, 4: 0b01, 8: 0b10, 16: 0b11}[scale] << 1
        self.write(ICM20948_ACCEL_CONFIG, value)

    def set_accelerometer_low_pass(self, enabled=True, mode=5):
        """Configure the accelerometer low pass filter."""
        self.bank(2)
        value = self.read(ICM20948_ACCEL_CONFIG) & 0b10001110
        if enabled:
            value |= 0b1
        value |= (mode & 0x07) << 4
        self.write(ICM20948_ACCEL_CONFIG, value)

    def set_gyro_sample_rate(self, rate=50):
        """Set the gyro sample rate in Hz."""
        self.bank(2)
        # 100Hz sample rate - 1.1 kHz / (1 + rate)
        rate = int((1100.0 / rate) - 1)
        self.write(ICM20948_GYRO_SMPLRT_DIV, rate)

    def set_gyro_full_scale(self, scale=500):
        """Set the gyro full scale range to +- supplied value."""
        self.bank(2)
        value = self.read(ICM20948_GYRO_CONFIG_1) & 0b11111001
        value |= {250: 0b00, 500: 0b01, 1000: 0b10, 2000: 0b11}[scale] << 1
        self.write(ICM20948_GYRO_CONFIG_1, value)

    def set_gyro_low_pass(self, enabled=True, mode=5):
        """Configure the gyro low pass filter."""
        self.bank(2)
        value = self.read(ICM20948_GYRO_CONFIG_1) & 0b10001110
        if enabled:
            value |= 0b1
        value |= (mode & 0x07) << 4
        self.write(ICM20948_GYRO_CONFIG_1, value)

    def read_temperature(self):
        """Property to read the current IMU temperature"""
        # PWR_MGMT_1 defaults to leave temperature enabled
        self.bank(0)
        temp_raw_bytes = self.read_bytes(ICM20948_TEMP_OUT_H, 2)
        temp_raw = struct.unpack('>h', bytearray(temp_raw_bytes))[0]
        temperature_deg_c = ((temp_raw - ICM20948_ROOM_TEMP_OFFSET) / ICM20948_TEMPERATURE_SENSITIVITY) + ICM20948_TEMPERATURE_DEGREES_OFFSET
        return temperature_deg_c

    def __init__(self, i2c_addr=I2C_ADDR, i2c_bus=None):
        self._bank = -1
        self._addr = i2c_addr

        if i2c_bus is None:
            from smbus import SMBus
            self._bus = SMBus(1)
        else:
            self._bus = i2c_bus

        self.setupICM() # Вынес в отдельную функцию, чтобы не путать что к чему относится

        self.setupAK()
        # self.write(ICM20948_I2C_MST_CTRL, 0x4D)
        # self.write(ICM20948_I2C_MST_DELAY_CTRL, 0x01)
        

        





if __name__ == "__main__":
    imu = ICM20948()

    while True:
        x, y, z = imu.read_magnetometer_data()
        ax, ay, az, gx, gy, gz = imu.read_accelerometer_gyro_data()

        print("""
Accel: {:05.2f} {:05.2f} {:05.2f}
Gyro:  {:05.2f} {:05.2f} {:05.2f}
Mag:   {:05.2f} {:05.2f} {:05.2f}""".format(
            ax, ay, az, gx, gy, gz, x, y, z
        ))

        time.sleep(0.25)
