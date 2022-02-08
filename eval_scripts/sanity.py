import os
from time import sleep
from subprocess import Popen
from pexpect import pxssh
import pexpect
import argparse
from shutil import copy2
import psutil

parser = argparse.ArgumentParser(description='Sanity evaluation script')
parser.add_argument('-u', '--user', help='load generator server username', default='administrator', type=str)
parser.add_argument('-p', '--password', help='load generator server password', default='Mlnx2020', type=str)
parser.add_argument('-t', '--test', help='program to test', default='lspci', type=str)
parser.add_argument('-i', '--iterations', help='number of iterations', default=1, type=int)				

def sanityTest(username, password, test_prog, idx):
    outputFilePath = "/home/morenbach/dummy.log"
    vmiOutputFileName = '/home/morenbach/eval/vmi_logs_%s/vmi_%d.txt' % (test_prog, idx)
    straceOutputFileName = '/home/administrator/strace_logs_%s/strace_%d.txt' % (test_prog, idx)
    print ("Starting test %s...storing file to: %s" % (test_prog, vmiOutputFileName))		
    GuestAddress = "192.168.122.185"

    outputFile = open(outputFilePath,'wb')

    vmi_pid = Popen("/home/morenbach/kvm-vmi/libvmi/build/examples/vmi-syscalls-trace -n ubuntu_meni -j /home/morenbach/Ubuntu-5.8.0-41.json -s /tmp/introspector -m 500 -o {}".format(vmiOutputFileName).split()).pid
	
    sleep(10)

    s = pxssh.pxssh(timeout=7200)
    if not s.login (GuestAddress, username, password):
        print ("SSH session failed on login")
        print (str(s))
    else:
        print ("SSH session login successful")
        # s.logfile = outputFile
        print("Starting process: " + test_prog)
        s.sendline("LD_PRELOAD=/home/administrator/syscall_test/hax.so strace -xx -ttt -ff -o {} {}".format(straceOutputFileName, test_prog))        
        # s.expect(pexpect.EOF)
        s.logout()
        
    outputFile.close()

    return vmi_pid

def runInternalTest(user, password, test_prog, iterations):
    GuestAddress = "192.168.122.185"
    s = pxssh.pxssh(timeout=7200)    
    if not s.login (GuestAddress, user, password):
        print ("SSH session failed on login")
        print (str(s))
    else:
        print ("SSH session login successful")
        s.sendline("rm -rf /home/administrator/strace_logs_{}".format(test_prog))
        s.sendline("mkdir -p /home/administrator/strace_logs_{}".format(test_prog))
        s.logout()

    for i in range(iterations):                
        vmi_pid = sanityTest(user, password, test_prog, i)
        print("checking if pid exists: " + str(vmi_pid))
        if psutil.pid_exists(vmi_pid):
            p = psutil.Process(vmi_pid)            
            if not p.is_running():
                break
            print("indeed exists: " + str(vmi_pid))
            sleep(1)            
        print("pid dead: " + str(vmi_pid))
    
def runTest():
    args = parser.parse_args()

    if (not args.user or not args.password  or not args.test):
        print ("Invalid usage")
        return

    # start with an empty logs dir
    logs_dir = "/home/morenbach/eval/vmi_logs_" + args.test
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)
    else:
        for the_file in os.listdir(logs_dir):
            file_path = os.path.join(logs_dir, the_file)
            os.unlink(file_path)
		
    runInternalTest(args.user, args.password, args.test, args.iterations)

if __name__ == "__main__":
	runTest()