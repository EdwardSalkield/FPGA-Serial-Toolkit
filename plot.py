# plot.py
#       Renders a run_file_output file for graphing purposes

import matplotlib.pyplot as plt

from random import randint
import pickle, toml
import argparse
import sys, os


parser = argparse.ArgumentParser(description="Communicate with the Mark 1 FPGA and plot data")
parser.add_argument("setup_path")
parser.add_argument("data_path")
args = parser.parse_args()

if not os.path.isfile(args.setup_path):
        raise ValueError("error: path " + args.setup_path + " does not exist!")
if not os.path.isfile(args.data_path):
        raise ValueError("error: path " + args.output_path + " does not exist!")


with open(args.setup_path, 'r') as f:
	setup = toml.loads(f.read())

with open(args.data_path, 'rb') as f:
	data = pickle.load(f)
SUB_CYCLES = setup["SUB_CYCLES"]
if SUB_CYCLES >= 1:
        data2 = [dlist[1::2*SUB_CYCLES] for dlist in data]
else:
        data2 = data

# Label the data
labels = setup["OSC"]

f = plt.figure()

for i in range(setup["n_OSC"]):
        plt.subplot(setup["n_OSC"], 1, i+1)
        plt.plot(data2[i], drawstyle='steps-pre')
        l = plt.ylabel(labels[i])
        l.set_rotation(0)
        if not (0 in data2[i] and 1 in data2[i]):
            plt.axhline(y=0.5, color='k')
        plt.yticks([], [])
        axes = plt.gca()
        axes.set_ylim([0,1.1])


plt.show()

