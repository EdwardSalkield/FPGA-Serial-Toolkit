# Run File
# 	Describes the sequential operation of a circuit given in a circuit configuration file.


# Header
from communication import *
comm = Communicator('reduced_machine_cc.toml')

# Program to run

comm.send_pin('PS', 1)
comm.send_pin('KSP', 1)
comm.send_pin('KLC', 0)
comm.send_pin('KSC', 0)
comm.send_pin('WE', 0)
comm.send_pin('SS', 0)
comm.send_pin('KCC', 0)

comm.send_serial('TPR', [1,1,0,1,0,0,0,0,0,0, 0,0,0,0,0,0,0,0,0,0])
comm.send_serial('S', [0,0,0,0,0,0,0,0,0,0, 0,0,0,0, 0,0,0,0,0,0])

comm.run_osc('main', 50)

comm.save_history('run_file_output.pickle')
