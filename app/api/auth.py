from passlib.context import CryptContext
from jwt import encode as jwt_encode, decode as jwt_decode, InvalidTokenError,ExpiredSignatureError

from datetime import datetime, timedelta
import os 
from dotenv import load_dotenv

load_dotenv()

pwd_context = CryptContext(shemas=['bcrypt'], deprecated="auto")
def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)
def verify_password(palin_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return pwd_context.verify(palin_password,hash_password)


def creat_jwt_token(data:dict,expire_delta:timedelta|None=None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow()+(expire_delta or timedelta(minutes=30))
    to_encode.update({"exp": expire})
    secret_key = jwt_encode(to_encode, os.getenv("secret_key"), algorithm=os.getenv("Algorithm"))

    return secret_key
def decode_jwt_token(token: str) -> dict:
    try:
        data = jwt_decode(token, os.getenv("secret_key"), algorithms=[os.getenv("Algorithm")])
        return data 
    except InvalidTokenError:
        raise ValueError("Invalid token")
    except ExpiredSignatureError:
        raise ValueError("Token has expired")
    