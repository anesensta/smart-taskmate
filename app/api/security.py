from passlib.context import CryptContext
from jwt import exceptions,decode,encode

from datetime import datetime, timedelta
import os 
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(schemes=['bcrypt'], deprecated="auto")
def hash_password(password: str) -> str:
    
    return pwd_context.hash(password)
def verify_password(palin_password: str, hashed_password: str) -> bool:
   
    return pwd_context.verify(palin_password,hashed_password)


def creat_jwt_token(data:dict,expire_delta:timedelta|None=None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow()+(expire_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    secret_key = encode(to_encode, os.getenv("secret_key"), algorithm="HS256")

    return secret_key
def decode_jwt_token(token: str) -> dict:
    try:
        data = decode(token, os.getenv("secret_key"), algorithms=["HS256"])
        return data 
    except exceptions.InvalidTokenError :
        raise ValueError("Invalid token")
    except  exceptions.ExpiredSignatureError :
        raise ValueError(f"Token expired")
    