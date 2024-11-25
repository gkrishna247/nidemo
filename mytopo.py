#!/usr/bin/python

from mininet.net import Mininet
from mininet.node import Controller, CPULimitedHost
from mininet.link import TCLink
from mininet.topo import Topo
from mininet.log import setLogLevel

class DumbbellTopo(Topo):
    "Dumbbell topology with a bottleneck link."

    def build(self, n=2):  # n hosts on each side
        leftSwitch = self.addSwitch('s1')
        rightSwitch = self.addSwitch('s2')

        # Add hosts to left side
        leftHosts = []
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            leftHosts.append(host)
            self.addLink(host, leftSwitch)

        # Add hosts to right side
        rightHosts = []
        for h in range(n, 2*n):
            host = self.addHost('h%s' % (h + 1))
            rightHosts.append(host)
            self.addLink(host, rightSwitch)

        # Add bottleneck link
        self.addLink(leftSwitch, rightSwitch, bw=10, delay='10ms', loss=0, max_queue_size=1000) # Adjust bw, delay, loss as needed


def runExperiment(tcp_congestion_ctrl):
    topo = DumbbellTopo(n=1)  # Just one host on each side for simplicity
    net = Mininet(topo=topo, host=CPULimitedHost, link=TCLink, controller=Controller)
    net.start()

    h1 = net.get('h1')
    h2 = net.get('h2')

    # Set the TCP congestion control algorithm
    h1.cmd('sysctl -w net.ipv4.tcp_congestion_control=%s' % tcp_congestion_ctrl)

    # Run iperf for throughput measurement
    server_cmd = 'iperf -s -w 16m'  # Server (receiver)
    client_cmd = 'iperf -c %s -t 10 -w 16m' % h2.IP() # Client (sender), adjust time as needed

    h2.cmd(server_cmd + ' &') # Run server in background
    result = h1.cmd(client_cmd) # Run client and capture output

    print("Results for %s:" % tcp_congestion_ctrl)
    print(result)

    net.stop()



if __name__ == '__main__':
    setLogLevel('info')

    algorithms = ['reno', 'cubic', 'bbr']
    for algo in algorithms:
      runExperiment(algo)
