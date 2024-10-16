import time
from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import os
import uuid
from minio import Minio
from selenium import webdriver
from database import get_db
from schemas import ScreenshotCreate
from crud import get_screenshot_by_url, create_or_update_screenshot_record

app = FastAPI()

# Настройка MinIO
MINIO_URL = os.getenv("MINIO_URL")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY")

minio_client = Minio(
    MINIO_URL.replace("http://", "").replace("https://", ""),
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=False
)

bucket_name = "screenshots"
if not minio_client.bucket_exists(bucket_name):
    minio_client.make_bucket(bucket_name)


@app.post("/screenshot/")
async def capture_screenshot(url: str, is_fresh: bool, db: Session = Depends(get_db)):
    # Проверяем, есть ли скриншот в базе данных
    screenshot = get_screenshot_by_url(db, url)

    if screenshot and not is_fresh:
        # Возвращаем кешированный скриншот
        file_path = f"/tmp/{screenshot.minio_path}"
        minio_client.fget_object(bucket_name, screenshot.minio_path, file_path)
        return {"message": "Скриншот найден", "file_path": file_path}
    else:
        # Если требуется свежий скриншот
        screenshot_filename = f"{uuid.uuid4()}.png"
        local_file_path = f"/tmp/{screenshot_filename}"

        # Запуск браузера с Selenium для снятия скриншота
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')

        # Используйте адрес контейнера selenium
        # Подключаемся к Selenium Grid

        try:
            driver = webdriver.Remote(command_executor='http://selenium:4444/wd/hub', options=options)
            driver.get(url=url)
            # Спим 5 сек чтобы страница прогрузилась полностью
            time.sleep(5)
            driver.save_screenshot(local_file_path)
            driver.quit()

        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Ошибка при создании скриншота: {str(e)}")

        # Сохраняем скриншот в Minio
        print(f"Сохраняем скриншот в MinIO: {screenshot_filename}")
        minio_client.fput_object(bucket_name, screenshot_filename, local_file_path)
        print(f"Скриншот успешно сохранён в MinIO под именем: {screenshot_filename}")

        # Записываем запись в базу данных
        new_screenshot = ScreenshotCreate(url=url, minio_path=screenshot_filename)
        create_or_update_screenshot_record(db, new_screenshot)

        return {"message": "Скриншот создан", "file_path": local_file_path}
