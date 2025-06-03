from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, Session
from starlette import status

from src.database import get_db, MovieModel
from src.database.models import CountryModel, GenreModel, ActorModel, LanguageModel, CountryModel
from src.schemas.movies import MovieResponse, MovieCreate, MovieListItemResponse, PaginationResponse, MovieDetailResponse, CountryResponse


router = APIRouter()

@router.post("/theater/movies/", response_model=MovieResponse)
def add_film(film:  MovieCreate, db: Session = Depends(get_db)):
    added_film = db.query(MovieModel).filter(MovieModel.name == film.name, MovieModel.date == film.date).first()
    if added_film:
        raise HTTPException(status_code=400, detail="Movie already exists")

    country = db.query(CountryModel).filter(CountryModel.code == film.country).first()

    if country:
        raise HTTPException(status_code=400, detail="Country already exists")

    new_film = MovieModel(
        name=film.name,
        date=film.date,
        score=film.score,
        overview=film.overview,
        status=film.status,
        budget=film.budget,
        revenue=film.revenue,
        country_id=film.country_id
    )



    db.add(new_film)
    db.commit()
    db.refresh(new_film)

    return MovieResponse.from_orm(new_film)


@router.get("/theater/movies/", response_model=PaginationResponse)
def list_films(
        page: int = Query(1, ge=1, le=1000, description="Page number, must be >= 1"),
        per_page: int = Query(10, ge=1, le=50, description="Items per page, must be >= 1"),
        db: Session = Depends(get_db)
):
    if page < 1 or per_page < 1:
        raise HTTPException(status_code=422, detail="Input should be greater than or equal to 1")

    skip = (page - 1) * per_page
    films = db.query(MovieModel).order_by(MovieModel.id.desc()).offset(skip).limit(per_page).all()

    if not films:
        raise HTTPException(status_code=404, detail="No movies found.")

    total_items = db.query(MovieModel).count()
    total_pages = (total_items + per_page - 1) // per_page

    next_page = f"/theater/movies/?page={page + 1}&per_page={per_page}" if page < total_pages else None
    prev_page = f"/theater/movies/?page={page - 1}&per_page={per_page}" if page > 1 else None

    movie_responses = [
        MovieListItemResponse(
            id=movie.id,
            name=movie.name,
            date=movie.date.strftime('%Y-%m-%d'),
            score=movie.score,
            overview=movie.overview
        )
        for movie in films
    ]

    return PaginationResponse(
        movies=movie_responses,
        prev_page=prev_page,
        next_page=next_page,
        total_pages=total_pages,
        total_items=total_items
    )


@router.get("/theater/movies/{movie_id}/", response_model=MovieDetailResponse)
def get_movie_by_id(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(MovieModel).filter(MovieModel.id == movie_id).first()

    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found.")

    country_data = None
    if movie.country:
        country_data = CountryResponse(id=movie.country.id, name=movie.country.name, code=movie.country.code)

    return MovieDetailResponse(
        id=movie.id,
        name=movie.name,
        date=movie.date.isoformat(),
        score=movie.score,
        overview=movie.overview,
        status=movie.status.value,
        budget=movie.budget,
        revenue=movie.revenue,
        country=country_data,
        genres=[genre.name for genre in movie.genres],
        actors=[actor.name for actor in movie.actors],
        languages=[language.name for language in movie.languages]
    )


@router.get("/theater/movies/{film_id}", response_model=MovieResponse)
def read_film(film_id: int, db: Session = Depends(get_db)):
    db_film = db.query(MovieModel).filter(MovieModel.id == film_id).first()
    if not db_film:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")

    return MovieResponse(
        id=db_film.id,
        name=db_film.name,
        date=db_film.date.strftime('%Y-%m-%d'),
        score=db_film.score,
        overview=db_film.overview,
        status=db_film.status.value.lower(),
        budget=db_film.budget,
        revenue=db_film.revenue,
        country_id=db_film.country.id,
        genres=[genre.name for genre in db_film.genres],
        actors=[actor.name for actor in db_film.actors],
        languages=[language.name for language in db_film.languages]
    )


@router.delete("/theater/movies/{film_id}/", status_code=status.HTTP_204_NO_CONTENT)
def remove_film(film_id: int, db: Session = Depends(get_db)):
    db_film = db.query(MovieModel).filter(MovieModel.id == film_id).first()
    if not db_film:
        raise HTTPException(status_code=404, detail="Movie with the given ID was not found.")