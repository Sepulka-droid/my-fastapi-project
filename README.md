# FastAPI Микросервисы: TODO и ShortURL

Два микросервиса на FastAPI, упакованные в Docker контейнеры.

## Сервисы

### 1. TODO-сервис
- **Порт:** 8000
- **Эндпоинты:** CRUD для задач
- **База данных:** SQLite
- **Документация:** `http://localhost:8000/docs`

### 2. Сервис сокращения URL (ShortURL)
- **Порт:** 8001
- **Эндпоинты:** Создание коротких ссылок, редиректы, статистика
- **База данных:** SQLite
- **Документация:** `http://localhost:8001/docs`

## Запуск через Docker

### Предварительные требования
- Docker

### 1. Сборка образов
```bash
# Собрать TODO-сервис
cd todo_app
docker build -t todo-service:latest .
```

# Собрать ShortURL-сервис
```
cd ../shorturl_app
docker build -t shorturl-service:latest .
```

### 2. Тестирование TODO-сервиса:
```
curl -X POST "http://localhost:8000/items" \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task"}'

# Получить все задачи
curl "http://localhost:8000/items"
```

### 3. Тестирование ShortURL-сервиса:
```
# Создать короткую ссылку
curl -X POST "http://localhost:8001/shorten" \
  -H "Content-Type: application/json" \
  -d '{"url": "https://example.com"}'

# Получить статистику
curl "http://localhost:8001/stats/<short_url>
```



