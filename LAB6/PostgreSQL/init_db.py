import psycopg2

conn = psycopg2.connect(
    database="postgres",
    user='postgres',
    password='password',
    host='127.0.0.1',
    port='5432'
)
conn.autocommit = True

cursor = conn.cursor()
cursor.execute("""DROP DATABASE IF EXISTS scooters;""")
cursor.execute("""CREATE DATABASE scooters;""")

conn = psycopg2.connect(
    database="scooters",
    user='postgres',
    password='password',
    host='127.0.0.1',
    port='5432'
)
conn.autocommit = True

cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS electro_scooters(
id SERIAL PRIMARY KEY,
name VARCHAR ( 255 ),
battery_level FLOAT);
""")
print("Scooters database created.")

conn.close()
