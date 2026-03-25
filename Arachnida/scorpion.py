import sys
import os
from PIL import Image
from PIL.ExifTags import TAGS

def file_info(file):
    if(not os.path.isfile(file)):
        print(f"[ERROR], the file : {file} dosen't exist or is not a file")
    elif (not file.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))):
        print("Extension error")

    img = Image.open(file)
    exif = img.getexif()

    if not img.info:
        print("No metadata founded!")
    else:
        print("# ------ METADATA ------ #")
        for key, value in img.info.items():
            print(f"{key} : {value}")
        print("# ---------------------- #")
    
    if not exif:
        print("No exif founded!")
    else:
        print("# ------ EXIF ------ #")
        for key, value in exif.items():
            tag = TAGS.get(key, key)
            print(f"{tag} : {value}")
        print("# ------------------ #")  

def main():
    if(sys.argv) < 2:
        print("[ERROR], correct usage : python scorpion.py [FILE1] [FILE2] [FILE...]")
        return
    
    for file in sys.argv[1:]:
        file_info(file)
        

if (__name__ == "__main__"):
    main()