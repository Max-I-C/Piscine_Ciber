import os
import argparse
import string
import time
from cryptography.fernet import Fernet

def args_mngt():
    parser = argparse.ArgumentParser(description="ft_otp")
    parser.add_argument(
        "-g", "--get",
        type=str,
        help="The program receives as argument a hexadecimal key of at least 64 characters. The program stores this key safely in a file called ft_otp.key, which is encrypted."
    )
    parser.add_argument(
        "-k", "--key",
        type=str,
        help="The program generates a new temporary password based on the key give as argument and prints it on the standard output."
    )
    args = parser.parse_args()
    return(args)

def valid_hexa_key(hexadecimal_key):
    print("Valid")
    # Need to save that key # 
    key = Fernet.generate_key()
    f = Fernet(key)
    print(f"key -> {key}")
    token = f.encrypt(hexadecimal_key.encode())
    print(f"Crypted : {token}")
    files = [".key", "ft_opt.key"]
    
    try:
        for file in files:
            create_file = open(file ,'wb')
            if (file == "key.txt"):
                create_file.write(key)
            else:
                create_file.write(token)
            create_file.close()
    except Exception as e:
        print(f"[ERROR], {e}")

def extract_from_file(original_file):
    try:
        with open(original_file) as  file:
            file = open(original_file, 'r')
            hexadecimal_key = file.read()
            print(hexadecimal_key)
            file.close()
    except Exception as e:
        print("[ERROR], {e}")
    return(hexadecimal_key)

def encrypte(hexadecimal_key):
    print("# ----- encryption to bytes scenario ----- #")
    if( all(char in string.hexdigits for char in hexadecimal_key) and len(hexadecimal_key) == 64) or (os.path.isfile(hexadecimal_key)):
        if(os.path.isfile(hexadecimal_key)):
            hexadecimal_key = extract_from_file(hexadecimal_key)
        valid_hexa_key(hexadecimal_key)
    else:
        print(["[ERROR], The key is not hexadecimal or is not 64"])
    
            
def generate_key(base_key):
    print("# ----- key generation scenario ----- #")
    # 1. Recuperer timestamp 
    timestamp = time.time()
    # 2. Le diviser par 30
    timeInterval = timestamp / 30 
    # 3. Utiliser cette valeur dans le HMAC
    # 3.1 Recuperer la clé
    try:
        with open(base_key) as file:
            file = open(base_key, 'r')
            key = file.read()
            print(key)
            file.close()
    except Exception as e:
        print("[ERROR], {e}")

    # 4. Appliquer le HOTP algo 
    # 5. Reduire a 6 chiffre   
def main():
    args = args_mngt()
    if(args.get):
        encrypte(args.get)
    if (args.key):
        generate_key(args.key)
    if (not args.key and not args.get):
        print("[ERROR], no instruction indicated.")
        return
    return

if (__name__ == "__main__"):
    main()