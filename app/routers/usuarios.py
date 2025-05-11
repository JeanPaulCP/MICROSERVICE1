from fastapi import APIRouter, HTTPException
from typing import List
from .. import schemas, database

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

@router.post("/", response_model=schemas.Usuario)
def crear_usuario(usuario: schemas.UsuarioCreate):
    conn = database.get_connection()
    cursor = conn.cursor()

    # Insertar o verificar roles
    roles_ids = []
    for rol in usuario.roles:
        cursor.execute("SELECT id_rol FROM roles WHERE nombre_rol = %s", (rol.nombre_rol,))
        resultado = cursor.fetchone()
        if resultado:
            id_rol = resultado[0]
        else:
            cursor.execute("INSERT INTO roles (nombre_rol) VALUES (%s)", (rol.nombre_rol,))
            conn.commit()
            id_rol = cursor.lastrowid
        roles_ids.append({"id_rol": id_rol, "nombre_rol": rol.nombre_rol})

    # Insertar usuario con n_resena y n_prestamo
    cursor.execute(
        """
        INSERT INTO usuarios (nombre, apellido, correo, fecha_registro, n_resena, n_prestamo)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (
            usuario.nombre,
            usuario.apellido,
            usuario.correo,
            usuario.fecha_registro,
            usuario.n_resena,
            usuario.n_prestamo
        )
    )
    id_usuario = cursor.lastrowid

    # Insertar en tabla intermedia usuario_rol
    for rol in roles_ids:
        cursor.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (%s, %s)", (id_usuario, rol["id_rol"]))

    conn.commit()
    conn.close()

    return schemas.Usuario(
        id_usuario=id_usuario,
        nombre=usuario.nombre,
        apellido=usuario.apellido,
        correo=usuario.correo,
        fecha_registro=usuario.fecha_registro,
        n_resena=usuario.n_resena,
        n_prestamo=usuario.n_prestamo,
        roles=[schemas.Rol(**rol) for rol in roles_ids]
    )

@router.get("/", response_model=List[schemas.Usuario])
def listar_usuarios():
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios")
    usuarios_raw = cursor.fetchall()

    usuarios = []
    for usuario in usuarios_raw:
        # Buscar roles de ese usuario
        cursor.execute("""
            SELECT r.id_rol, r.nombre_rol
            FROM roles r
            JOIN usuario_rol ur ON r.id_rol = ur.id_rol
            WHERE ur.id_usuario = %s
        """, (usuario["id_usuario"],))
        roles = cursor.fetchall()
        usuarios.append(schemas.Usuario(**usuario, roles=roles))

    conn.close()
    return usuarios

@router.get("/{id_usuario}", response_model=schemas.Usuario)
def obtener_usuario(id_usuario: int):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)

    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    usuario = cursor.fetchone()
    if not usuario:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    cursor.execute("""
        SELECT r.id_rol, r.nombre_rol
        FROM roles r
        JOIN usuario_rol ur ON r.id_rol = ur.id_rol
        WHERE ur.id_usuario = %s
    """, (id_usuario,))
    roles = cursor.fetchall()

    conn.close()
    return schemas.Usuario(**usuario, roles=roles)

@router.put("/{id_usuario}", response_model=schemas.Usuario)
def actualizar_usuario(id_usuario: int, usuario_actualizado: schemas.UsuarioCreate):
    conn = database.get_connection()
    cursor = conn.cursor(dictionary=True)

    # Verificar existencia del usuario
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    if not cursor.fetchone():
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Actualizar todos los campos del usuario (incluyendo los nuevos)
    cursor.execute("""
        UPDATE usuarios
        SET nombre = %s,
            apellido = %s,
            correo = %s,
            fecha_registro = %s,
            n_resena = %s,
            n_prestamo = %s
        WHERE id_usuario = %s
    """, (
        usuario_actualizado.nombre,
        usuario_actualizado.apellido,
        usuario_actualizado.correo,
        usuario_actualizado.fecha_registro,
        usuario_actualizado.n_resena,
        usuario_actualizado.n_prestamo,
        id_usuario
    ))

    # Borrar roles anteriores
    cursor.execute("DELETE FROM usuario_rol WHERE id_usuario = %s", (id_usuario,))

    # Insertar nuevos roles (o crearlos si no existen)
    roles_actualizados = []
    for rol in usuario_actualizado.roles:
        cursor.execute("SELECT id_rol FROM roles WHERE nombre_rol = %s", (rol.nombre_rol,))
        result = cursor.fetchone()
        if result:
            id_rol = result["id_rol"]
        else:
            cursor.execute("INSERT INTO roles (nombre_rol) VALUES (%s)", (rol.nombre_rol,))
            conn.commit()
            id_rol = cursor.lastrowid
        cursor.execute("INSERT INTO usuario_rol (id_usuario, id_rol) VALUES (%s, %s)", (id_usuario, id_rol))
        roles_actualizados.append({"id_rol": id_rol, "nombre_rol": rol.nombre_rol})

    conn.commit()
    conn.close()

    return schemas.Usuario(
        id_usuario=id_usuario,
        nombre=usuario_actualizado.nombre,
        apellido=usuario_actualizado.apellido,
        correo=usuario_actualizado.correo,
        fecha_registro=usuario_actualizado.fecha_registro,
        n_resena=usuario_actualizado.n_resena,
        n_prestamo=usuario_actualizado.n_prestamo,
        roles=[schemas.Rol(**rol) for rol in roles_actualizados]
    )

@router.delete("/{id_usuario}")
def eliminar_usuario(id_usuario: int):
    conn = database.get_connection()
    cursor = conn.cursor()

    # Verificar existencia
    cursor.execute("SELECT * FROM usuarios WHERE id_usuario = %s", (id_usuario,))
    if not cursor.fetchone():
        conn.close()
        raise HTTPException(status_code=404, detail="Usuario no encontrado")

    # Eliminar relaciones
    cursor.execute("DELETE FROM usuario_rol WHERE id_usuario = %s", (id_usuario,))
    cursor.execute("DELETE FROM usuarios WHERE id_usuario = %s", (id_usuario,))

    conn.commit()
    conn.close()

    return {"mensaje": "Usuario eliminado exitosamente"}