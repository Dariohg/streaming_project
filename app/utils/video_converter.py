import os
import subprocess
import logging


def create_hls_segments(input_file, output_dir):
    """
    Convierte un video a formato HLS con segmentos pequeños
    """
    # Crear directorio si no existe
    os.makedirs(output_dir, exist_ok=True)

    # Nombre base sin extensión
    base_name = os.path.splitext(os.path.basename(input_file))[0]

    # Ruta del playlist m3u8
    playlist_path = os.path.join(output_dir, f"{base_name}.m3u8")

    # Si ya existe el playlist, salir
    if os.path.exists(playlist_path):
        return playlist_path

    try:
        # Comando para crear segmentos HLS
        cmd = [
            'ffmpeg',
            '-i', input_file,
            '-profile:v', 'baseline',
            '-level', '3.0',
            '-start_number', '0',
            '-hls_time', '5',  # Duración de cada segmento en segundos
            '-hls_list_size', '0',  # Mantener todos los segmentos en la lista
            '-f', 'hls',
            playlist_path
        ]

        # Ejecutar comando
        subprocess.run(cmd, check=True)

        return playlist_path
    except subprocess.CalledProcessError as e:
        logging.error(f"Error al crear segmentos HLS: {e}")
        return None
    except Exception as e:
        logging.error(f"Error inesperado: {e}")
        return None