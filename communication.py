# communication.py
#	Describes a class for communication with FPGA circuitry running the serial protocol, which can:
# 	 * Load circuit configuration files to communicate with the circuitry
#	 * Execute run files
#	 * Return the results

import serial
import toml, pickle
import os.path

# Circuit Config Class
#	Abstract representation of a circuit configuration file
#	Parses circuit config file at __init__
class _CircuitConfig:
	pi_board_mode = None
	constants = {}
	pin_inputs = {}
	pin_outputs = {}
	serial_inputs = {}
	serial_outputs = {}
	virtual_oscs = {}

	def __init__(self, circuit_config):
		# Replace constants within top level config construct and create serial object
		def instantiate_serials(config_dict, serial_class):
			if not isinstance(config_dict, dict):
				raise TypeError("config_dict of invalid type " + str(type(config_dict)) + ". Should be dict.")

			serial_objects = {}
			for interface, config in config_dict.items():
				class_arguments = {}
				for prop, key in config.items():
					if isinstance(key, str):
						# Separate val into fields
						keys = key.split('.')
						
						# Look up value
						lookup = self.constants
						for key in keys:
							lookup = lookup[key]

						# Create dict of looked-up values
						class_arguments[prop] = lookup

					elif isinstance(key, int):
						class_arguments[prop] = key

					else:
						raise TypeError("Invalid type at " + ".".join([interface, prop]) + " in circuit config. Is " + str(type(key)) + " , should be int, str")

				serial_objects[interface] = serial_class(**class_arguments)

			return serial_objects


		# Load configuration from file, replacing constants
		self.pi_board_mode = circuit_config['global']['pi_board_mode']
		serial.initialise(self.pi_board_mode)

		self.constants = circuit_config['constants']
		self.pin_inputs = instantiate_serials(circuit_config['pin_inputs'], serial.PinOut)
		self.pin_outputs = instantiate_serials(circuit_config['pin_outputs'], serial.PinIn)
		self.serial_inputs = instantiate_serials(circuit_config['serial_inputs'], serial.SerialOut)
		self.serial_outputs = instantiate_serials(circuit_config['serial_outputs'], serial.SerialIn)
		self.virtual_oscs = instantiate_serials(circuit_config['virtual_oscs'], serial.VirtualOsc)

		
	

# Communicator Class
#	Loads a circuit configuration file by path
#	Exposes functions to easily interact with the described circuit
class Communicator:
	config = None	# Circuit config object
	history = []

	def __init__(self, circuit_config_path):
		# Load configuration file and initialise circuitry
		if not os.path.isfile(circuit_config_path):
			raise ValueError("circuit_config_path " + str(circuit_config_path) + " does not exist!")
		# Parse circuit config and create circuit config object
		with open(circuit_config_path, 'r') as f:
			config = toml.load(f)
			self.config = _CircuitConfig(config)
		
	# Interaction functions
	#  Set output GPIO pin to a given state
	def send_pin(self, pin_name, value):
		self.config.pin_inputs[pin_name].output(value)

	#  Return the state of an input GPIO pin
	def receive_pin(self, pin_name):
		data = self.config.pin_outputs[pin_name].input()
		history.append(("pin", pin_name, data))
		return data

	#  Run output GPIO pin as clock for given number of cycles
	def run_pin(self, pin_name, cycles):
		self.config.pin_inputs[pin_name].run(cycles)

	#  Send serial signal over named serial interface
	def send_serial(self, bus_name, data):
		self.config.serial_inputs[bus_name].output(data)

	# Receive serial signal over named serial interface
	def receive_serial(self, bus_name):
		data = self.config.pin_outputs[bus_name].input()
		history.append(("serial", bus_name, data))
		return data

	# Run virtual oscilloscope given number of cycles
	def run_osc(self, osc_name, cycles):
		data = self.config.virtual_oscs[osc_name].run(cycles)
		history.append("osc", osc_name, data)
		return data

	#def run_oscs(self, osc_names, cycles):
	#	for cycle in cycles:

	# Return or save the current history
	def save_history(self, output_path=None):
		if file_path != None:
			with open(output_path, 'wb') as f:
				pickle.dump(self.history, f)
		
		return self.history
