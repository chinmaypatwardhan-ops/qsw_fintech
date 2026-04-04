#!/usr/bin/env python3
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI
from mininet.log import setLogLevel, info
import os

ASN_MAP = [1, 0, 0, 3, 4, 2, 3, 2, 1, 0, 2, 1, 4, 0, 2, 3, 4, 0, 2, 1, 4, 2, 2, 3, 1, 2, 2, 2, 1, 1]
N_PATHS = 30

def create_fintech_topology():
    net = Mininet(controller=None, link=TCLink, switch=OVSKernelSwitch)

    info('*** Adding Ingress and Egress Hosts with Static MACs\n')
    h_in = net.addHost('h_in', ip='10.0.0.1/24', mac='00:00:00:00:00:01')
    h_out = net.addHost('h_out', ip='10.0.0.2/24', mac='00:00:00:00:00:02')

    info('*** Adding OpenFlow 1.3 Switches\n')
    s_in = net.addSwitch('s_in', dpid='0000000000000001', protocols='OpenFlow13')
    s_out = net.addSwitch('s_out', dpid='0000000000000002', protocols='OpenFlow13')

    net.addLink(h_in, s_in, port1=1, port2=1, bw=1000)
    net.addLink(h_out, s_out, port1=1, port2=1, bw=1000)

    path_switches = []
    for i in range(N_PATHS):
        if i < 10: crypto_delay = '2ms'
        elif i < 20: crypto_delay = '5ms'
        else: crypto_delay = '15ms'
            
        hex_dpid = f"{i+3:016x}"
        s_p = net.addSwitch(f's_p{i}', dpid=hex_dpid, protocols='OpenFlow13')
        path_switches.append(s_p)
        
        net.addLink(s_in, s_p, port1=i+2, port2=1, bw=10, delay=crypto_delay, use_tbf=True, limit=5000)
        net.addLink(s_p, s_out, port1=2, port2=i+2, bw=10, delay='1ms')

    info('*** Starting network\n')
    net.start()

    info('*** Enforcing Static ARP to prevent L2 broadcast storms\n')
    h_in.cmd('arp -s 10.0.0.2 00:00:00:00:00:02')
    h_out.cmd('arp -s 10.0.0.1 00:00:00:00:00:01')

    info('*** Injecting OpenFlow 1.3 Data Plane Rules\n')
    for i in range(N_PATHS):
        os.system(f"ovs-ofctl -O OpenFlow13 add-flow s_p{i} in_port=1,actions=output:2")
        os.system(f"ovs-ofctl -O OpenFlow13 add-flow s_p{i} in_port=2,actions=output:1")

    os.system("ovs-ofctl -O OpenFlow13 add-flow s_out in_port=1,actions=normal")
    for i in range(N_PATHS):
        os.system(f"ovs-ofctl -O OpenFlow13 add-flow s_out in_port={i+2},actions=output:1")

    group_cmd = "ovs-ofctl -O OpenFlow13 add-group s_in 'group_id=1,type=select"
    for i in range(N_PATHS):
        group_cmd += f",bucket=weight:1,actions=output:{i+2}"
    group_cmd += "'"
    os.system(group_cmd)

    os.system("ovs-ofctl -O OpenFlow13 add-flow s_in in_port=1,ip,actions=group:1")
    for i in range(N_PATHS):
        os.system(f"ovs-ofctl -O OpenFlow13 add-flow s_in in_port={i+2},actions=output:1")

    info('*** Data Plane Programmed.\n')
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    create_fintech_topology()