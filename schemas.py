from pydantic import BaseModel, Field
from datetime import datetime

class BookCreate(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    author: str = Field(min_length=1, max_length=200)
    year: int = Field(gt=0, le=datetime.now().year)
    

class BookResponse(BaseModel):  
    id: int
    title: str
    author: str
    year: int