#!/usr/bin/env python3
import argparse
import sys
import ipaddress
import re

class Inquisitor():
    def __init__(self, argument):
        self.ip_addr_host = argument[1]
        self.mac_addr_host = argument[2]
        self.ip_addr_serv = argument[3]
        self.mac_addr_serv = argument[4]
        print(f"Constructor, inquisition set : {self.mac_addr_host} + {self.ip_addr_host} + {self.mac_addr_serv} + {self.ip_addr_serv}")

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
    

if (__name__ == "__main__"):
    main()