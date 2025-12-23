from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from fastapi.responses import RedirectResponse
import db_models
from db_models import SessionLocal, create_tables

# Создаем приложение FastAPI
app = FastAPI(title="URL Shortener Service",
              description="Сервис сокращения URL"
)


# Создаем таблицы при старте приложения
@app.on_event("startup")
def on_startup():
    create_tables()


# Валидации Pydantic
class ShortenRequest(BaseModel):
    url: str

    class Config:
        pass


class ShortenResponse(BaseModel):
    short_url: str
    full_url: str


class StatsResponse(BaseModel):
    short_url: str
    full_url: str
    id: int


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


# Создание короткой ссылки
@app.post("/shorten", response_model=ShortenResponse)
def shorten_url(request: ShortenRequest, db: Session = Depends(get_db)):
    url = request.url.strip()
    if not url.startswith(('http://', 'https://')):
        url = 'http://' + url

    # Проверяем, не существует ли уже такой URL в БД
    existing_url = db.query(db_models.ShortURL).filter(
        db_models.ShortURL.full_url == url
    ).first()

    if existing_url:
        return ShortenResponse(
            short_url=existing_url.short_url,
            full_url=existing_url.full_url
        )

    # Создаем новую запись
    new_url = db_models.ShortURL(full_url=url)

    db.add(new_url)
    db.commit()
    db.refresh(new_url)

    return new_url
    # return ShortenResponse(
    #     short_url=new_url.short_url,
    #     full_url=new_url.full_url
    # )


# Редирект по короткой ссылке
@app.get("/{short_url}")
def redirect_to_full_url(short_url: str, db: Session = Depends(get_db)):
    url_record = db.query(db_models.ShortURL).filter(
        db_models.ShortURL.short_url == short_url
    ).first()

    if not url_record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return RedirectResponse(url=url_record.full_url, status_code=307)


# Статистика по короткой ссылке
@app.get("/stats/{short_url}", response_model=StatsResponse)
def get_url_stats(short_url: str, db: Session = Depends(get_db)):
    url_record = db.query(db_models.ShortURL).filter(
        db_models.ShortURL.short_url == short_url
    ).first()

    if not url_record:
        raise HTTPException(status_code=404, detail="Short URL not found")

    return StatsResponse(
        id=url_record.id,
        short_url=url_record.short_url,
        full_url=url_record.full_url
    )


# Главная страничка сайта
@app.get("/")
def read_root():
    return {
        "message": "URL Shortener Service is running",
        "docs": "/docs",
        "endpoints": {
            "shorten": "POST /shorten",
            "redirect": "GET /{short_url}",
            "stats": "GET /stats/{short_url}"
        }
    }