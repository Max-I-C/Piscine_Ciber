import os
import argparse
import string
import time
import hmac
import hashlib
import binascii
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
    files = ["master.key", "ft_otp.key"]
    
    try:
        for file in files:
            create_file = open(file ,'wb')
            if (file == "master.key"):
                create_file.write(key)
            else:
                create_file.write(token)
            create_file.close()
    except Exception as e:
        print(f"[ERROR], {e}")

def extract_from_file(original_file):
    try:
        with open(original_file) as  file:
            hexadecimal_key = file.read().strip()
            #print(hexadecimal_key)
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
    
            
def generate_key(base_key_encrypted):
    print("# ----- key generation scenario ----- #")
    # 1. Recuperer timestamp 
    timestamp = time.time()
    # 2. Le diviser par 30
    timeInterval = int(timestamp // 30)
    #print(timeInterval) 
    # 3. Utiliser cette valeur dans le HMAC
    # 3.1 Recuperer la clé
    try:
        with open(base_key_encrypted) as file:
            key_encrypted = file.read().strip()
            #print(key)
        # DECHIFFRE LA CLE 
        with open("master.key") as file:
            key_decode = file.read().strip()
            #print(key_decode)
        f = Fernet(key_decode.encode())
        decoded_key = f.decrypt(key_encrypted.encode())
        # 3.2 Transfo de la cle hexa en bytes
        key_bytes = binascii.unhexlify(decoded_key)
        # 3.3 Convertir le compteur en 8bytes
        counter_bytes = timeInterval.to_bytes(8,  'big')
        hmac_hash = hmac.new(key_bytes, counter_bytes, hashlib.sha1).digest()
        offset = hmac_hash[-1] & 0x0F
        code = (
            ((hmac_hash[offset] & 0x7f) << 24) |
            ((hmac_hash[offset + 1] & 0xff) << 16) |
            ((hmac_hash[offset + 2] & 0xff) << 8) |
            (hmac_hash[offset + 3] & 0xff) 
        )
        otp = code % 1_000_000
        print(f"OTP code: {str(otp).zfill(6)}")
    except Exception as e:
        print(f"[ERROR], {e}")

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