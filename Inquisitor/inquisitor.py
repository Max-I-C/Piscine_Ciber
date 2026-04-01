import argparse
import sys

class Inquisitor():
    def __init__(self, argument):
        self.ip_addr_host = argument[1]
        self.mac_addr_host = argument[2]
        self.ip_addr_serv = argument[3]
        self.mac_addr_serv = argument[4]
        print(f"Constructor, inquisition set : {self.mac_addr_host} + {self.ip_addr_host} + {self.mac_addr_serv} + {self.ip_addr_serv}")

    def poisoning():
        print("All the logic about the change of IP in the networks")

def main():
    if(len(sys.argv) < 5):
        print("[ERROR, not enought args]")
        return
    inquisition = Inquisitor(sys.argv)
    

if (__name__ == "__main__"):
    main()