from sqlmodel import Session,create_engine,select,SQLModel
import os
from dotenv import load_dotenv
load_dotenv()

engin = create_engine(url=os.getenv("DATABASE_URL"),echo=True)
def init_db():
    # print("Dropping all tables...")
    # SQLModel.metadata.drop_all(engin)

    print("Recreating all tables...")
    SQLModel.metadata.create_all(engin)
def get_session():
    with Session(engin) as session:
        yield session