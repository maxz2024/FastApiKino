from typing import Literal, Annotated
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel
from utils.sqlite_execute import execute_query
from utils.jwt_encoding import encode_token, decode_token

router = APIRouter(prefix="/user", tags=["User"])


class ResponseModel(BaseModel):
    status: Literal["200", "404"]
    data: dict
    msg: str


@router.post("/auth", response_model=ResponseModel)
def Auth_User(
    name: str, login: str, password: str,
):
    """Авторизация пользователя"""

    query1 = "Select * from User where User.login == ?"
    params1 = (login,)
    status_query, result1 = execute_query(query1, params1)
    if status_query:
        if len(result1) != 0:
            return ResponseModel(status="404", data={}, msg="Такой логин уже занят!")
    else:
        return ResponseModel(status="404", data={}, msg=result1)

    query2 = f"Insert Into User(name, login, password) Values(?, ?, ?);"
    params2 = (name, login, password)
    status_query, result2 = execute_query(query2, params2, fetch_one=True)
    if status_query:
        return ResponseModel(
            status="200", data={}, msg="Вы успешно зарегистрировались"
        )
    else:
        return ResponseModel(status="404", data={}, msg=result2)


@router.post("/login", response_model=ResponseModel)
def Login_User(
    response: Response,
    login: str,
    password: str,
    token: Annotated[str | None, Cookie()] = None,
):
    """Вход пользователя"""

    if token:
        if decode_token(token).get("user_id"):
            return ResponseModel(
                status="200",
                data=decode_token(token),
                msg="Вход уже был выполнен.",
            )

    query = f"Select * from User where User.login == ? and User.password == ?"
    params = (login, password)
    status_query, result = execute_query(query, params, fetch_one=True)
    if status_query:
        if result:
            response.set_cookie(
                "token",
                encode_token({"user_id": result["id"], "login": result["login"], "role": "user"}),
            )
            return ResponseModel(status='200', data=result, msg="Вход выполнен")
        else:
            return ResponseModel(
                status='404',
                data={},
                msg="Ошибка входа, проверьте логин и пароль.",
            )
    else:
        return ResponseModel(status="404", data={}, msg=result)


@router.get("/current", response_model=ResponseModel)
def Current_User(response: Response, token: Annotated[str | None, Cookie()] = None):
    """Получение текущего пользователя"""
    if token == None:
        return ResponseModel(status="404", data={}, msg="Токен не найден.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Токен не верный.")
        else:
            query1 = "Select * from User where User.id == ?" 
            params1 = (decode_token(token)["user_id"],)
            status_query1, result1 = execute_query(query1, params1, fetch_one=True)
            if status_query1:
                if not result1:
                    response.delete_cookie("token")
                    return ResponseModel(status='404', data={}, msg="Пользователь с таким токеном не существует.")
            else:
                return ResponseModel(status='404', data={}, msg=result1)
        return ResponseModel(
            status="200", data=decode_token(token), msg=""
        )



@router.get("/logout", response_model=ResponseModel)
def Logout_User(response: Response, token: Annotated[str | None, Cookie()] = None):
    """Выход пользователя"""

    if token:
        response.delete_cookie("token")
        return ResponseModel(status="200", data={}, msg="Выход выполнен.")
    else:
        return ResponseModel(status="404", data={}, msg="Выход не возможен.")

@router.post("/edit", response_model=ResponseModel)
def Edit_User(key: Literal['name', 'login', 'password'], value: str, token: Annotated[str | None, Cookie()] = None,):
    """Редактирование данных о пользователе
    :key - название атрибута для изменения
    :value - значение на которое надо поменять"""
    
    if token == None:
        return ResponseModel(status="404", data={}, msg="Вы не авторизованы.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Токен не верный.")
        
    query1 = "Select * from User where User.id == ?" 
    params1 = (decode_token(token)["user_id"],)
    status_query1, result1 = execute_query(query1, params1, fetch_one=True)
    if status_query1:
        if not result1.get("id"):
            return ResponseModel(status='404', data={}, msg="Пользователь с таким токеном не существует.")
        query2 = f"Update User set {key}=? where id= ?"
        
        params2 = (value,decode_token(token)["user_id"])
        status_query2, result2 = execute_query(query2, params2, fetch_one=True)
        if status_query2:
            status_query3, result3 = execute_query(query1, params1, fetch_one=True)
            
            return ResponseModel(status='200',data=result3,msg="Данные изменены.")
        else:
            return ResponseModel(status='404', data=result2, msg="")
    else:
        return ResponseModel(status='404', data={}, msg=result1)
