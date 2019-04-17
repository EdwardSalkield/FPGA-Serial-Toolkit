# plot.py
#       Renders a run_file_output file for graphing purposes

import matplotlib.pyplot as plt

from random import randint
import pickle, toml
import argparse
import sys, os


# Parse command line arguments
parser = argparse.ArgumentParser(description="Communicate with the Mark 1 FPGA and plot data")
parser.add_argument("CIRCUIT_CONFIG")
parser.add_argument("RUN_FILE_OUTPUT")
args = parser.parse_args()


# Check CIRCUIT_CONFIG and RUN_FILE_OUTPUT exist
if not os.path.isfile(args.CIRCUIT_CONFIG):
        raise ValueError("error: path " + args.CIRCUIT_CONFIG + " does not exist!")
if not os.path.isfile(args.RUN_FILE_OUTPUT):
        raise ValueError("error: path " + args.RUN_FILE_OUTPUT + " does not exist!")

with open(args.CIRCUIT_CONFIG, 'r') as f:
	CIRCUIT_CONFIG = toml.load(f)

with open(args.RUN_FILE_OUTPUT, 'rb') as f:
	output = pickle.load(f)


# Extract labelling data from RUN_FILE_OUTPUT
osc_labels = {}

for osc, d in CIRCUIT_CONFIG['virtual_oscs'].items():
    if not len(d['BUS_LABELS']) == d['BUS_WIDTH']:
            raise ValueError("Mismatch in BUS_LABELS and BUS_WIDTH for virtual osc " + str(osc))
    osc_labels[osc] = d['BUS_LABELS']


def display_pin(name, data):
        print("Pin: " + name)
        print(str(data))


def display_serial(name, data):
        print("Serial: " + name)
        print(str(data))



def display_osc(name, data, n):
        labels = osc_labels[name]

        # Extract SUB_CYCLES data and apply it
        # i.e. how many subcycles of the clock equals one "true" cycle
        SUB_CYCLES = CIRCUIT_CONFIG["constants"]["SUB_CYCLES"]
        if SUB_CYCLES >= 1:
                data2 = [dlist[1::2*SUB_CYCLES] for dlist in data]
        else:
                data2 = data


        f = plt.figure(n)
        f.suptitle(name)

        for i in range(len(labels)):
                plt.subplot(len(labels), 1, i+1)
                plt.plot(data2[i], drawstyle='steps-pre')
                l = plt.ylabel(labels[i])
                l.set_rotation(0)
                if not (0 in data2[i] and 1 in data2[i]):
                    plt.axhline(y=0.5, color='k')
                plt.yticks([], [])
                axes = plt.gca()
                axes.set_ylim([0,1.1])


# Display outputted data
n_figs = 1
for (data_type, name, data) in output:
        if data_type == 'pin':
                display_pin(name, data)
        elif data_type == 'serial':
                display_serial(name, data)
        elif data_type == 'osc':
                display_osc(name, data, n_figs)
                n_figs += 1


plt.show()
