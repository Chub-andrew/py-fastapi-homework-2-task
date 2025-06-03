from typing import List, Optional, ClassVar

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime, date



# Base = declarative_base()

class CountryBase(BaseModel):
    id: int
    code: str
    name: str

    # schema_extra = {
    #     "example": {
    #         "id": 1,
    #         "code": "US",
    #         "name": "United States"
    #     }
    # }

    model_config: ClassVar[dict] = {
        "json_schema_extra": {
            "example": {
                "id": 1,
                "code": "US",
                "name": "United States"
            }
        }
    }

class GenreBase(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


class ActorBase(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

class LanguageBase(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)


# class MovieModel(Base):
#     __tablename__ = "movies"
#
#     id = Column(Integer, primary_key=True)
#     name = Column(String)
#     country_id = Column(Integer, ForeignKey("countries.id"), nullable=False)
#     country = relationship("CountryModel", back_populates="movies")

class MovieBase(BaseModel):
    id: int
    name: str
    date: str
    score: float
    overview: str
    status: str
    budget: float
    revenue: float
    country: CountryBase
    genres: List[GenreBase]
    actors: List[ActorBase]
    languages: List[LanguageBase]

    model_config = ConfigDict(from_attributes=True)


class MovieResponse(BaseModel):
    id: int
    name: str
    date: date
    score: Optional[float] = None
    overview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class MovieCreate(BaseModel):
    name: str
    date: date
    score: float
    overview: str
    status: str
    budget: float
    revenue: float
    country: str
    genres: List[str]
    actors: List[str]
    languages: List[str]


class MovieListItemResponse(BaseModel):
    id: int
    name: str
    date: str
    score: Optional[float] = None
    overview: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)


class PaginationResponse(BaseModel):
    movies: List[MovieListItemResponse]
    prev_page: Optional[str] = None
    next_page: Optional[str] = None
    total_pages: int
    total_items: int


class CountryResponse(BaseModel):
    id: int
    name: str = Field(..., example="USA")
    code: str = Field(..., example="US")

class MovieDetailResponse(BaseModel):
    id: int
    name: str
    date: str
    score: float
    overview: str
    status: str
    budget: float
    revenue: float
    country: CountryResponse