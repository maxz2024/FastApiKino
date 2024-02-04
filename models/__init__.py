import sqlite3
from models import user, film

con = sqlite3.connect('mydatabase.db')
cursor = con.cursor()

def create():
    """Создаем таблицы базы данных"""
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {user.MODEL}")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {film.MODEL}")
    con.commit()

create() 
