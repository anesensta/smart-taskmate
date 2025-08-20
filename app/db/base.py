from sqlmodel import Session,create_engine,select,SQLModel
import os
from dotenv import load_dotenv
load_dotenv()

engin = create_engine(url=os.getenv("DATABASE_url"),echo=True)
def init_db():
    SQLModel.metadata.create_all(engin)
def get_session():
    with Session(engin) as session:
        yield session