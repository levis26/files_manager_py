import os
import shutil

# Variable global para almacenar la ruta absoluta del directorio de datos
DATA_DIR = None
PROJECT_ROOT = None # Store project root path as well

def initialize_paths(project_root_path):
    """
    Inicializa las rutas PROJECT_ROOT y DATA_DIR basadas en la ruta raíz del proyecto.
    DATA_DIR se almacenará como ruta absoluta.
    Debe ser llamada una vez al inicio de la aplicación.
    """
    global DATA_DIR, PROJECT_ROOT
    PROJECT_ROOT = os.path.abspath(project_root_path)
    # Ensure DATA_DIR is stored as its absolute path immediately after joining
    DATA_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'data'))

    # Asegurar que el directorio data exista
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
        print(f"utils.py: Directorio DATA_DIR creado en: {DATA_DIR}") # Log para verificar
    else:
        print(f"utils.py: Directorio DATA_DIR ya existe en: {DATA_DIR}") # Log para verificar

# Dedicated function to get the absolute DATA_DIR path reliably
def get_data_dir_abs():
    """
    Retorna la ruta absoluta del directorio DATA_DIR.
    Asegura que DATA_DIR está inicializado.
    Si no está inicializado, levanta un error de tiempo de ejecución.
    """
    if DATA_DIR is None:
        # Raising a RuntimeError is better here to signal a critical setup issue
        raise RuntimeError("DATA_DIR has not been initialized. Call initialize_paths() at application startup.")
    return DATA_DIR # DATA_DIR is already stored as absolute

# Helper function to get full path with security checks
def get_full_path(user_path):
    """
    Construye la ruta completa dentro de DATA_DIR y la valida para prevenir
    vulnerabilidades de Directory Traversal.
    Retorna la ruta absoluta si es válida, de lo contrario retorna None.
    """
    # Use the dedicated function to get the absolute DATA_DIR
    try:
        data_dir_abs = get_data_dir_abs()
    except RuntimeError as e:
        print(f"utils.py: Error in get_full_path: {e}")
        return None # Return None if DATA_DIR is not initialized

    # --- Logging para diagnóstico detallado ---
    print(f"\n--- get_full_path ---")
    print(f"Input user_path (from frontend): '{user_path}'")
    # Use the already absolute DATA_DIR for logging
    print(f"Configured DATA_DIR (absolute): '{data_dir_abs}'")


    try:
        # Si no se proporciona ninguna ruta (ej. para el directorio raíz), retornar la ruta absoluta de DATA_DIR.
        if not user_path:
            print(f"Result: user_path vacío, retornando DATA_DIR absoluto = '{data_dir_abs}'")
            print(f"--- Fin get_full_path ---\n")
            return data_dir_abs # Return the absolute DATA_DIR

        # --- CORRECCIÓN AQUÍ: Eliminar el prefijo 'data/' si existe ---
        # The frontend sends paths that already include 'data/', but we must join them to the absolute DATA_DIR path.
        # If user_path starts with 'data/', remove it to avoid duplication when joining with the absolute DATA_DIR.
        processed_user_path = user_path
        # More robust check: ensure it's the DATA_DIR prefix before removing
        # This assumes the frontend path starts with "data/" relative to the project root conceptually
        # A safer way might be to check if user_path, when made absolute relative to PROJECT_ROOT,
        # starts with DATA_DIR, but let's stick to the current logic's intent for now.
        # The existing check `processed_user_path.startswith('data/')` is probably sufficient given the frontend code.
        if processed_user_path.startswith('data/'):
            processed_user_path = processed_user_path[len('data/'):]
            print(f"Removed 'data/' prefix. Processed user_path: '{processed_user_path}'")
        elif processed_user_path == 'data': # Handle the case where user_path is just 'data'
             processed_user_path = ''
             print(f"Handled 'data' path. Processed user_path: '{processed_user_path}'")


        # Convertir las barras diagonales del frontend a separadores del sistema operativo
        os_specific_path = processed_user_path.replace('/', os.sep)
        print(f"Converted to OS specific separators: '{os_specific_path}'")

        # Normalizar la ruta específica del OS
        # Usamos os.path.normpath para manejar '..' y '.' y múltiples separadores
        # Luego strip(os.sep) para quitar cualquier separador al inicio o final
        normalized_os_path = os.path.normpath(os_specific_path).strip(os.sep)
        print(f"Normalized OS specific path: '{normalized_os_path}'")

        # Unir el DATA_DIR absoluto con la ruta normalizada específica del OS
        # Use the absolute DATA_DIR directly
        full_item_path_candidate = os.path.join(data_dir_abs, normalized_os_path)
        print(f"Candidate full path (DATA_DIR + normalized): '{full_item_path_candidate}'")

        # Obtener la ruta absoluta final y resuelta para la verificación de seguridad y existencia
        # Resolve any symlinks or complex paths relative to the filesystem root
        requested_abs = os.path.abspath(full_item_path_candidate)
        print(f"Requested absolute path: '{requested_abs}'")

        # Obtener la ruta absoluta de DATA_DIR para comparación de seguridad (DATA_DIR is already absolute)
        # data_dir_abs is already obtained above
        print(f"DATA_DIR absolute for comparison: '{data_dir_abs}'")


        # Validación de seguridad: Asegurarse de que la ruta absoluta solicitada esté dentro de DATA_DIR.
        # Convertir ambas rutas a minúsculas para comparación insensible a mayúsculas (más seguro en algunos OS)
        # Utilizamos startswith después de asegurar que requested_abs está normalizada y absoluta
        if not requested_abs.lower().startswith(data_dir_abs.lower()):
             print(f"SECURITY ALERT: Path '{requested_abs}' does NOT start with DATA_DIR '{data_dir_abs}'. Returning None.")
             print(f"--- Fin get_full_path ---\n")
             return None # La ruta está fuera de DATA_DIR, potencial intento de traversal.

        # Si la ruta pasa la validación de seguridad, es la ruta completa y válida que buscamos.
        print(f"Result: Valid path within DATA_DIR. Returning '{requested_abs}'")
        print(f"--- Fin get_full_path ---\n")
        return requested_abs

    except Exception as e:
        # Capturar cualquier error inesperado during path processing (excluding the RuntimeError from get_data_dir_abs)
        print(f"Exception in get_full_path for '{user_path}': {e}. Returning None.")
        print(f"--- Fin get_full_path ---\n")
        return None

def get_current_path_display(path):
    """
    Retorna una visualización legible de la ruta actual relativa a DATA_DIR.
    """
    # Use the dedicated function to get the absolute DATA_DIR
    try:
        data_dir_abs = get_data_dir_abs()
    except RuntimeError:
         print("utils.py: Error: DATA_DIR no inicializado al obtener la ruta para visualización.")
         return 'Error de Ruta' # Return error message if DATA_DIR is not initialized


    # If the path corresponds to the absolute DATA_DIR path, show 'data/'
    # Compare against the already absolute DATA_DIR
    if os.path.abspath(path) == data_dir_abs:
        return 'data/'

    # Obtener la ruta relativa a DATA_DIR
    try:
        # Use os.path.relpath with the absolute DATA_DIR
        relative_path = os.path.relpath(os.path.abspath(path), data_dir_abs) # Ensure path is also absolute for relpath
        # Reemplazar separadores específicos del OS con barras diagonales para visualización en URL
        display_path = relative_path.replace(os.sep, '/')
        # Añadir barra diagonal al final si es un directorio (ya manejado arriba para la raíz)
        # Solo añadir si no es la cadena vacía (que representa el directorio actual if it's DATA_DIR)
        if os.path.isdir(os.path.abspath(path)) and display_path and display_path != '.' and not display_path.endswith('/'):
             display_path += '/'
        # If relative_path is '.', display_path is '', we want 'data/'
        if display_path == '.':
             display_path = ''
        return 'data/' + display_path
    except ValueError:
        # Manejar casos donde la ruta no está dentro de DATA_DIR
        return 'Ruta Inválida'
    except Exception as e:
         # Catch any other unexpected errors during display path generation
         print(f"utils.py: Unexpected error in get_current_path_display for '{path}': {e}")
         return 'Error de Ruta'