from typing import Literal, Annotated
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel
from utils.sqlite_execute import execute_query
from utils.jwt_encoding import encode_token, decode_token

router = APIRouter(prefix="/film", tags=["Film"])


class ResponseModel(BaseModel):
    status: Literal["200", "404"]
    data: dict | list
    msg: str

@router.post("/add", response_model=ResponseModel)
def Add_Film(name: str, description: str, genre: str, token: Annotated[str | None, Cookie()] = None):
    """Добавление фильма"""
    
    if token == None:
        return ResponseModel(status="404", data={}, msg="Вы не авторизованы.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Токен не верный.")
        
    user_id = decode_token(token)["user_id"]
    query1 = "Select * from User where id  = ?"
    params1 = (user_id,)
    status_query1, result1 = execute_query(query1, params1, fetch_one=True)
    if status_query1:
        if result1.get("role") != "creative":
            return ResponseModel(status="404", data={}, msg="Вы зарегистрированы как пользователь. Ваша роль должна быть creative")
    else:
        return ResponseModel(status="404", data={}, msg=result1)
    
    query1 = "Select * from Film where Film.name == ?"
    params1 = (name,)
    status_query, result1 = execute_query(query1, params1)
    if status_query:
        if len(result1) != 0:
            return ResponseModel(status="404", data={}, msg="Такой фильм уже есть!")
    else:
        return ResponseModel(status="404", data={}, msg=result1)

    query2 = f"Insert Into Film(code_avtor, name, description, genre) Values(?, ?, ?, ?);"
    params2 = (user_id, name, description, genre)
    status_query, result2 = execute_query(query2, params2, fetch_one=True)
    if status_query:
        return ResponseModel(
            status="200", data={}, msg="Вы успешно добавили фильм"
        )
    else:
        return ResponseModel(status="404", data={}, msg=result2)

@router.get("/get/all", response_model=ResponseModel)
def Get_All_Films(token: Annotated[str | None, Cookie()] = None):
    """Получение всех фильмов"""
    
    if token == None:
        return ResponseModel(status="404", data={}, msg="Вы не авторизованы.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Токен не верный.")
        
    query1 = "Select * from Film"
    status_query, result1 = execute_query(query1)
    if status_query:
        return ResponseModel(status='200', data=result1, msg="")
    else:
        return ResponseModel(status='404', data={}, msg="")

