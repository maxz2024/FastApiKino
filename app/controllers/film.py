import datetime
import json
from typing import Literal, Annotated
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel, Field
from app.utils.sqlite_execute import execute_query
from app.utils.jwt_encoding import encode_token, decode_token

router = APIRouter(prefix="/film", tags=["Film"])


class ResponseModel(BaseModel):
    status: Literal["200", "404"]
    data: dict | list
    msg: str

@router.post("/add", response_model=ResponseModel)
def Add_Film(
    response: Response,
    film_name: str,
    description: str,
    genres: str,
    date: datetime.datetime,
    population: float,
    token: Annotated[str | None, Cookie()] = None,
):
    """Добавление фильма
    :name - Название фильма
    :description - Описание фильма
    :genres - Жанры фильмов. Вводить через пробел
    :date - Дата создание фильма
    :popilation - Оценка фильма в дробном числе от 1.0 до 5.0"""

    if token == None:
        return ResponseModel(status="404", data={}, msg="Вы не авторизованы.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Токен не верный.")

    user_id = decode_token(token)["user_id"]
    query1 = "Select * from User where id  = ?"
    params1 = (user_id,)
    status_query1, result1 = execute_query(query1, params1, fetch_one=True)
    if status_query1 and result1:
        if not result1.get("id"):
           response.delete_cookie("token")
           return ResponseModel(status='404', data={}, msg="Пользователь с таким токеном не существует.")
        elif decode_token(token)["role"] != "author":
            return ResponseModel(status='404',data={},msg="Вы не автор.")
    else:
        return ResponseModel(status="404", data={}, msg=f"{result1=}")

    query2 = "Select * from Author where user_id  = ?"
    params2 = (user_id,)
    status_query2, result2 = execute_query(query2, params2, fetch_one=True)
    if status_query2:
        if not result2:
            return ResponseModel(status='404',data={},msg="Автор не зарегистрирован.")
        else:
            author_info = result2
    else:
        return ResponseModel(status="404", data={}, msg=f"{result2}")
    query3 = "Select * from Film where Film.name == ?"
    params3 = (film_name,)
    status_query3, result3 = execute_query(query3, params3, fetch_one=True)
    if status_query3:
        if result3:
            return ResponseModel(status="404", data={}, msg="Такой фильм уже есть!")
    else:
        return ResponseModel(status="404", data={}, msg=f"{result3=}")
    
    if population > 5.0 or population < 1.0 :
        return ResponseModel(status="404", data={}, msg="Оценка фильма должна быт в промежутке от 1.0 до 5.0")

    genres = genres.strip().split(" ")
    yes = False
    for genre_name in genres:
        query4 = "Select * From Genre where Genre.name = ?"
        params4 = (genre_name,)
        status_query4, result4 = execute_query(query4, params4, fetch_one=True)
        if status_query4:
            if not result4:
                query5 = "Insert Into Genre(name) Values(?)"
                params5 = (genre_name, )
                status_query5, result5 = execute_query(query5, params5, fetch_one=True)
                if status_query5:
                    yes = True
                else:
                    return ResponseModel(status="404", data={}, msg=f"Не удалось добавить genre. {result4}")
            else:
                yes = True
        else:
            return ResponseModel(status="404", data={}, msg=f"{result4=}")   
    if yes:   
        query6 = f"Insert Into Film(author_id, name, description, population, date) Values(?, ?, ?, ?, ?);"
        params6 = (author_info["id"], film_name, description, population, date.date())
        status_query6, result6 = execute_query(query6, params6, fetch_one=True)
        if status_query6:
            yes = False
            for genre_name in genres:
                query7 = "SELECT Genre.id as genre_id, Film.Id as film_id From Genre JOIN Film WHERE Genre.name = ? AND Film.name = ?"
                params7 = (genre_name, film_name)
                status_query7, result7 = execute_query(query7, params7, fetch_one=True)
                if status_query7:
                    if result7:
                        query8 = "Insert Into FilmGenres(FilmId, GenreId) Values (?,?)"
                        params8 = (result7["film_id"], result7["genre_id"])
                        status_query8, result8 = execute_query(query8, params8)
                        if status_query8:
                            yes = True
                        else:
                            return ResponseModel(status="404", data={}, msg=f"Не удалось добавить связку FilmGenre. {result8}")
                    else:
                        return ResponseModel(status="404", data={}, msg="Ids жанра или фильма не найдено.")
                else:
                    return ResponseModel(status="404", data={}, msg=f"{result7=}")
            if yes:

                return ResponseModel(status="200", data={}, msg="Вы успешно добавили фильм")
        else:
            return ResponseModel(status="404", data={}, msg=f"{result5=}")
    else:
        return ResponseModel(status="404", data={}, msg=f"Не все жанры были добавлены.")
            


@router.get("/get/all", response_model=ResponseModel)
def Get_All_Films(token: Annotated[str | None, Cookie()] = None):
    """Получение всех фильмов"""

    if token == None:
        return ResponseModel(status="404", data={}, msg="Вы не авторизованы.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Токен не верный.")

    query1 = "Select * from Film"
    status_query1, result1 = execute_query(query1)
    data = []
    if status_query1:
        for film in result1:
            query2 = "Select Genre.name from FilmGenres join Genre where FilmId = ?  and Genre.id = GenreID"
            params2 = (film["Id"],)
            status_query2, result2 = execute_query(query2, params2)
            print(result2)
            if status_query2:
                if result2:
                    genres = list(map(lambda genre: genre["name"], result2))
                    film["genres"] = genres
                    data.append(film)
        return ResponseModel(status="200", data=result1, msg="")
    else:
        return ResponseModel(status="404", data={}, msg="")
