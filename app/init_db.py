import sqlite3

connection = sqlite3.connect('blackjack.db')
with open('BJschema.sql') as f:
    connection.executescript(f.read())

connection.commit()
connection.close()