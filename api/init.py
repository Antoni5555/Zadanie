from database import Base, engine
from models import Screenshot

# Инициализация базы данных
Base.metadata.create_all(bind=engine)
