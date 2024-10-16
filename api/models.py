from sqlalchemy import Column, Integer, String
from database import Base


class Screenshot(Base):
    __tablename__ = "screenshots"

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    minio_path = Column(String, index=True)
