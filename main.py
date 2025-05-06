from fastapi import FastAPI
from .routers import usuarios
from . import models, database

models.Base.metadata.create_all(bind=database.engine)

app = FastAPI()
app.include_router(usuarios.router)
