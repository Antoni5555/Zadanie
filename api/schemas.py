from pydantic import BaseModel


class ScreenshotBase(BaseModel):
    url: str


class ScreenshotCreate(ScreenshotBase):
    minio_path: str


class Screenshot(ScreenshotBase):
    id: int
    minio_path: str

    class Config:
        from_attributes = True
