import datetime

def get_timestamp():
    """Genera la marca de tiempo para los logs del sistema."""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def format_filename(name):
    """Limpia el nombre del archivo para el estándar de Noa."""
    return name.replace(" ", "_").upper()
