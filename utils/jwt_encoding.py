import jwt

SECRET = "secret" # Значение обязательно должно быть более сложным и не храниться в коде
algorithm = "HS256"

def encode_token(data: dict[str,str]):
    token = jwt.encode(data, SECRET, algorithm)
    return token

def decode_token(token: str) -> dict[str,str]:
    data = jwt.decode(token, SECRET, algorithm)
    return data