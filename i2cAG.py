import Adafruit_GPIO as GPIO
import Adafruit_GPIO.FT232H as FT232H


FT232H.use_FT232H()
ft232h = FT232H.FT232H()



class i2cAG(object):

	def __init__(self, address=0x68, config=0):
		""" Default address for 6050 module is 0x68, external resistor can change this to 0x69
			Config
			0			Part awake, all sensors enabled, accel scaled to +/-2g, gyro scaled to +/- 250 degrees/s
			1			Part awake, all sensors enabled, accel scaled to +/-4g, gyro scaled to +/- 500 degrees/s
			2			Part awake, all sensors enabled, accel scaled to +/-8g, gyro scaled to +/- 1000 degrees/s
			3			Part awake, all sensors enabled, accel scaled to +/-16g, gyro scaled to +/- 2000 degrees/s
			4			Low power accel only mode, temp sensor and gyroscopes disable, accel scaled to +/-4g
		"""
		self.i2c = FT232H.I2CDevice(ft232h, address)
		if config == 0:
			self.setWake()
			self.setScale(mode='ACC',scale=0)
			self.setScale(mode='GYR',scale=0)
		elif config == 1:
			self.setWake()
			self.setScale(mode='ACC',scale=1)
			self.setScale(mode='GYR',scale=1)				
		elif config == 2:
			self.setWake()
			self.setScale(mode='ACC',scale=2)
			self.setScale(mode='GYR',scale=2)	
		elif config == 3:
			self.setWake()
			self.setScale(mode='ACC',scale=3)
			self.setScale(mode='GYR',scale=3)				
		elif config == 4:
			self.setWake()
			self.setScale(mode='ACC',scale=1)	
			self.setTempDisable()
			self.setGYRStandby(axis='X')
			self.setGYRStandby(axis='Y')
			self.setGYRStandby(axis='Z')
		
	def read(self, register): #good
		""" Reads 8 bits from the given register
		"""
		currentVal = self.i2c.readU8(register)
		return currentVal

	def write(self, register, value):  #good
		""" Writes a value to an 8 bit register
		"""
		self.i2c.write8(register, value)
		
	def softReset(self):  #good
		""" Performs a part reset, clearing all registers to their default values.
			0x6B[7] = 1 Reset
		"""
		currentVal = self.dec2BinList(self.read(0x6b))
		currentVal[7] = 1
		currentVal = self.binList2Dec(currentVal)
		self.write(0x6b, currentVal)
		
	def setWake(self, wakeBit=0): #good
		""" Wake bit 0x6B[6] = 0 normal operation 
							 = 1 Device is in low power sleep mode
		"""
		currentVal = self.dec2BinList(self.read(0x6b))
		currentVal[6] = wakeBit
		currentVal = self.binList2Dec(currentVal)
		self.write(0x6b, currentVal)	
		
	def setCycle(self, cycleBit=0):
		""" Cycle bit 0x6B[5] = 0 normal operation 
							  = 1 When sleep = 0, device enters Cycle mode. Cycles between sleep and wake, taking one sample 
							  based on time defined by LP_WAKE_CTRL register 0x6C
		"""
		currentVal = self.dec2BinList(self.read(0x6b))
		currentVal[5] = cycleBit
		currentVal = self.binList2Dec(currentVal)
		self.write(0x6b, currentVal)

	def setTempDisable(self, bit=1):
		""" Cycle bit 0x6B[3] = 0 normal operation 
							  = 1 disables the internal temperature sensor
		"""
		currentVal = self.dec2BinList(self.read(0x6b))
		currentVal[3] = bit
		currentVal = self.binList2Dec(currentVal)
		self.write(0x6b, currentVal)		

	def setClock(self, clock=0):
		""" CLK Sel 0x6B[2:0] 
			Setting
			0		Internal 8MHz Clock		*Default on power up
			1		PLL with X axis gyroscope reference
			2		PLL with Y axis gyroscope reference
			3		PLL with Z axis gyroscope reference
			4		PLL with external 32.768kHz reference
			5		PLL with external 19.2MHz reference
			6		Reserved
			7		Stops the clock and keeps the timing generator in reset
			
			Documentatoion recommends using either 1,2,or 3
		"""
		currentVal = self.i2c.readU8(0x6b)
		currentVal = currentVal|(clock)
		self.i2c.write8(0x6b, currentVal)	
		
	def setACCStandby(self, axis='X',mode=1):
		""" Cycle bit 0x6C[5:3] = 0 Normal operation 
							    = 1 Disables the given accelerometer 
		"""
		currentVal = self.dec2BinList(self.read(0x6C))
		if axis.upper() == 'X':
			reg = 5
		elif axis.upper() == 'Y':
			reg = 4
		elif axis.upper() == 'Z':
			reg = 3
		else:
			return False
		currentVal[reg] = mode
		currentVal = self.binList2Dec(currentVal)
		self.write(0x6C, currentVal)	

	def setGYRStandby(self, axis='X',mode=1):
		""" Cycle bit 0x6C[5:3] = 0 Normal operation 
							    = 1 Disables the given accelerometer 
		"""
		currentVal = self.dec2BinList(self.read(0x6C))
		if axis.upper() == 'X':
			reg = 2
		elif axis.upper() == 'Y':
			reg = 1
		elif axis.upper() == 'Z':
			reg = 0
		else:
			return False
		currentVal[reg] = mode
		currentVal = self.binList2Dec(currentVal)
		self.write(0x6C, currentVal)		
		
	def setWakecCtrl(self, frequency=0):
		""" CLK Sel 0x6C[7:6] Sets the wake cycle refresh time
			Setting
			0		1.25 Hz
			1		5 Hz
			2		20 Hz
			3		40 Hz

			Low power accelerometer only example
			1) Set CYCLE bit to 1
			2) Set SLEEP bit to 0
			3) Set TEMP_DIS bit to 1
			4) Set STBY_XG, STBY_YG, STBY_ZG bits to 1

			
		"""
		currentVal = self.read(0x6b)
		currentVal = currentVal|(clock)
		self.i2c.write8(0x6b, currentVal)		

	def setScale(self, mode='ACC', scale=0):
		"""	Mode = 'ACC' or 'GYR'
			ACC  Scale
			0 	+/- 2g
			1 	+/- 4g
			2 	+/- 8g
			3 	+/- 16g
			
			Gyro Scale
			0 	+/- 250 deg/s
			1 	+/- 500 deg/s
			2 	+/- 1000 deg/s
			3 	+/- 2000 deg/s

		"""
		if mode.upper() == 'ACC':
			reg = 0x1C
		elif mode.upper() == 'GYR':
			reg = 0x1B		
		else:
			return False
		currentVal = self.read(reg)
		currentVal = self.dec2BinList(currentVal)
		scale = self.dec2BinList(value=scale,bits=2)
		currentVal[3] = scale[0]
		currentVal[4] = scale[1]
		currentVal = self.binList2Dec(currentVal)
		self.write(reg, currentVal)	
		
	def getScale(self, mode='ACC'):	#good
		"""	Mode = 'ACC' or 'GYR'
			ACC  Scale
			0 	+/- 2g
			1 	+/- 4g
			2 	+/- 8g
			3 	+/- 16g
			
			Gyro Scale
			0 	+/- 250 deg/s
			1 	+/- 500 deg/s
			2 	+/- 1000 deg/s
			3 	+/- 2000 deg/s

		"""
		if mode.upper() == 'ACC':
			reg = 0x1C
		elif mode.upper() == 'GYR':
			reg = 0x1B		
		else:
			return False
		currentVal = self.read(reg)
		currentVal = self.dec2BinList(currentVal)
		scaleSetting = (currentVal[4]*2) + (currentVal[3]*1) 
		if mode.upper() == 'ACC':
			scale = 2**(scaleSetting+1) 
		elif mode.upper() == 'GYR':
			scale = (2**(scaleSetting+1))*125
		else:
			return False
		return scale,scaleSetting

	def getACC(self, axis='X'):
		""" Returns the raw ADC value (2s compliment) as well as the scaled acceleration value
		
		"""
		scale = self.getScale(mode='ACC')[0]
		if axis.upper() == 'X':
			reg = 0x3B
		elif axis.upper() == 'Y':
			reg = 0x3D
		elif axis.upper() == 'Z':
			reg = 0x3F
		else:
			return False
		acc_H = self.read(reg)
		acc_L = self.read(reg+1)
		accRaw = self.twos_comp(val=(acc_H*256 + acc_L),bits=16)
		return scale*(accRaw/float(2**15)), accRaw
		
	def getGYR(self, axis='X'):
		""" Returns the raw ADC value (2s compliment) as well as the scaled gyroscope value
		
		"""
		scale = self.getScale(mode='GYR')[0]
		if axis.upper() == 'X':
			reg = 0x43
		elif axis.upper() == 'Y':
			reg = 0x45
		elif axis.upper() == 'Z':
			reg = 0x47
		else:
			return False
		gyr_H = self.read(reg)
		gyr_L = self.read(reg+1)
		gyrRaw = self.twos_comp(val=(gyr_H*256 + gyr_L),bits=16)
		return scale*(gyrRaw/float(2**15)), gyrRaw		
		
	def getTEMP(self):
		""" Returns the raw ADC temperature, C temp, and F temp
		
		"""
		temp_H = self.read(0x41)
		temp_L = self.read(0x42)
		temp = self.twos_comp(val = (temp_H*256 + temp_L),bits=16)
		tempC = (temp/340.0)+36.53
		tempF = tempC*(9.0/5) + 32
		return tempC,tempF ,temp 
				
		
	def whoAmI(self): #good
		""" Returns the i2c address
		"""
		return self.read(0x75)	
		
	def dec2BinList(self, value=0, bits=8):
		""" Returns a binary list of length "bits"
		"""
		binList = [int(x) for x in bin(value)[2:]]
		padLength = bits - len(binList)
		binList.reverse()
		for x in range(padLength):
			binList.append(0)
		return binList
	
	def binList2Dec(self, list=[]):
		""" Returns a decimal value when given a binary list
		"""
		value = 0
		for x in range(len(list)):
			value = value + list[x]*(2**x)
		return value

	def twos_comp(self,val=0, bits=0):
		""" Returns 2s compliment of given value, found online 
		"""
		if (val & (1 << (bits - 1))) != 0: # if sign bit is set e.g., 8bit: 128-255
			val = val - (1 << bits)        # compute negative value
		return val 
		





		