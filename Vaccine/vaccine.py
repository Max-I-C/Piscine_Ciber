#!/usr/bin/env python3
import argparse
import requests

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
        self.session = requests.Session() # Askip c'est pour gerer les cookies faut que je verif sa 
        print("Initalise the program")

    def make_request(self, url, method="GET", data=None):
        if(method.upper() == "GET"):
            return( requests.get(url, params=data))
        elif(method.upper() == "POST"):
            return( requests.post(url, data=data))
 
    def check_vulnerability(self, payload):
        params = {"id": f"1{payload}"}
        response = self.make_request(self.url, method=self.method, data=params)
        errors = {
            "MySQL": ["SQL syntax", "mysql_fetch_array", "MySQL Error"],
            "PostgreSQL": ["PostgreSQL query failed", "PSQLException"],
            "SQLite": ["unrecognized token", "SQLite3::prepare"]
        }
        for db_name, signa in errors.items():
            for sign in signa:
                if sign.lower() in response.text.lower():
                    print(f"# -- Vulneravbility founded : Type : {db_name}")
                    return(db_name)
        return  

    def scan(self):
        print(f"# -- Scanning {self.url} with {self.method} -- #")
        db_detected = self.check_vulnerability("'")
        if(db_detected):
            print(f"The target use {db_detected}")
        else:
            print("No sql error detected in the payload")



def main():
    args = args_manager()
    vaccine = Vaccine(args)
    vaccine.scan()

if(__name__ == "__main__"):
    main()