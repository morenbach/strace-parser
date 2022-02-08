from importlib.resources import read_text

import pytest

import tests.data
from strace_parser.parser import get_parser
from strace_parser.json_transformer import to_json


import os
from time import sleep
from subprocess import Popen
from pexpect import pxssh
import pexpect
import argparse
from shutil import copy2
import psutil

parser = argparse.ArgumentParser(description='Syscall validation script')
parser.add_argument('--strace', help='directory of strace logs', type=str)
parser.add_argument('--vmi', help='directory of vmi syscalls logs', type=str)

strace_syscall_histogram = dict()
our_syscall_histogram = dict()

def parse_strace_file(path):
    global strace_syscall_histogram
    with open(path) as fp:  
        line = fp.readline()
        while line:
            val = get_parser().parse(line)
            j = to_json(val)
            #print(j[0]['name'])
            syscall_name = j[0]['name']
            if (syscall_name in strace_syscall_histogram):
                strace_syscall_histogram[syscall_name] += 1;
            else:
                strace_syscall_histogram[syscall_name] = 1;

            line = fp.readline()            


def parse_our_output(path):
    global our_syscall_histogram
    with open(path) as fp:
        line = fp.readline()
        while line:
            # our format will simply be name of the syscall
            syscall_name = line.replace(" ", "").replace("\n", "")
            #print(syscall_name)
            if (syscall_name in our_syscall_histogram):
                our_syscall_histogram[syscall_name] += 1;
            else:
                our_syscall_histogram[syscall_name] = 1;

            line = fp.readline()

def main():
    global strace_syscall_histogram
    global our_syscall_histogram

    args = parser.parse_args()
    for the_file in os.listdir(args.strace):        
        strace_file_path = os.path.join(args.strace, the_file)
        temp=the_file.split(".",1)[0]
        idx = int(temp[7:len(temp)])
        vmi_file = 'vmi_%d.txt' % (idx)
        vmi_file_path = os.path.join(args.vmi, vmi_file)
        print(the_file + " vs: " + vmi_file)

        wrong_idx = 1
        with open(strace_file_path) as strace_fp:  
            with open(vmi_file_path) as vmi_fp:  
                strace_line = strace_fp.readline()
                our_syscall_name = ""
                while (our_syscall_name != "execve"):
                    our_line = vmi_fp.readline()
                    our_syscall_name = our_line.replace(" ", "").replace("\n", "")
                while strace_line:
                    if ("--- SIG" in strace_line):                        
                        # ignore signals
                        strace_line = strace_fp.readline()
                        continue
                    if "exited with" in strace_line:
                        strace_line = strace_fp.readline()
                        break # done
                    
                    if ("wait4" in strace_line):
                        strace_syscall_name = "wait4"
                    else:
                        #val = get_parser().parse(strace_line)
                        #j = to_json(val)
                        #strace_syscall_name = j[0]['name']
                        x=strace_line
                        strace_syscall_name =  x[18:len(x)].split('(')[0]
                    our_syscall_name = our_line.replace(" ", "").replace("\n", "")
                    if (strace_syscall_name != our_syscall_name):
                        print("ERROR:" + strace_syscall_name + " vs " + our_syscall_name + "[" + str(wrong_idx) + "]")
                        break
                        return
                    #else:
                    #    print("OK:" + strace_syscall_name)
                    our_line = vmi_fp.readline()
                    strace_line = strace_fp.readline()
                    wrong_idx += 1
        
        print("SAME SYSCALLS")
    return

    parse_our_output("/home/morenbach/log.txt")
    parse_strace_file("/home/morenbach/temp.txt.480")

    total_syscalls = 0
    missed_syscalls = 0
    for k in strace_syscall_histogram:
        total_syscalls += strace_syscall_histogram[k]
        if (k not in our_syscall_histogram):
            missed_syscalls += strace_syscall_histogram[k]
            continue

        missed_syscalls += abs(strace_syscall_histogram[k] - our_syscall_histogram[k])


    print (" ==== Missed syscalls: " + str(missed_syscalls) + " out of total: " + str(total_syscalls) + " (" + str(int(100*float(missed_syscalls) / total_syscalls)) + "%) ==== ")
    print ("Histogram:")
    for k in strace_syscall_histogram:
        actual = 0
        if (k in our_syscall_histogram):
            actual = our_syscall_histogram[k]
        print ("[" + k + "] " + str(actual) + "/" + str(strace_syscall_histogram[k]))


if __name__ == "__main__":
    main()
