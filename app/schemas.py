from pydantic import BaseModel
from typing import List
from datetime import date
from pydantic import field_validator

class RolBase(BaseModel):
    nombre_rol: str

class Rol(RolBase):
    id_rol: int
    class Config:
        from_attributes = True

class UsuarioBase(BaseModel):
    nombre: str
    apellido: str
    correo: str
    fecha_registro: date
    n_resena: int = 0
    n_prestamo: int = 0

    @field_validator("n_prestamo")
    @classmethod
    def validar_n_prestamo(cls, value):
        if value > 1:
            raise ValueError("El usuario no puede tener más de 1 préstamo activo.")
        return value

class UsuarioCreate(UsuarioBase):
    roles: List[RolBase]  # lista de roles base

class Usuario(UsuarioBase):
    id_usuario: int
    roles: List[Rol]
    class Config:
        from_attributes = True