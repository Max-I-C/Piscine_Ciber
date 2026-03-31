from pathlib import Path
import argparse
import os

def args_manager():
    parser = argparse.ArgumentParser(description="Spider")
    parser.add_argument(
        "-v", "--version",
        type=int,
        default=1,
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
    def __init__(self, key):
        print(f"Constructor, key value -> {key}")
        self.key = key

    def decrypt_files(self):
        print("hello decryption")

    def encrypt_files(self, path):
        if os.path.exists(path):
            main_folder = Path(path)
            for elements in main_folder.rglob('*'):
                if elements.is_file():
                    try:
                        with open(elements) as f: 
                            content = f.read()
                            print("FILE CONTENT -> ", content)
                            # ENCRYPTER LES DONNEES PUIS SAUVER LA CLE #
                    except Exception as e:
                        print(f"[ERROR], {e}")

def main():
    print("Hello")
    args = args_manager()
    Stockholm = RansomWare("key")
    Stockholm.encrypt_files('infection')


if(__name__ == "__main__"):
    main()