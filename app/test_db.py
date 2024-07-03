import sqlite3

def get_db_connection():
    connection = sqlite3.connect('blackjack.db')
    tableExists = connection.execute('SELECT * FROM sqlite_master WHERE type="table" AND name="gamestates"').fetchall() != []
    if not tableExists:
        print("Creating gamestates table...")
        with open('./BJschema.sql') as f:
            connection.executescript(f.read())
    connection.row_factory = sqlite3.Row
    return connection

def reset_db():
    connection = get_db_connection()
    connection.execute('DROP TABLE IF EXISTS gamestates')
    with open('./BJschema.sql') as f:
        connection.executescript(f.read())
    connection.commit()
    connection.close()

connection = get_db_connection()
cur = connection.cursor()
print("Database connection established successfully...")
tablesList = cur.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall()
print("Tables SQL executed successfully...")
for table in tablesList:
    print(table)
gs = cur.execute("SELECT * FROM gamestates ORDER BY id DESC").fetchall()
print("gamestates SQL executed successfully...")
for state in gs:
    print(state['id'], state['player'], state['dealer'])
print("gamestates printed successfully...")
connection.commit()
connection.close()
