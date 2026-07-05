from sqlalchemy import Column, Integer, String
from database.db_session import Base

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    role = Column(String)
    code_elevage = Column(String)