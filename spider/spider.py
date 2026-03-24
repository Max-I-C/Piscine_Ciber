
import requests
import os
import argparse
from bs4 import BeautifulSoup
from genericpath import exists
from urllib.parse import urljoin
from requests import RequestException


visited = set()

def args_manager():
    parser = argparse.ArgumentParser(description="Spider")
    parser.add_argument(
        "-p", "--path",
        type=str,
        help="To indicate a path for saving the images"
    )
    parser.add_argument(
        "-r", "--recursive",
        type=bool,
        default=False,
        help="Turn to program in recurssive mode"
    )
    parser.add_argument(
        "-l", "--layer",
        type=int,
        default=5,
        help="Specify the layer quantity you want to explore"
    )
    args = parser.parse_args()
    return(args)


def curl(path, url, recurssif, layer):
    if(layer <= 0 or url in visited):
        return
    visited.add(url)
    try:
        response = requests.get(url)
    except RequestException as e:
        print("Error with ", {e})
        return
    soup = BeautifulSoup(response.text, 'html.parser')
    for image in soup.find_all('img'):
        if (image.get('src')) != None:
            img_url = urljoin(url, image.get('src')) 
            if(img_url.endswith(('.png', '.jpg', '.jpeg', '.gif', '.bmp'))):
                if(path is not None):
                    name = path + "/" + img_url.split('/')[-1]
                else:
                    name = '.data/' + img_url.split('/')[-1]
                try:
                    img = requests.get(img_url)
                    if(img.status_code != 404):
                        print(img_url)
                        file = open(name ,'wb')
                        file.write(img.content)
                        file.close()
                except RequestException as e:
                    print("Error with ", {e})
    # Ajouter la logique pour les liens #
    if(recurssif):
        for link in soup.find_all('a'):
            if(link.get('href') != None):
                link_url = urljoin(url, link.get('href'))
                curl(path, link_url, True, layer - 1)

def main():
    args = args_manager()
    print(args.recursive)
    if args.path is not None and not exists(args.path):
        os.mkdir(args.path)
    elif (not exists(".data") and args.path is None):
        os.mkdir('.data')
    curl(args.path, 'https://www.42madrid.com/', args.recursive, args.layer)

if(__name__ == "__main__"):
    main()