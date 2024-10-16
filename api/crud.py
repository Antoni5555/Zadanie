from sqlalchemy.orm import Session
from models import Screenshot
from schemas import ScreenshotCreate
from sqlalchemy.exc import IntegrityError


def get_screenshot_by_url(db: Session, url: str):
    return db.query(Screenshot).filter(Screenshot.url == url).first()


# Version 3

def create_or_update_screenshot_record(db: Session, screenshot: ScreenshotCreate):
    # Попробуем получить существующую запись
    db_screenshot = get_screenshot_by_url(db, screenshot.url)

    if db_screenshot:
        # Если запись существует, обновим её
        db_screenshot.minio_path = screenshot.minio_path
    else:
        # Если записи нет, создадим новую
        db_screenshot = Screenshot(url=screenshot.url, minio_path=screenshot.minio_path)
        db.add(db_screenshot)

    # Пробуем сохранить изменения
    try:
        db.commit()
    except IntegrityError:
        db.rollback()
        # Обработка ошибок (например, если происходит дублирование)
        raise

    db.refresh(db_screenshot)
    return db_screenshot


"""
# Version 1

def create_screenshot_record(db: Session, screenshot: ScreenshotCreate):
    db_screenshot = Screenshot(url=screenshot.url, minio_path=screenshot.minio_path)
    db.add(db_screenshot)
    db.commit()
    db.refresh(db_screenshot)
    return db_screenshot
"""

"""
# Version 2

def create_screenshot_record(db: Session, screenshot: ScreenshotCreate):
    # Сначала проверяем, существует ли запись с таким же URL
    existing_screenshot = get_screenshot_by_url(db, screenshot.url)
    if existing_screenshot:
        # Если запись существует, возвращаем её или обрабатываем по вашему усмотрению
        return existing_screenshot

    # Если запись не существует, создаём новую
    db_screenshot = Screenshot(url=screenshot.url, minio_path=screenshot.minio_path)
    db.add(db_screenshot)
    try:
        db.commit()
        db.refresh(db_screenshot)
    except IntegrityError:
        db.rollback()
        # Здесь можно вернуть ошибку или обработать её
        return None  # Или можно вернуть существующую запись, если это имеет смысл

    return db_screenshot

"""
