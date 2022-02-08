import os
import subprocess
from time import sleep, time
from subprocess import Popen
from pexpect import pxssh
import pexpect
import argparse
from shutil import copy2
import psutil
import socket

parser = argparse.ArgumentParser(description='Sanity evaluation script')
parser.add_argument('-u', '--user', help='load generator server username', default='morenbach', type=str)
parser.add_argument('-p', '--password', help='load generator server password', default='Mlnx2020', type=str)
parser.add_argument('-t', '--test', help='program to test', default='lspci', type=str)
parser.add_argument('-i', '--iterations', help='number of iterations', default=1, type=int)				

def latencyTest(username, password, test_prog, use_vmi):
    latency_file = "/home/morenbach/eval/latency_log_" + os.path.basename(test_prog) + ".txt"

    GuestAddress = "192.168.122.185"        

    time_service_process = Popen("/home/morenbach/eval/time_server", stdout=subprocess.PIPE)
    # give timing process sufficient time to init everything
    sleep(1)
	
    s = pxssh.pxssh(timeout=7200)
    if not s.login (GuestAddress, username, password):
        print ("SSH session failed on login")
        print (str(s))
    else:
        print ("SSH session login successful")        
        print("Starting process: " + test_prog)
        s.sendline("rm -rf /home/morenbach/test_ransomware")
        s.sendline("cp -r /home/morenbach/test_ransomware_bu /home/morenbach/test_ransomware")
        if use_vmi:
            s.sendline("/home/administrator/syscall_test/{}_exec_test dummy vmi &> /dev/null".format(test_prog))        
        else:
            s.sendline("/home/administrator/syscall_test/{}_exec_test dummy &> /dev/null".format(test_prog))                
        s.sendline("rm -rf /home/morenbach/test_ransomware")
        s.logout()    

    out = time_service_process.communicate()    
    with open(latency_file, 'a+') as latency_fp:  
        latency_fp.write(test_prog + ", is_vmi(" + str(use_vmi) + "), " + str(out) + "\n")

def runInternalTest(user, password, test_prog, iterations):
    for i in range(iterations):                        
        vmi_pid = 0
        while (True):
            vmi_process = Popen("/home/morenbach/kvm-vmi/libvmi/build/examples/vmi-syscalls-trace -n ubuntu_meni -j /home/morenbach/Ubuntu-5.8.0-41.json -s /tmp/introspector -m 500 -o /home/morenbach/dummy.txt".split())
            vmi_pid = vmi_process.pid
            sleep(10)
            if psutil.pid_exists(vmi_pid):
                p = psutil.Process(vmi_pid)            
                if p.is_running():
                    break
            # a_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            # location = ("127.0.0.1", 9680)
            # result_of_check = a_socket.connect_ex(location)
            # a_socket.close()
            # if result_of_check == 0:
            #     print("OPEN..BREAK")
            #     break
            # print("CLOSED")

        print("SUCCESS")


        # for line in vmi_process.stdout:
        #     print(line, end='') 
        # vmi_pid = vmi_process.pid
        # give vmi process sufficient time to init everything
        # sleep(10)
        vmi_pid = vmi_process.pid

        latencyTest(user, password, test_prog, False)
        latencyTest(user, password, test_prog, True)
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
    
    runInternalTest(args.user, args.password, args.test, args.iterations)

if __name__ == "__main__":
	runTest()