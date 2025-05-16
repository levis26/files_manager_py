import os # Una vez más, 'os' es nuestro amigo para interactuar con los archivos en el sistema.
from flask import Blueprint, request, jsonify # Lo usual de Flask: Blueprint para organizar, request para ver qué nos pide el navegador, jsonify para mandar respuestas en JSON.
from utils import get_full_path # Importamos nuestra función de 'utils' para estar seguros con las rutas. ¡La seguridad primero!

# Creamos un Blueprint específico para las operaciones relacionadas con el contenido de los archivos.
# Así mantenemos nuestro código modular y fácil de manejar. Lo llamamos 'file_content_bp'.
file_content_bp = Blueprint('file_content_bp', __name__)

# --- Endpoint para obtener el contenido de un archivo ---
# Definimos una ruta API. Cuando el frontend (por ejemplo, al hacer clic en un archivo para previsualizarlo)
# hace una petición GET a '/api/get-file-content' con la ruta del archivo en los parámetros,
# se ejecutará la función de abajo.
@file_content_bp.route('/api/get-file-content')
def get_file_content():
    """
    Este endpoint sirve para que el frontend nos pida el contenido de un archivo específico.
    Piensa en esto como la parte del backend que lee el archivo para mostrarlo en la previsualización.
    """
    # Obtenemos la ruta del archivo que el frontend nos envía en los parámetros de la URL ('path').
    # Si no viene nada, usamos una cadena vacía, aunque para leer un archivo necesitamos una ruta.
    path = request.args.get('path', '')
    # --- Logueo para depurar y ver qué ruta llegó ---
    print(f"\n--- /api/get-file-content ---")
    print(f"Ruta recibida del frontend: '{path}'")

    # ¡Paso crucial! Usamos 'get_full_path' para convertir la ruta recibida (que es relativa y podría ser maliciosa)
    # en una ruta completa y segura dentro de nuestra carpeta 'data'. Si la ruta no es válida o intenta salirse,
    # 'get_full_path' nos dará None.
    full_path = get_full_path(path)
    print(f"/api/get-file-content: get_full_path devolvió: '{full_path}'")

    # Validamos que la ruta obtenida sea válida Y que el archivo realmente exista en el sistema.
    # Si 'full_path' es None (ruta inválida) o si 'os.path.exists' dice que no existe...
    # --- Logueo extra para saber por qué falló ---
    print(f"/api/get-file-content: Verificando existencia de '{full_path}'...")
    if not full_path or not os.path.exists(full_path):
         print(f"/api/get-file-content: full_path inválida ('{full_path}') o la ruta NO existe para la ruta del frontend '{path}'. Enviando error.")
         print(f"--- Fin /api/get-file-content ---\n")
         return jsonify({
            'success': False, # Indicamos que falló.
            'message': 'Invalid file path or not a file' # Mensaje genérico para el frontend.
        })
    print(f"/api/get-file-content: La ruta '{full_path}' existe.")

    # Ahora que sabemos que la ruta existe y es segura, ¡tenemos que verificar que sea un ARCHIVO!
    # No podemos leer el contenido de una carpeta.
    print(f"/api/get-file-content: Verificando si '{full_path}' es un archivo...")
    if not os.path.isfile(full_path):
         print(f"/api/get-file-content: La ruta completa '{full_path}' NO es un archivo. Enviando error.")
         print(f"--- Fin /api/get-file-content ---\n")
         return jsonify({
            'success': False,
            'message': 'Invalid file path or not a file' # El mismo mensaje, ya que para el frontend el resultado es el mismo: no puede obtener el contenido.
        })
    print(f"/api/get-file-content: La ruta '{full_path}' es un archivo.")

    # Si hemos llegado hasta aquí, la ruta es válida, existe y apunta a un archivo. ¡Perfecto!
    # Intentamos leer su contenido. Usamos un bloque try...except por si hay problemas al leer el archivo (ej. permisos).
    try:
        # Abrimos el archivo de forma segura con 'with open(...) as f:'. Python se encargará de cerrarlo automáticamente.
        # 'full_path': La ruta del archivo a abrir.
        # 'r': Modo de lectura ('read').
        # 'encoding='utf-8'': Vital para leer archivos de texto y manejar correctamente tildes, eñes y otros caracteres.
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read() # Leemos todo el contenido del archivo de una vez.

        print(f"/api/get-file-content: Contenido leído exitosamente de '{full_path}'.")
        print(f"--- Fin /api/get-file-content ---\n")
        # Si la lectura fue exitosa, mandamos una respuesta con el contenido.
        return jsonify({
            'success': True, # ¡Éxito!
            'content': content # Aquí va el contenido del archivo.
        })
    except Exception as e:
        # Si algo falla al leer el archivo (ej. no tenemos permisos, el archivo está corrupto, etc.)...
        # Capturamos el error, lo imprimimos en la consola del servidor para depurar.
        print(f"/api/get-file-content: Error leyendo el archivo {full_path}: {e}. Enviando error.")
        print(f"--- Fin /api/get-file-content ---\n")
        # Y le mandamos un mensaje de error al frontend con la descripción del problema.
        return jsonify({
            'success': False,
            'message': str(e) # Convertimos el error a cadena para enviarlo.
        })