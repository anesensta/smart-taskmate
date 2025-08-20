import os
from fastapi import FastAPI,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel,select,Session
from app.db.base import  get_session
from auth import get_password_hash, verify_password, creat_jwt_token, decode_jwt_token
from datetime import timedelta

from app.db.models import userdb, tasks, userbase

api = FastAPI()

@api.post("/singup")
def sign_up(dataformat :OAuth2PasswordRequestForm, session: Session=Depends(get_session)):
    user = session.exec(select(userbase).where(userbase.email == dataformat.username)).first()
    if user :
        raise HTTPException(status_code=400, detail="User already exists")
    new_user = userbase(email=dataformat.username, password=get_password_hash(dataformat.password))
    session.add(new_user)
    session.commit()
    session.refresh(new_user)
    return {"message": "User created successfully", "user_id": new_user.id}
    
@api.post("/login")
def login (dataformat:OAuth2PasswordRequestForm,session:Session= Depends(get_session)):
    user = session.exec(select(userdb).where(userdb.email == dataformat.username)).first()
    if not user or not verify_password(dataformat.password, user.password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    token = creat_jwt_token({"email": userdb.email, "id": userdb.id})
    return {"access_token": token, "token_type": "bearer"}
@api.get("/users/me")
def get_current_user(token:str = Depends(OAuth2PasswordBearer(tokenUrl="\login")),session:Session=Depends(get_session)):
    try:
        decode_token = decode_jwt_token(token)
        user = session.exec(select(userdb).where(userdb.id == decode_token.get("id"))).first()
        if not user :
            raise HTTPException(status_code=404, detail="User not found")
    except ValueError as e :
        raise HTTPException(status_code=401, detail=str(e))
    return {"username": user.email, "id": user.id}