import requests
import os
import io
import zipfile
import shutil

# URL para obtener la última versión disponible
VERSION_URL = "https://raw.githubusercontent.com/CristoferLuna1/Juego-Python/master/version.txt"
# URL para descargar el archivo zip de la última versión
ZIP_URL = "https://github.com/CristoferLuna1/Juego-Python/archive/refs/heads/master.zip"

# Nombre del archivo donde se guarda la versión local
LOCAL_VERSION_FILE = "local_version.txt"

def get_local_version():
    # Devuelve la versión local leyendo el archivo correspondiente
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    return "0.0.0"

def get_remote_version():
    # Obtiene la versión remota desde la URL
    r = requests.get(VERSION_URL)
    return r.text.strip()

def updater_game():
    print("Descargar Autolizacion")
    # Descarga el archivo zip de la última versión
    r = requests.get(ZIP_URL)
    z = zipfile.ZipFile(io.BytesIO(r.content))

    temp_dir = "temp_update"
    # Extrae el contenido del zip en una carpeta temporal
    z.extractall(temp_dir)

    # Ruta de la carpeta extraída dentro del zip
    extracted_folder = os.path.join(temp_dir, "hola-master")
    # Copia los archivos y carpetas extraídos al directorio actual
    for item in os.listdir(extracted_folder):
        s = os.path.join(extracted_folder, item)
        d = os.path.join(".", item)
        if os.path.isdir(s):
            # Si el directorio ya existe, lo elimina antes de copiar
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            # Mueve los archivos al directorio actual
            shutil.move(s, d)
    # Elimina la carpeta temporal después de actualizar
    shutil.rmtree(temp_dir)
    print("Actualización completada.")
