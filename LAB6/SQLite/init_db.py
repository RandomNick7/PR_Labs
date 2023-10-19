import sqlite3

conn = sqlite3.connect('scooters.db')

cur = conn.cursor()

cur.execute("""DROP TABLE IF EXISTS electro_scooters;""")
cur.execute("""
    CREATE TABLE IF NOT EXISTS electro_scooters (
        id INTEGER PRIMARY KEY,
        name TEXT NOT NULL,
        battery_level REAL NOT NULL
    );"""
)
print("Scooters database created.")

conn.commit()
cur.close()
conn.close()
