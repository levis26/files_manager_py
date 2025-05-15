import os
import shutil

# Variable global para almacenar la ruta del directorio de datos
DATA_DIR = None
PROJECT_ROOT = None

def initialize_paths(project_root_path):
    """
    Inicializa las rutas DATA_DIR y PROJECT_ROOT basadas en la ruta raíz del proyecto.
    Debe ser llamada una vez al inicio de la aplicación.
    """
    global DATA_DIR, PROJECT_ROOT
    PROJECT_ROOT = os.path.abspath(project_root_path)
    DATA_DIR = os.path.join(PROJECT_ROOT, 'data')

    # Asegurar que el directorio data exista
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"utils.py: Directorio DATA_DIR creado en: {DATA_DIR}") # Log para verificar
    else:
        print(f"utils.py: Directorio DATA_DIR ya existe en: {DATA_DIR}") # Log para verificar


# Helper function to get full path with security checks
def get_full_path(user_path):
    """
    Construye la ruta completa dentro de DATA_DIR y la valida para prevenir
    vulnerabilidades de Directory Traversal.
    Retorna la ruta absoluta si es válida, de lo contrario retorna None.
    """
    # Asegurarse de que DATA_DIR ha sido inicializado
    if DATA_DIR is None:
        print("utils.py: Error: DATA_DIR no inicializado. Llama a initialize_paths() al inicio.")
        return None

    # --- Logging para diagnóstico detallado ---
    print(f"\n--- get_full_path ---")
    print(f"Input user_path: '{user_path}'")
    print(f"Configured DATA_DIR: '{DATA_DIR}'")

    try:
        # Si no se proporciona ninguna ruta (ej. para el directorio raíz), retornar la ruta absoluta de DATA_DIR.
        if not user_path:
            data_dir_abs = os.path.abspath(DATA_DIR)
            print(f"Result: user_path vacío, retornando DATA_DIR absoluto = '{data_dir_abs}'")
            print(f"--- Fin get_full_path ---\n")
            return data_dir_abs

        # Normalizar la ruta: resolver '..' y '.', y eliminar separadores redundantes.
        # .strip(os.sep) asegura que la ruta sea verdaderamente relativa a DATA_DIR
        normalized_path = os.path.normpath(user_path).strip(os.sep)
        print(f"Normalized path: '{normalized_path}'")
        
        # Unir DATA_DIR con la ruta de usuario normalizada para obtener la ruta completa deseada.
        full_item_path = os.path.join(DATA_DIR, normalized_path)
        print(f"Joined path (DATA_DIR + normalized): '{full_item_path}'")
        
        # Obtener la ruta absoluta de DATA_DIR para comparación.
        data_dir_abs = os.path.abspath(DATA_DIR)
        
        # Obtener la ruta absoluta y resuelta del elemento solicitado por el usuario.
        requested_abs = os.path.abspath(full_item_path)
        print(f"Requested absolute path: '{requested_abs}'")
        
        # Validación de seguridad crucial: Asegurarse de que la ruta absoluta solicitada esté dentro de DATA_DIR.
        # os.path.commonpath retorna el sub-camino común más largo. Si no es DATA_DIR mismo,
        # significa que la ruta solicitada está fuera de DATA_DIR (ej. vía '..').
        # Convertir ambas rutas a minúsculas para comparación insensible a mayúsculas (útil en algunos OS)
        if not requested_abs.lower().startswith(data_dir_abs.lower()):
             print(f"SECURITY ALERT: Path '{requested_abs}' is outside DATA_DIR '{data_dir_abs}'. Returning None.")
             print(f"--- Fin get_full_path ---\n")
             return None # La ruta está fuera de DATA_DIR, potencial intento de traversal.

        # Si la ruta es válida y está dentro de DATA_DIR, retornar su forma absoluta.
        # La verificación de existencia se realiza por la función que llama (ej. os.path.exists() en delete_item).
        print(f"Result: Valid path within DATA_DIR. Returning '{requested_abs}'")
        print(f"--- Fin get_full_path ---\n")
        return requested_abs
    except Exception as e:
        # Capturar cualquier error inesperado durante el procesamiento de la ruta.
        print(f"Exception in get_full_path for '{user_path}': {e}. Returning None.")
        print(f"--- Fin get_full_path ---\n")
        return None

def get_current_path_display(path):
    """
    Retorna una visualización legible de la ruta actual relativa a DATA_DIR.
    """
    # Asegurarse de que DATA_DIR ha sido inicializado
    if DATA_DIR is None:
         print("utils.py: Error: DATA_DIR no inicializado. Llama a initialize_paths() al inicio.")
         return 'Error de Ruta'

    # Si la ruta corresponde a la ruta absoluta de DATA_DIR, mostrar 'data/'
    if os.path.abspath(path) == os.path.abspath(DATA_DIR):
        return 'data/'
    
    # Obtener la ruta relativa a DATA_DIR
    try:
        relative_path = os.path.relpath(path, DATA_DIR)
        # Reemplazar separadores específicos del OS con barras diagonales para visualización en URL
        display_path = relative_path.replace(os.sep, '/')
        # Añadir barra diagonal al final si es un directorio (ya manejado arriba para la raíz)
        # Solo añadir si no es la cadena vacía (que representa el directorio actual si es DATA_DIR)
        if os.path.isdir(path) and display_path and not display_path.endswith('/'):
             display_path += '/'
        # Si relative_path es '.', display_path es '', queremos 'data/'
        if display_path == '.':
             display_path = ''
        return 'data/' + display_path
    except ValueError:
        # Manejar casos donde la ruta no está dentro de DATA_DIR
        return 'Ruta Inválida'

