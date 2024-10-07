'''database with Sqlite3 for sign language detector'''

import sqlite3

CONNECTION = sqlite3.connect('signs.db')
CURSOR = CONNECTION.cursor()

def create_table():
    CURSOR.execute('''CREATE TABLE IF NOT EXISTS signs
        (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, date TEXT)''')
    CONNECTION.commit()

def insert(name, date):
    CURSOR.execute('INSERT INTO signs (name, date) VALUES (?, ?)', (name, date))
    CONNECTION.commit()

def select():
    CURSOR.execute('SELECT * FROM signs')
    return CURSOR.fetchall()

def delete(id):
    CURSOR.execute('DELETE FROM signs WHERE id = ?', (id,))
    CONNECTION.commit()

def close():
    CONNECTION.close()

create_table()