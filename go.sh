#!/bin/bash

# go.sh
#	A shell script which:
#	 * loads a circuit config file onto a Raspberry Pi
#	 * loads loading a run file onto the RPi
#	 * executes the run file on the RPi
#	 * returns the results from the RPi
#	 * renders the results locally on the machine

# Test for correct number of command line arguments
if [ $# -ne 5 ]; then
	echo "Usage:  $0 SSH_TARGET TARGET_DIR CIRCUIT_CONFIG RUN_FILE OUTPUT_FILE"
	echo "	SSH_TARGET 	- The specified SSH destination."
	echo "	TARGET_DIR 	- The target directory that the toolkit resides in on the SSH_TARGET."
	echo "		    	  Can be relative to the home directory of the SSH_TARGET user."
	echo "	CIRCUIT_CONFIG 	- The path to the circuit configuration file on the local machine."
	echo "	RUN_FILE	- The path to the run file on the local machine."
	echo "	OUTPUT_FILE	- The name of the output file to be generated on the RPi."
	echo "			  This can be specified in the RUN_FILE."
	exit 1
fi

# Parse command line arguments
SSH_TARGET=$1
TARGET_DIR=$2
CIRCUIT_CONFIG=$3
RUN_FILE=$4
OUTPUT_FILE=$5

scp $CIRCUIT_CONFIG $RUN_FILE $SSH_TARGET:$TARGET_DIR &&
ssh $SSH_TARGET "cd $TARGET_DIR && python3 $RUN_FILE" &&
scp $SSH_TARGET:$TARGET_DIR$OUTPUT_FILE . &&
python3 plot.py $CIRCUIT_CONFIG $OUTPUT_FILE
exit 0
