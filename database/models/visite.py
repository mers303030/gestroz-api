from sqlalchemy import Column, Integer, String
from database.db_session import Base

class Visite(Base):
    __tablename__ = 'visites'
    id = Column(Integer, primary_key=True)
