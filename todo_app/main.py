from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
import db_models  # Наш файл с БД и моделью

app = FastAPI(
    title="TODO Service API",
    description="Микросервис для управления задачами",
    version="1.0.0"
)


# Валидация создания задачи
class TodoItemCreate(BaseModel):
    title: str
    description: Optional[str] = None
    completed: bool = False


# Валидация ответа клиенту
class TodoItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str]
    completed: bool

    class Config:
        from_attributes = True


# Частичное обнолвение задачи

class TodoItemUpdate(BaseModel):
    """Схема для ЧАСТИЧНОГО обновления задачи"""
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None


# === Часть 3: Зависимость для получения сессии БД ===
def get_db():
    db = db_models.SessionLocal()
    try:
        yield db  # Отдаём сессию эндпоинту
    finally:
        db.close()  # Закрываем сессию в любом случае


# === Часть 4: ЭНДПОИНТЫ API ===

# Создание новой задачи
@app.post("/items", response_model=TodoItemResponse, status_code=status.HTTP_201_CREATED)
def create_todo_item(item: TodoItemCreate, db: Session = Depends(get_db)):
    db_item = db_models.TodoItem(
        title=item.title,
        description=item.description,
        completed=item.completed
    )

    # Добавляние в БД
    db.add(db_item)
    db.commit()
    db.refresh(db_item)

    return db_item


# Список всех задач
@app.get("/items", response_model=list[TodoItemResponse])
def read_all_todo_items(db: Session = Depends(get_db)):
    return db.query(db_models.TodoItem).all()


# Получение задачи по id
@app.get("/items/{item_id}", response_model=TodoItemResponse)
def read_todo_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(db_models.TodoItem).filter(db_models.TodoItem.id == item_id).first()

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {item_id} не найдена"
        )

    return db_item


# Обновление задачи
@app.put("/items/{item_id}", response_model=TodoItemResponse)
def update_todo_item(item_id: int, item: TodoItemCreate, db: Session = Depends(get_db)):
    db_item = db.query(db_models.TodoItem).filter(db_models.TodoItem.id == item_id).first()

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {item_id} не найдена"
        )

    db_item.title = item.title
    db_item.description = item.description
    db_item.completed = item.completed
    db.commit()
    db.refresh(db_item)

    return db_item


# Частичное обновление задачи
# Не требовалось в условии задачи,
# но очень логично звучит, если мы хотим только завершить задачу
@app.patch("/items/{item_id}", response_model=TodoItemResponse)
def partial_update_todo_item(item_id: int, item_update: TodoItemUpdate,
                             db: Session = Depends(get_db)):
    db_item = db.query(db_models.TodoItem).filter(db_models.TodoItem.id == item_id).first()

    if db_item is None:
        raise HTTPException(status_code=404, detail=f"Задача с ID {item_id} не найдена")

    update_data = item_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_item, field, value)

    db.commit()
    db.refresh(db_item)
    return db_item

# Удаление задачи
@app.delete("/items/{item_id}")
def delete_todo_item(item_id: int, db: Session = Depends(get_db)):
    db_item = db.query(db_models.TodoItem).filter(db_models.TodoItem.id == item_id).first()

    if db_item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Задача с ID {item_id} не найдена"
        )

    db.delete(db_item)
    db.commit()

    return {"message": f"Задача с ID {item_id} успешно удалена"}


# Создание таблиц при запуске
@app.on_event("startup")
def on_startup():
    db_models.Base.metadata.create_all(bind=db_models.engine)
    print("Таблицы БД созданы")


# Главная страничка сайта
@app.get("/")
def read_root():
    return {
        "service": "TODO Service",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /items": "Создать задачу",
            "GET /items": "Все задачи",
            "GET /items/{id}": "Задача по ID",
            "PUT /items/{id}": "Обновить задачу",
            "DELETE /items/{id}": "Удалить задачу"
        }
    }
