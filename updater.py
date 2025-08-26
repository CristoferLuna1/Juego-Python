import requests
import os
import io
import zipfile
import shutil
import sys

# URL para obtener la última versión disponible
VERSION_URL = "https://raw.githubusercontent.com/CristoferLuna1/Juego-Python/master/version.txt"
# URL para descargar el archivo zip de la última versión
ZIP_URL = "https://github.com/CristoferLuna1/Juego-Python/archive/refs/heads/master.zip"

# Nombre del archivo donde se guarda la versión local
LOCAL_VERSION_FILE = "version.txt"

def get_local_version():
    if os.path.exists(LOCAL_VERSION_FILE):
        with open(LOCAL_VERSION_FILE, "r") as f:
            return f.read().strip()
    return "0.0.0"

def get_remote_version():
    r = requests.get(VERSION_URL)
    r.raise_for_status()
    return r.text.strip()

def updater_game():
    print("Descargando actualización...")

    r = requests.get(ZIP_URL, stream=True)
    r.raise_for_status()
    total_size = int(r.headers.get('content-length', 0))
    block_size = 1024  # 1 KB
    downloaded_size = 0
    zip_data = io.BytesIO()

    for data in r.iter_content(block_size):
        zip_data.write(data)
        downloaded_size += len(data)
        percent = downloaded_size / total_size * 100
        mb_downloaded = downloaded_size / (1024 * 1024)
        mb_total = total_size / (1024 * 1024)
        # Muestra progreso en la misma línea
        sys.stdout.write(f"\rDescargado: {mb_downloaded:.2f}/{mb_total:.2f} MB ({percent:.1f}%)")
        sys.stdout.flush()

    print("\nDescarga completada. Extrayendo archivos...")

    zip_data.seek(0)
    z = zipfile.ZipFile(zip_data)

    temp_dir = "temp_update"
    z.extractall(temp_dir)

    extracted_folder = os.path.join(temp_dir, "Juego-Python-master")
    for item in os.listdir(extracted_folder):
        s = os.path.join(extracted_folder, item)
        d = os.path.join(".", item)
        if os.path.isdir(s):
            if os.path.exists(d):
                shutil.rmtree(d)
            shutil.copytree(s, d)
        else:
            shutil.move(s, d)

    shutil.rmtree(temp_dir)
    print("Actualización completada.")

    # Actualiza la versión local
    remote_version = get_remote_version()
    with open(LOCAL_VERSION_FILE, "w") as f:
        f.write(remote_version)

def main():
    local_version = get_local_version()
    print(f"Versión local: {local_version}")
    try:
        remote_version = get_remote_version()
        print(f"Versión remota: {remote_version}")
        if local_version != remote_version:
            print("Nueva versión disponible. Actualizando...")
            updater_game()
        else:
            print("El juego ya está actualizado.")
    except requests.RequestException as e:
        print(f"No se pudo comprobar la versión remota: {e}")

if __name__ == "__main__":
    main()
