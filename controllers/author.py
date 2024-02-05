import datetime
from typing import Literal, Annotated
from fastapi import APIRouter, Response, Cookie
from pydantic import BaseModel
from utils.sqlite_execute import execute_query
from utils.jwt_encoding import encode_token, decode_token

router = APIRouter(prefix="/author", tags=["Author"])


class ResponseModel(BaseModel):
    status: Literal["200", "404"]
    data: dict
    msg: str


@router.post("/auth", response_model=ResponseModel)
def Auth_Author(
    response: Response, author_name: str, birth_date: datetime.datetime, token: Annotated[str | None, Cookie()] = None
):
    """Авторизация Автора"""

    if token == None:
        return ResponseModel(status="404", data={}, msg="Токен не найден.")
    else:
        if not decode_token(token).get("user_id"):
            return ResponseModel(status="404", data={}, msg="Вход не выполнен.")
    data = decode_token(token)   
    user_id = data.get("user_id")
    query1 = "Select * from User where User.id == ?"
    params1 = (user_id,)
    status_query1, result1 = execute_query(query1, params1,fetch_one=True)
    if status_query1:
        if result1.get("id"):
            query2 = "Select * from Author where Author.user_id == ?"
            params2 = (user_id,)
            status_query2, result2 = execute_query(query2, params2, fetch_one=True)
            data["role"] = "author"
            token = encode_token(data)
            if status_query2:
                if not result2:
                    query3 = f"Insert Into Author(user_id, author_name, birth_date) Values(?, ?, ?);"
                    params3 = (user_id, author_name, birth_date.date())
                    status_query3, result3 = execute_query(query3, params3, fetch_one=True)
                    if status_query3:
                        response.set_cookie("token",token)
                        return ResponseModel(
                            status="200", data={}, msg="Автор зарегистрирован."
                        )
                    else:
                        return ResponseModel(status="404", data={}, msg=result2)
                else:
                    response.set_cookie("token",token)
                    return ResponseModel(status="404", data={}, msg="Вы уже являетесь автором")
            else:
                return ResponseModel(status="404", data={}, msg=result1)
        else:
            return ResponseModel(status="404", data={}, msg="Такого пользователя не существует")
    else:
        return ResponseModel(status="404", data={}, msg=result1)

    
