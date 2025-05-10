from fastapi import FastAPI
from .routers import usuarios
from . import models, database
from fastapi.middleware.cors import CORSMiddleware

# Crear tablas si no existen
models.Base.metadata.create_all(bind=database.engine)

# Crear app
app = FastAPI()

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Puedes reemplazar "*" con ["http://localhost:3000"] en producción
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registrar rutas
app.include_router(usuarios.router)
