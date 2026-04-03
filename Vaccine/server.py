#!/usr/bin/env python3
"""
Serveur Flask volontairement vulnérable aux injections SQL.
UNIQUEMENT pour tester vaccine.py en local — ne jamais déployer en prod.
"""

from flask import Flask, request
import sqlite3

app = Flask(__name__)
DB_PATH = "test_vuln.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    c.executescript("""
        DROP TABLE IF EXISTS users;
        DROP TABLE IF EXISTS products;
        DROP TABLE IF EXISTS secrets;

        CREATE TABLE users (
            id       INTEGER PRIMARY KEY,
            username TEXT,
            password TEXT,
            email    TEXT
        );
        CREATE TABLE products (
            id    INTEGER PRIMARY KEY,
            name  TEXT,
            price REAL,
            stock INTEGER
        );
        CREATE TABLE secrets (
            id    INTEGER PRIMARY KEY,
            label TEXT,
            value TEXT
        );

        INSERT INTO users VALUES
            (1, 'admin',   'sup3r_s3cr3t', 'admin@corp.io'),
            (2, 'alice',   'alice1234',    'alice@corp.io'),
            (3, 'bob',     'b0bpass',      'bob@corp.io'),
            (4, 'charlie', 'ch4rlie!',     'charlie@corp.io');

        INSERT INTO products VALUES
            (1, 'Laptop',     999.99, 10),
            (2, 'Mouse',       19.99, 50),
            (3, 'Keyboard',    49.99, 30),
            (4, 'Monitor',    299.99,  8);

        INSERT INTO secrets VALUES
            (1, 'api_key',      'sk-XXXX-super-secret-key'),
            (2, 'db_password',  'root_password_1234'),
            (3, 'internal_url', 'http://internal-api.corp.io:8080');
    """)
    conn.commit()
    conn.close()
    print("[*] Base de données initialisée : test_vuln.db")

@app.route("/")
def index():
    return """
    <h2>Serveur de test SQLi — Vaccine</h2>
    <ul>
        <li>GET  <a href="/search?q=1">/search?q=1</a>  — recherche produit</li>
        <li>GET  <a href="/user?id=1">/user?id=1</a>    — profil utilisateur</li>
        <li>POST /login                                  — formulaire de connexion</li>
    </ul>
    """

@app.route("/search")
def search():
    q = request.args.get("q", "")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        query = f"SELECT * FROM products WHERE id = {q}"
        rows = conn.execute(query).fetchall()
        result = "<br>".join(
            f"[{r['id']}] {r['name']} — {r['price']}€ (stock: {r['stock']})"
            for r in rows
        ) or "Aucun résultat."
        return f"<pre>{result}</pre>"
    except sqlite3.OperationalError as e:
        return f"<pre>SQLite error: {e}\nQuery was: {query}</pre>", 500
    finally:
        conn.close()

@app.route("/user")
def user():
    uid = request.args.get("id", "")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        query = f"SELECT username, email FROM users WHERE id = {uid}"
        row = conn.execute(query).fetchone()
        if row:
            return f"<pre>User: {row['username']} | Email: {row['email']}</pre>"
        return "<pre>Utilisateur introuvable.</pre>"
    except sqlite3.OperationalError as e:
        return f"<pre>SQLite error: {e}\nQuery was: {query}</pre>", 500
    finally:
        conn.close()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return """
        <form method="POST">
            Username: <input name="username" value="admin"><br>
            Password: <input name="password" value="test"><br>
            <button type="submit">Login</button>
        </form>
        """
    username = request.form.get("username", "")
    password = request.form.get("password", "")
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        query = f"SELECT * FROM users WHERE username = '{username}' AND password = '{password}'"
        row = conn.execute(query).fetchone()
        if row:
            return f"<pre>Connecté en tant que : {row['username']} ({row['email']})</pre>"
        return "<pre>Identifiants incorrects.</pre>", 401
    except sqlite3.OperationalError as e:
        return f"<pre>SQLite error: {e}\nQuery was: {query}</pre>", 500
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("[*] Serveur lancé sur http://localhost:5000")
    print("[*] Endpoints :")
    print("      GET  http://localhost:5000/search?q=1")
    print("      GET  http://localhost:5000/user?id=1")
    print("      POST http://localhost:5000/login")
    app.run(debug=False, port=5000)