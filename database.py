import sqlite3

def connect_to_database():
    conn = sqlite3.connect('database.sqlite')
    cursor = conn.cursor()
    return cursor, conn