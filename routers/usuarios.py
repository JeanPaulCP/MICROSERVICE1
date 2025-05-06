from typing import List # Para Python 3.8 o anterior
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas, database

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate, db: Session = Depends(get_db)):

    roles_db = []
    for rol_data in usuario.roles:
        # rol_data es un JSON con los datos del rol
        db_rol = db.query(models.Rol).filter(models.Rol.nombre_rol == rol_data.nombre_rol).first()
        if not db_rol:
            db_rol = models.Rol(nombre_rol=rol_data.nombre_rol)
            db.add(db_rol)
            db.commit()
            db.refresh(db_rol)
        roles_db.append(db_rol)

    db_usuario = models.Usuario(
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        fecha_registro=usuario.fecha_registro,
        roles=roles_db
    )
    db.add(db_usuario)
    db.commit()
    db.refresh(db_usuario)

    return db_usuario

@router.get("/", response_model=List[schemas.Usuario])
def listar_usuarios(db: Session = Depends(get_db)):
    return db.query(models.Usuario).all()

@router.get("/{id_usuario}", response_model=schemas.Usuario)
def obtener_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return usuario

@router.put("/{id_usuario}", response_model=schemas.Usuario)
def actualizar_usuario(id_usuario: int, usuario_actualizado: schemas.UsuarioCreate, db: Session = Depends(get_db)):
    usuario_db = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usuario_db:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    usuario_db.nombre = usuario_actualizado.nombre
    usuario_db.apellido = usuario_actualizado.apellido
    usuario_db.correo = usuario_actualizado.correo
    usuario_db.fecha_registro = usuario_actualizado.fecha_registro

    # Actualizando roles
    roles_db = []
    for rol_data in usuario_actualizado.roles:
        db_rol = db.query(models.Rol).filter(models.Rol.nombre_rol == rol_data.nombre_rol).first()
        if not db_rol:
            db_rol = models.Rol(nombre_rol=rol_data.nombre_rol)
            db.add(db_rol)
            db.commit()
            db.refresh(db_rol)
        roles_db.append(db_rol)
    usuario_db.roles = roles_db

    db.commit()
    db.refresh(usuario_db)
    return usuario_db

@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int, db: Session = Depends(get_db)):
    usuario = db.query(models.Usuario).filter(models.Usuario.id_usuario == id_usuario).first()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    db.delete(usuario)
    db.commit()
    return {"mensaje": "Usuario eliminado exitosamente"}
