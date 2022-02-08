# -*- coding: utf-8 -*- 

# from __future__ import unicode_literals
import matplotlib
matplotlib.rcParams.update({
    'backend': 'pdf',
    'font.family': 'sans-serif',
    'font.size': 14,
    'font.sans-serif': ['Linux Biolinum O'],
})

import os
import matplotlib.pyplot as plt
import matplotlib.pylab as pylab
import numpy as np

def parseResults(file):
        baseline = []
        vmi = []
        with open(file) as fp:
            lines = fp.readlines()
            for line in lines:
                val = float(line.split(',')[2].split(':')[1].replace(" ","").replace("\\n\'",""))
                if "False" in line: # baseline
                    baseline.append(val)
                else:
                    vmi.append(val)

        baseline_np = np.array(baseline)
        vmi_np = np.array(vmi)

        baseline_std = np.std(baseline_np)
        baseline_mean = np.mean(baseline_np)
        baseline_median = np.median(baseline_np)

        vmi_std = np.std(vmi_np)
        vmi_mean = np.mean(vmi_np)
        vmi_median = np.median(vmi_np)
        print("[" + file + "] vmi_std: " + str(vmi_std) + ", vmi_mean: " + str(vmi_mean) + ", vmi_median: " + str(vmi_median))
        print("[" + file + "] baseline_std: " + str(baseline_std) + ", baseline_mean: " + str(baseline_mean) + ", baseline_median: " + str(baseline_median))

        return (baseline_median, vmi_median)
		
def Plot():
    params = {'legend.fontsize': 'xx-large', 'axes.labelsize': 'xx-large', 'axes.titlesize':'xx-large', 'xtick.labelsize':'xx-large', 'ytick.labelsize':'xx-large'}
    pylab.rcParams.update(params)

    N = 3
    ind = np.arange(N)  # the x locations for the groups
    width = 0.2       # the width of the bars

    fig = plt.figure()
    fig.set_size_inches(10.5, 4.5)

    ax = fig.add_subplot(111)

    kvm_baseline_vals = []
    kvm_vmi_vals = []

    # Got values from Thanh
    xen_baseline_vals = [ 0.172, 0.234, 0.860 ]        
    xen_vmi_vals = [ 12.8397, 13.7992, 12.9049 ]

    (baseline, vmi) = parseResults('/home/morenbach/eval/latency_log_raasnet.txt')    
    kvm_baseline_vals.append(baseline)
    kvm_vmi_vals.append(vmi)
    (baseline, vmi) = parseResults('/home/morenbach/eval/latency_log_ransom0.txt')    
    kvm_baseline_vals.append(baseline)
    kvm_vmi_vals.append(vmi)
    (baseline, vmi) = parseResults('/home/morenbach/eval/latency_log_ransomware_poc.txt')    
    kvm_baseline_vals.append(baseline)
    kvm_vmi_vals.append(vmi)

    rects1 = ax.bar(ind, kvm_baseline_vals, width, color='#016c59', edgecolor='k', zorder=3)
    rects2 = ax.bar(ind+width, kvm_vmi_vals, width, color='#1c9099', edgecolor='k', zorder=3)
    rects3 = ax.bar(ind+width*2, xen_baseline_vals, width, color='#67a9cf', edgecolor='k', zorder=3)
    rects4 = ax.bar(ind+width*3, xen_vmi_vals, width, color='#bdc9e1', edgecolor='k', zorder=3)

    ax.set_ylabel('Latency (seconds)')
    ax.set_xticks(ind+width)
    ax.set_xticklabels( ('RAASNet', 'Ransom0', 'Ransomware-POC') )
    ax.legend( (rects1[0], rects2[0], rects3[0], rects4[0]), ('Non-intrusive baseline', 'Non-intrusive tracing', 'Intrusive baseline', 'Intrusive tracing'), bbox_to_anchor=(0., 1.02, 1., .102), loc=3, ncol=2, mode="expand", borderaxespad=0.)

    plt.tight_layout()
    plt.gca().yaxis.grid(True,zorder=0)

    tmp=plt.gca().get_yticklabels()
    tmp[0]=''
    plt.gca().set_yticklabels(tmp)
    plt.yscale("log")

    plt.savefig('ransomware_latency.pdf')

if __name__ == "__main__":
	Plot()
