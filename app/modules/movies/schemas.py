from pydantic import BaseModel,Field,HttpUrl,ConfigDict
from datetime import date,datetime
from app.modules.movies.models import MovieCertification,MovieStatus
from uuid import UUID

class MovieCreate(BaseModel):

    title:str = Field(min_length=1,max_length=255,examples=["Spider Man"])
    duration_minutes:int = Field(gt=0)
    release_date:date | None = Field(default=None)
    description:str | None = None
    poster_url:HttpUrl | None = Field(default=None,max_length=500)
    certification:MovieCertification | None = None

class MovieResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    duration_minutes: int
    release_date: date | None
    description: str | None
    poster_url: str | None
    certification: MovieCertification | None
    status: MovieStatus
    created_at: datetime
    updated_at: datetime

class MovieUpdate(BaseModel):
    title: str | None = Field(default=None,min_length=1,max_length=255)
    duration_minutes: int | None = Field(default=None,gt=0)
    release_date: date | None = None
    description: str | None = None
    poster_url: HttpUrl | None = Field(default=None,max_length=500)
    certification: MovieCertification | None = None
    
