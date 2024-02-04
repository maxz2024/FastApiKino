from typing import Literal
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel
from utils.sqlite_execute import execute_query
from utils.jwt_encoding import encode_token, decode_token

router = APIRouter(prefix="/user", tags=["User"])


class ResponseModel(BaseModel):
    status: Literal[200, 404]
    data: dict
    msg: str


@router.post("/auth", response_model=ResponseModel)
def Auth_User(
    name: str, login: str, password: str, role: Literal["user", "create"] = "user"
):
    """Авторизация пользователя"""

    query1 = "Select * from User where User.login == ?"
    params1 = (login,)
    status_query, result1 = execute_query(query1, params1)
    if status_query:
        if len(result1) != 0:
            return {"status": 404, "data": {}, "msg": "Такой логин уже занят!"}
    else:
        return {"status": 200, "data": {}, "msg": result1}

    query2 = f"Insert Into User(name, login, password, role) Values(?, ?, ?, ?);"
    params2 = (name, login, password, role)
    status_query, result2 = execute_query(query2, params2)

    if status_query:
        if len(result2) == 0:
            return {"status": 200, "data": {}, "msg": "Вы успешно зарегистрировались"}
    else:
        return {"status": 404, "data": {}, "msg": result2}


@router.post("/login", response_model=ResponseModel)
def Login_User(
    response: Response,
    login: str,
    password: str,
    token: str | None = Cookie(default=None),
):
    """Вход пользователя"""

    if token:
        return {
            "status": 200,
            "data": decode_token(token),
            "msg": "Вход уже был выполнен.",
        }

    query = f"Select * from User where User.login == ? and User.password == ?"
    params = (login, password)
    status_query, result = execute_query(query, params)
    if status_query:
        response.set_cookie(
            "token",
            encode_token({"user_id": result[0]["id"], "login": result[0]["login"]}),
        )
        return {"status": 200, "data": result, "msg": "Вход выполнен"}
    else:
        return {
            "status": 404,
            "data": {},
            "msg": "Ошибка входа, проверьте логин и пароль.",
        }


@router.get("/current", response_model=ResponseModel)
def Current_User(token: str | None = Cookie(default=None)):
    if token == None:
        return {"status": 404, "data": {}, "msg": "Токен не найден."}
    else:
        return {"status": 200, "data": decode_token(token), "msg": "Текущий токен"}
