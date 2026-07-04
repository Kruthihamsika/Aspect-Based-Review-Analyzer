from pydantic import BaseModel, Field


class UploadResponse(BaseModel):
    message: str = Field(default="File uploaded successfully")
    upload_id: str
    total_reviews: int
    status: str = Field(default="uploaded")
