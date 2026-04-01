import argparse
import sys

class inquisition():
    def __init__(self):
        print("Constructor")

def main():
    if(sys.argv[1] is not None):
        print(sys.argv[1])

if (__name__ == "__main__"):
    main()