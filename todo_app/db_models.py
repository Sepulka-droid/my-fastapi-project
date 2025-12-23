from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker


# База данных будет в папке /app/data внутри контейнера.
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/todo.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})

# Создаем фабрику сессий для работы с БД.
#  Каждый запрос к API будет работать в своей сессии.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Модель базы данных
class TodoItem(Base):
    __tablename__ = "todo_items"

    # идентификатор
    id = Column(Integer, primary_key=True, index=True)
    # название задачи
    title = Column(String, nullable=False)

    # описание, необязательно
    description = Column(String, nullable=True)  # Необязательное поле

    # статус выполнения
    completed = Column(Boolean, default=False)   # По умолчанию False


# Функция для создания таблиц при запуске
def create_tables():
    Base.metadata.create_all(bind=engine)