import datetime
from typing import Literal, Annotated
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel
from app.utils.sqlite_execute import execute_query
from app.utils.jwt_encoding import encode_token, decode_token

router = APIRouter(prefix="/genre", tags=["Genre"])


class ResponseModel(BaseModel):
    status: Literal["200", "404"]
    data: dict | list
    msg: str

@router.post("/add", response_model=ResponseModel)
def Add_Genre(
    response: Response,
    name: str,
    token: Annotated[str | None, Cookie()] = None,
):
    """Добавление жанра"""

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
        return ResponseModel(status="404", data={}, msg=result1)

    query2 = "Select * from Author where user_id  = ?"
    params2 = (user_id,)
    status_query2, result2 = execute_query(query2, params2, fetch_one=True)
    if status_query2:
        if not result2:
            return ResponseModel(status='404',data={},msg="Автор не зарегистрирован.")
        else:
            author_info = result2
    else:
        return ResponseModel(status="404", data={}, msg=result2)
    
    query3 = "Select * from Genre where Genre.name == ?"
    params3 = (name,)
    status_query3, result3 = execute_query(query3, params3, fetch_one=True)
    if status_query3:
        if result3:
            return ResponseModel(status="404", data={}, msg="Такой жанр уже есть!")
    else:
        return ResponseModel(status="404", data={}, msg=result3)

    query4 = f"Insert Into Genre(name) Values(?);"
    param4 = (name,)
    status_query4, result4 = execute_query(query4, param4, fetch_one=True)
    if status_query4:
        return ResponseModel(status="200", data={}, msg="Вы успешно добавили жанр.")
    else:
        return ResponseModel(status="404", data={}, msg=result4)


@router.get("/get/all", response_model=ResponseModel)
def Get_All_Films(token: Annotated[str | None, Cookie()] = None):
    """Получение всех фильмов"""

    if token == None:
        return ResponseModel(status="404", data={}, msg="Вы не авторизованы.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Токен не верный.")

    query1 = "Select * from Genre"
    status_query, result1 = execute_query(query1)
    if status_query:
        return ResponseModel(status="200", data=result1, msg="")
    else:
        return ResponseModel(status="404", data={}, msg="")
