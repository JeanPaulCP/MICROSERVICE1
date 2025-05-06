# Imagen base con Python
FROM python:3.11

# Establece el directorio de trabajo
WORKDIR /app

# Copia los archivos de tu proyecto
COPY . /app

# Instala las dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que corre la app
EXPOSE 8000

# Comando para ejecutar la app
CMD ["fastapi", "dev", "main.py"]
