import sqlite3
from models import author, user, film, genre, FilmGenres

con = sqlite3.connect('mydatabase.db')
cursor = con.cursor()

def create():
    """Создаем таблицы базы данных"""
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {user.MODEL}")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {film.MODEL}")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {author.MODEL}")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {genre.MODEL}")
    cursor.execute(f"CREATE TABLE IF NOT EXISTS {FilmGenres.MODEL}")
    con.commit()


create() 
