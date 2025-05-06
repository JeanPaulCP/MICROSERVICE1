from sqlalchemy import Column, Integer, String, Date, Table, ForeignKey
from sqlalchemy.orm import relationship
from .database import Base

usuario_rol = Table(
    'usuario_rol', Base.metadata,
    Column('id_usuario', Integer, ForeignKey('usuarios.id_usuario'), primary_key=True),
    Column('id_rol', Integer, ForeignKey('roles.id_rol'), primary_key=True)
)

class Usuario(Base):
    __tablename__ = "usuarios"

    id_usuario = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(100))
    apellido = Column(String(100))
    correo = Column(String(100), unique=True)
    fecha_registro = Column(Date)

    roles = relationship("Rol", secondary=usuario_rol, back_populates="usuarios")


class Rol(Base):
    __tablename__ = "roles"

    id_rol = Column(Integer, primary_key=True, index=True)
    nombre_rol = Column(String(50), unique=True)

    usuarios = relationship("Usuario", secondary=usuario_rol, back_populates="roles")
