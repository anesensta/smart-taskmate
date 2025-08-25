from sqlmodel import SQLModel, Field,Relationship
from datetime import datetime
from enum import Enum


class priorityEnum(str, Enum):
    Low = 'Low'
    Medium = 'Medium'
    High = 'High'
class statueEnum(str, Enum):
    Pending = 'Pending'
    InProgress = 'InProgress'
    Completed = 'Completed'
    
class userbase(SQLModel):
    username: str = Field( unique=True, max_length=50, nullable=False)
    email: str|None= Field(default=None, unique=True, max_length=100, nullable=True)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class userdb(userbase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tasks:list["tasks"] = Relationship(back_populates="userrelation")
    

class tasksbase(SQLModel):
    
    title:str |None = None
    descreption:str |None = None
    due_date:datetime|None = Field(default=None,nullable=True)
    priority :priorityEnum |None= Field(default=priorityEnum.Low, nullable=True)
    statue:statueEnum |None = Field(default=statueEnum.Pending, nullable=True)
        
class tasks(tasksbase,table = True):
    id :int =Field(default=None,primary_key=True)
    user_id :int = Field(default=None,foreign_key="userdb.id")
    userrelation: userdb = Relationship(back_populates="tasks")  
    ai_suggestion:list["ai_suggestions"] = Relationship(back_populates="task")

class ai_suggestionsbase(SQLModel):
    suggestion_text:str 
class ai_suggestions(ai_suggestionsbase,table = True):
    id:int = Field(default=None,primary_key=True)
    task_id:int =Field(default=None,foreign_key="tasks.id") 
    task:tasks=Relationship(back_populates="ai_suggestion")
        