from importlib.resources import read_text

import pytest

import tests.data
from strace_parser.parser import get_parser
from strace_parser.json_transformer import to_json

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
            print(syscall_name)
            if (syscall_name in our_syscall_histogram):
                our_syscall_histogram[syscall_name] += 1;
            else:
                our_syscall_histogram[syscall_name] = 1;

            line = fp.readline()

def main():
    global strace_syscall_histogram
    global our_syscall_histogram
    parse_our_output("./our.txt")
    parse_strace_file("./strace.txt")

    missed_syscalls = 0
    for k in strace_syscall_histogram:
        if (k not in our_syscall_histogram):
            missed_syscalls += strace_syscall_histogram[k]
            continue

        assert (strace_syscall_histogram[k] >= our_syscall_histogram[k])
        missed_syscalls += strace_syscall_histogram[k] - our_syscall_histogram[k]


    print (" ==== Missed syscalls: " + str(missed_syscalls) + " ==== ")
    print ("Histogram:")
    for k in strace_syscall_histogram:
        actual = 0
        if (k in our_syscall_histogram):
            actual = our_syscall_histogram[k]
        print ("[" + k + "] " + str(actual) + "/" + str(strace_syscall_histogram[k]))


if __name__ == "__main__":
    main()
