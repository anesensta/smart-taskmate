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
    email: str= Field(unique=True, max_length=100,nullable=False)
    password_hash: str = Field(max_length=255, nullable=False)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    
class userdb(userbase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    tasks:list["tasks"] = Relationship(back_populates="users")


class tasksbase(SQLModel):
    
    title:str = Field(nullable=False)
    descreption:str |None = None
    due_date:datetime = Field(default=None)
    priority :priorityEnum = Field(default=priorityEnum.Low, nullable=False)
    statue:statueEnum = Field(default=statueEnum.Pending, nullable=False)
        
class tasks(tasksbase,table = True):
    id :int =Field(default=None,primary_key=True)
    user_id :int = Field(default=None,foreign_key="users.id")
    userrelation: user = Relationship(back_populates="tasks")  
    ai_suggestion:list["ai_suggestions"] = Relationship(back_populates="tasks")

class ai_suggestionsbase(SQLModel):
    suggestion_text:str 
class ai_suggestions(ai_suggestionsbase,table = True):
    id:int = Field(default=None,primary_key=True)
    task_id:int =Field(default=None,foreign_key="tasks.id") 
    task:tasks=Relationship(back_populates="ai_suggestions")
        