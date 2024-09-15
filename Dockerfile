# Usa una imagen base de Python
FROM python:3.10-slim

# Instala las dependencias del sistema
RUN apt-get update && apt-get install -y \
    binutils \
    libproj-dev \
    gdal-bin \
    postgresql-client

# Establece el directorio de trabajo
WORKDIR /usr/src/app

# Copia el archivo requirements.txt y instala las dependencias
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copia el código del proyecto
COPY . .

# Expone el puerto 8000 para el servidor Django
EXPOSE 8000

# Comando por defecto para ejecutar el servidor
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
