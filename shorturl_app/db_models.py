from sqlalchemy import create_engine, Column, Integer, String, text, event
from sqlalchemy.orm import declarative_base, sessionmaker
from string import ascii_letters, digits
from random import choice

# длина короткой ссылки
LENGTH = 6

# База данных будет в папке /app/data внутри контейнера.
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/shorturl.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


# Модель базы данных для сокращенных ссылок
class ShortURL(Base):
    __tablename__ = "short_urls"

    id = Column(Integer, primary_key=True, index=True)
    short_url = Column(String, unique=True, index=True, nullable=False)
    full_url = Column(String, nullable=False)


# Обработчик before_insert для генерации short_url
@event.listens_for(ShortURL, 'before_insert')
def generate_short_url_before_insert(mapper, connection, target):
    global LENGTH
    characters = ascii_letters + digits
    while True:
        line = ''.join(choice(characters) for _ in range(LENGTH))
        result = connection.execute(
            text("SELECT COUNT(*) FROM short_urls WHERE short_url = :url"),
            {"url": line}
        ).fetchone()
        if result and result[0] == 0:
            target.short_url = line
            break

# Функция для создания таблиц при запуске
def create_tables():
    Base.metadata.create_all(bind=engine)