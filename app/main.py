
import json
import os
from fastapi import FastAPI,Depends,HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlmodel import SQLModel,select,Session

from .db.base import  get_session, init_db
from .api.security import hash_password, verify_password, creat_jwt_token, decode_jwt_token
from datetime import timedelta
from .frontend import runfrontend

from .db.models import tasksbase, userdb,tasks
from .ai import creat_task_json
api = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
@api.post("/signup")
def sign_up(dataformat :OAuth2PasswordRequestForm=Depends(), session: Session=Depends(get_session)):
    try:
        user = session.exec(select(userdb).where(userdb.username == dataformat.username)).first()
        if user :
            raise HTTPException(status_code=400, detail="User already exists")
        new_user = userdb(username=dataformat.username, password_hash=hash_password(dataformat.password))
        session.add(new_user)
        session.commit()
        session.refresh(new_user)
        return {"message": "User created successfully", "user_id": new_user.id}
    except Exception as e :
        raise HTTPException(status_code=500, detail=f"Internal server error :{str(e)}")
    
@api.post("/login")
def login (dataformat:OAuth2PasswordRequestForm = Depends(),session:Session= Depends(get_session)):
    try:
        user = session.exec(select(userdb).where(userdb.username == dataformat.username)).first()
        if not user or not verify_password(dataformat.password, user.password_hash):
            raise HTTPException(status_code=400, detail="Invalid credentials")
        token = creat_jwt_token({"sub": user.username, "id": user.id})
    except Exception as e :
        raise HTTPException(status_code=500,detail=f"Internal server error :{str(e)}")
    return {"access_token": token, "token_type": "bearer"}
@api.get("/users/me")
def get_current_user(token:str = Depends(oauth2_scheme),session:Session=Depends(get_session)):
    try:
        decode_token = decode_jwt_token(token)
        user = session.exec(select(userdb).where(userdb.id == decode_token.get("id"))).first()
        if not user :
            raise HTTPException(status_code=404, detail="User not found",)
    except ValueError as e :
        raise HTTPException(status_code=401, detail=str(e))
    return {"username": user.username, "id": user.id}

@api.post("/tasks")
def creat_task(task:tasksbase,token :str=Depends(oauth2_scheme),session:Session=Depends(get_session)):
    try:
        user_data =  decode_jwt_token(token)
        user = session.get(userdb,user_data['id'])
        if not user :
            raise HTTPException(status_code=404,detail='user not found')
        new_task = tasks (**task.model_dump(),user_id=user.id)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        
    except Exception as e :
        raise HTTPException(status_code=401, detail=str(e))
    return new_task

@api.get('/tasks')
def get_tasks(token:str= Depends(oauth2_scheme),session:Session=Depends(get_session)):
    try:
        user_data =decode_jwt_token(token)
        user_tasks = session.exec(select(tasks).where(tasks.user_id ==user_data['id'] )).all()
        return user_tasks
    except Exception as e :
        raise HTTPException(status_code=401, detail=str(e))
    
@api.delete("/tasks")
def delet_task(id:int,token:str= Depends(oauth2_scheme),session:Session=Depends(get_session)):
    
    try:
        user_data = decode_jwt_token(token)
        task = session.exec(select(tasks).where(tasks.id == id)).first()
        if task.user_id != user_data["id"]:
            raise HTTPException(status_code=403, detail="Not authorized to delete this task")

        if not task:
            raise HTTPException(status_code=404,detail='task not found')
        session.delete(task)
        session.commit()
        
        
    except Exception as e :
         raise HTTPException(status_code=401, detail=str(e))
    return {"message":"task deleted succsefly"}
@api.put("/tasks")
def update_task(id:int,task_updated:tasksbase,token:str= Depends(oauth2_scheme),session:Session=Depends(get_session)):
    try:
           
        user_data = decode_jwt_token(token)
        task = session.exec(select(tasks).where(tasks.id ==id)).first()
        if not task:
            raise HTTPException(status_code=401,detail="task dont exist")
        if task.user_id != user_data['id']:
            raise HTTPException(status_code=401,detail="Not authorized to update this task")
        for key,val in task_updated.model_dump(exclude_unset=True).items():
            setattr(task,key,val)
        
        session.commit()
        session.refresh(task)
        
    except Exception as e :
        raise HTTPException(status_code=401, detail=str(e))
    return task    
@api.post("/ai_creat")
def task_creation_ai(user_input:str,token :str=Depends(oauth2_scheme),session:Session=Depends(get_session)):
    try:
        user_data =  decode_jwt_token(token)
        user = session.get(userdb,user_data['id'])
        if not user :
            raise HTTPException(status_code=404,detail='user not found')
        task_data =creat_task_json(user_input=user_input)
      
        if not task_data.get("due_date"): 
            task_data["due_date"] = None
        new_task = tasks (**task_data,user_id=user.id)
        session.add(new_task)
        session.commit()
        session.refresh(new_task)
        
    except Exception as e :
        raise HTTPException(status_code=401, detail=str(e))
    return new_task
    
if __name__ in {"__main__", "__mp_main__"}:
    init_db()
    runfrontend( title="AI-Powered Task Manager")