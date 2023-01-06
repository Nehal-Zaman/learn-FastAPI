from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models as models
from app.database import engine
from app.routers import post, user, vote

models.Base.metadata.create_all(bind=engine)

origins = [
    'https://www.google.com',
    'https://www.youtube.com'
]

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins = origins,
    allow_credentials = True,
    allow_methods = ['*'],
    allow_headers = ['*']
)

app.include_router(post.router)
app.include_router(user.router)
app.include_router(vote.router)