import sqlite3
import os

def get_db():
    conn = sqlite3.connect('database/Webseite.db')
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():

    try:

        db_path = 'database/Webseite.db'
        first_run = not os.path.exists(db_path)

        conn = get_db()
        cur = conn.cursor()

        cur.execute('''
            CREATE TABLE IF NOT EXISTS user (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                email TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                cover BLOB NOT NULL,
                preis REAL NOT NULL,
                imBesitz BOOL NOT NULL DEFAULT 0,
                uploaded_by_user BOOL DEFAULT 0
            )
        ''')

        cur.execute('''
            CREATE TABLE IF NOT EXISTS user_bibliothek (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                game_id INTEGER,
                name TEXT,
                cover BLOB,
                FOREIGN KEY (user_id) REFERENCES user (id),
                FOREIGN KEY (game_id) REFERENCES shop_games (id)
            )
        ''')

        conn.commit()

        if first_run:
            # Füge nur beim ersten Erstellen der Datenbank die Spiele hinzu
            add_initial_games(conn)

    except Exception as e:
        print("an exception occured in initialize_db: ", e)

    finally:

        conn.close()

def add_initial_games(conn):
    cur = conn.cursor()

    # Bilder als binary lesen lassen
    with open('Ffxboxart.jpg', 'rb') as f:
        cover_bild1 = f.read()

    with open('9007385-0.jpg', 'rb') as f:
        cover_bild2 = f.read()

    with open('EldenRing-1.jpg', 'rb') as f:
        cover_bild3 = f.read()

    with open('290px-Pokémon_Rubin.jpg', 'rb') as f:
        cover_bild4 = f.read()

    # Überprüfen, ob die Tabelle bereits Daten enthält
    cur.execute("SELECT COUNT(*) FROM games")
    count = cur.fetchone()[0]

    if count == 0:
        # Bilder in die Datenbank einfügen
        cur.execute("INSERT INTO games (name, cover, preis) VALUES (?, ?, ?)",
                    ('Final Fantasy 10', cover_bild1, 29.99))

        cur.execute("INSERT INTO games (name, cover, preis) VALUES (?, ?, ?)",
                    ('Pokemon Saphire', cover_bild2, 89.99))

        cur.execute("INSERT INTO games (name, cover, preis) VALUES (?, ?, ?)",
                    ('Elden Ring', cover_bild3, 69.99))

        cur.execute("INSERT INTO games (name, cover, preis) VALUES (?, ?, ?)",
                    ('Pokemon Rubin', cover_bild4, 89.99))

        conn.commit()

if __name__ == '__main__':
    initialize_db()
