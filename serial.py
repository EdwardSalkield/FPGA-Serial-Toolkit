# serial.py
# Describes classes for communicating using the serial protocol.

import RPi.GPIO as GPIO
import time

# Initialise global communications functions
def initialise(GPIO_MODE):
	GPIO.setwarnings(False)
	if GPIO_MODE == "BOARD":
		GPIO.setmode(GPIO.BOARD)
	elif GPIO_MODE == "BCM":
		GPIO.setmode(GPIO.BCM)
	else:
		return ValueError("Invalid mode: " + str(GPIO_MODE))



# General purpose single pin output interface
class PinOut:
	PIN = None

	def __init__(self, PIN, **kwargs):
		self.PIN = PIN
		GPIO.setup(PIN, GPIO.OUT)

	def output(self, value):
		GPIO.output(self.PIN, value)



# General purpose single pin input interface
class PinIn:
	PIN = None

	def __init__(self, PIN, **kwargs):
		self.PIN = PIN
		GPIO.setup(PIN, GPIO.IN)

	def input(self):
		return GPIO.output(self.PIN)



# General purpose serial interface
#	Initialises the appropriate constructs for FPGA serial communication.
class Serial:
	BUS_WIDTH = None
	PIN_CLK = None
	DELAY = None

	def __init__(self, BUS_WIDTH, PIN_CLK, DELAY, **kwargs):
		# Initialise class
		self.BUS_WIDTH = BUS_WIDTH
		self.PIN_CLK = PIN_CLK
		self.DELAY = DELAY

		# Set up clock pin
		GPIO.setup(PIN_CLK, GPIO.OUT)




# Serial data output
# 	Handles driving serial clock lines for the transferring of a list of bits
class SerialOut(Serial):
	PIN_DATA = None

	def __init__(self, BUS_WIDTH, PIN_CLK, PIN_DATA, DELAY=0.01, **kwargs):
		super().__init__( BUS_WIDTH, PIN_CLK, DELAY)
		self.PIN_DATA = PIN_DATA
		GPIO.setup(PIN_DATA, GPIO.OUT)


	def output(self, bus):
		if not isinstance(bus, list):
			raise TypeError("bus is not a list")
		if len(bus) != self.BUS_WIDTH:
			raise ValueError("bus is of incorrect length " + str(len(bus)) +
				", BUS_WIDTH = " + str(self.BUS_WIDTH))

		for bit in bus:
			GPIO.output(self.PIN_DATA, bit)
			GPIO.output(self.PIN_CLK, 1)
			time.sleep(self.DELAY/2)
			GPIO.output(self.PIN_CLK, 0)
			time.sleep(self.DELAY/2)



# Serial data input
# 	Handles driving serial clock lines and the storage of the inputted data
class SerialIn(Serial):
	PIN_DATA = None

	def __init__(self, BUS_WIDTH, PIN_CLK, PIN_DATA, DELAY=0.01, **kwargs):
		super().__init__( BUS_WIDTH, PIN_CLK, DELAY)
		self.PIN_DATA = PIN_DATA
		GPIO.setup(PIN_DATA, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


	def input(self):
		bus = []
		if not isinstance(bus, list):
			raise TypeError("bus is not a list")

		for i in range(self.BUS_WIDTH):
			GPIO.output(self.PIN_CLK, 1)
			time.sleep(self.DELAY/2)
			bus.append(GPIO.input(self.PIN_DATA))
			GPIO.output(self.PIN_CLK, 0)
			time.sleep(self.DELAY/2)

		return bus



# Virtual oscilloscope 
#	Allows for the inspection of certain bits within the circuitry
#	after each rising and falling clock edge.
class VirtualOsc(Serial):
	def __init__(self,  BUS_WIDTH, PIN_CLK, PIN_DATA, DELAY=0.01, **kwargs):
		super().__init__(BUS_WIDTH, PIN_CLK, DELAY)
		self.PIN_DATA = PIN_DATA
		GPIO.setup(PIN_DATA, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
	

	def run(self, cycles):
		data = [[] for i in range(self.BUS_WIDTH)]

		for cycle in range(cycles):
			for w_CLK in [1,0]:
				for i in range(self.BUS_WIDTH+1):
					# Send clock pulse
					for signal in [0,1]:
						GPIO.output(self.PIN_CLK, signal)
						time.sleep(self.DELAY/2)
					# Measure
					if i != 0:
						datum = GPIO.input(self.PIN_DATA)
						data[(i-1)%self.BUS_WIDTH].append(datum)
		return data

