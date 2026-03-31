from fastapi import FastAPI

from app.lifespan import lifespan

app = FastAPI(lifespan=lifespan)
