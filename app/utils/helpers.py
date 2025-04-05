import os
import re
import secrets
from datetime import datetime


def format_duration(seconds):
    """Formatea segundos a formato de duración (HH:MM:SS)"""
    if not seconds:
        return "00:00"

    hours = seconds // 3600
    seconds %= 3600
    minutes = seconds // 60
    seconds %= 60

    if hours > 0:
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    else:
        return f"{int(minutes):02d}:{int(seconds):02d}"


def generate_unique_filename(original_filename):
    """Genera un nombre de archivo único para evitar colisiones"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    random_hex = secrets.token_hex(8)
    _, file_extension = os.path.splitext(original_filename)

    return f"{timestamp}_{random_hex}{file_extension}"


def sanitize_filename(filename):
    """Limpia el nombre de archivo para que sea seguro para el sistema de archivos"""
    # Eliminar caracteres no alfanuméricos excepto puntos, guiones y guiones bajos
    s = re.sub(r'[^\w\.\-]', '_', filename)

    # Asegurarse de que no comienza con un punto (archivo oculto)
    if s.startswith('.'):
        s = '_' + s

    return s


def human_readable_size(size_bytes):
    """Convierte bytes en un formato legible por humanos"""
    if size_bytes == 0:
        return "0B"

    size_name = ("B", "KB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB")
    i = 0
    while size_bytes >= 1024 and i < len(size_name) - 1:
        size_bytes /= 1024
        i += 1

    return f"{size_bytes:.2f} {size_name[i]}"


def get_video_categories():
    """Devuelve una lista de categorías de videos"""
    return [
        "Películas",
        "Series",
        "Documentales",
        "Tutoriales",
        "Música",
        "Animación",
        "Deportes",
        "Noticias",
        "Otros"
    ]