import os # Necesitamos 'os' para interactuar con el sistema de archivos, ¡especialmente para buscar directorios y archivos de forma recursiva!
from flask import Blueprint, request, jsonify # Lo de siempre de Flask: Blueprint para organizar, request para coger los datos de la búsqueda y jsonify para la respuesta JSON.
from utils import get_full_path # Importamos get_full_path para verificar y convertir la ruta de inicio de la búsqueda a una ruta absoluta y segura.

# Creamos un Blueprint específico para las funcionalidades de búsqueda.
# Lo llamamos 'search_bp'. Esto nos ayuda a mantener el código ordenado por temática.
search_bp = Blueprint('search_bp', __name__)

# --- Endpoint para realizar una búsqueda ---
# Esta ruta API responde a peticiones GET en '/api/search'.
# Usamos GET porque estamos pidiendo información (los resultados de la búsqueda), no estamos modificando nada en el servidor.
@search_bp.route('/api/search', methods=['GET'])
def search_files():
    """
    Este es el endpoint de la API que se encarga de buscar archivos y directorios.
    Cuando escribes algo en la barra de búsqueda del frontend, la petición llega aquí.
    """
    # Obtenemos el término de búsqueda que el frontend nos envía en los parámetros de la URL ('term').
    # Lo convertimos a minúsculas de inmediato (.lower()) para que la búsqueda no distinga mayúsculas de minúsculas.
    search_term = request.args.get('term', '').lower()
    # También obtenemos la ruta desde donde empezar la búsqueda ('path'). Si no viene, asumimos la raíz.
    current_path = request.args.get('path', '')

    # --- Logueo para ver qué término y ruta de inicio nos llegaron ---
    print(f"\n--- /api/search ---")
    print(f"Término de búsqueda recibido: '{search_term}'")
    print(f"Ruta de inicio de búsqueda recibida del frontend: '{current_path}'")

    # Validamos: si el término de búsqueda está vacío, no podemos buscar nada.
    if not search_term:
        print(f"/api/search: El término de búsqueda está vacío. Enviando error.")
        print(f"--- Fin /api/search ---\n")
        return jsonify({
            'success': False, # Indicamos que falló.
            'message': 'Por favor, ingrese un término de búsqueda' # Mensaje para el usuario.
        })

    # Validamos y convertimos la ruta de inicio de la búsqueda a una ruta COMPLETA y SEGURA.
    # Si la ruta del frontend era "mala", 'get_full_path' devolverá None.
    full_current_path = get_full_path(current_path)
    print(f"/api/search: get_full_path devolvió: '{full_current_path}'")

    # Si la ruta de inicio de la búsqueda no es válida, mandamos un error.
    if not full_current_path:
        print(f"/api/search: Ruta inválida después de get_full_path para '{current_path}'. Enviando error.")
        print(f"--- Fin /api/search ---\n")
        return jsonify({
            'success': False,
            'message': 'Ruta de búsqueda no válida. Por favor, verifique la ruta actual'
        })

    # --- Verificamos que la ruta de inicio de la búsqueda realmente exista ---
    print(f"/api/search: Verificando existencia de la ruta de búsqueda '{full_current_path}'...")
    if not os.path.exists(full_current_path):
        print(f"/api/search: La ruta de búsqueda '{full_current_path}' NO existe. Enviando error.")
        print(f"--- Fin /api/search ---\n")
        return jsonify({
            'success': False,
            'message': 'El directorio especificado para la búsqueda no existe'
        })
    print(f"/api/search: La ruta de búsqueda '{full_current_path}' existe.")

    # Si todo lo anterior está bien, ¡podemos empezar la búsqueda!
    try:
        # Creamos una lista vacía donde guardaremos todos los resultados que coincidan.
        matches = []
        # --- ¡La magia de la búsqueda recursiva! ---
        # 'os.walk()' es una función increíble que recorre un directorio
        # Y TODOS sus subdirectorios, uno por uno.
        # En cada iteración, nos da:
        # - 'root': La ruta del directorio actual que está visitando.
        # - 'dirs': Una lista con los nombres de los subdirectorios DENTRO de 'root'.
        # - 'files': Una lista con los nombres de los archivos DENTRO de 'root'.
        print(f"/api/search: Iniciando búsqueda recursiva desde '{full_current_path}'...")
        for root, dirs, files in os.walk(full_current_path):
            # --- Buscamos coincidencias en los nombres de los directorios ---
            for dir_name in dirs:
                # Convertimos el nombre del directorio a minúsculas y vemos si el término de búsqueda está dentro.
                if search_term in dir_name.lower():
                    # Si coincide, construimos la ruta completa de este directorio encontrado.
                    dir_path = os.path.join(root, dir_name)
                    # Necesitamos la ruta relativa a nuestro 'DATA_DIR' para mostrarla correctamente en el frontend.
                    # Aquí hay algo a tener en cuenta: el código está recalculando la ruta de DATA_DIR usando os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data')).
                    # Esto puede ser un poco arriesgado si la estructura de carpetas cambia o si el script se ejecuta desde un lugar inesperado.
                    # Idealmente, se debería acceder a la variable global DATA_DIR que se inicializa de forma segura al inicio de la aplicación en utils.py.
                    # Pero como no debemos cambiar la funcionalidad, mantenemos el código original y solo lo comentamos.
                    relative_path = os.path.relpath(dir_path, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))) # <-- ¡Ojo! Esto recalcula DATA_DIR.

                    # Añadimos la información del directorio encontrado a nuestra lista de resultados.
                    matches.append({
                        'name': dir_name, # El nombre del directorio.
                        'path': relative_path.replace(os.sep, '/'), # La ruta relativa con barras web '/'
                        'is_dir': True, # Confirmamos que es un directorio.
                        'is_file': False # No es un archivo.
                    })

            # --- Buscamos coincidencias en los nombres de los archivos ---
            for file_name in files:
                # Hacemos lo mismo que con los directorios: convertimos el nombre del archivo a minúsculas y buscamos el término.
                if search_term in file_name.lower():
                    # Si coincide, construimos la ruta completa de este archivo encontrado.
                    file_path = os.path.join(root, file_name)
                    # De nuevo, calculamos la ruta relativa para el frontend.
                    # Recordar la nota sobre recalcular DATA_DIR aquí.
                    relative_path = os.path.relpath(file_path, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))) # <-- ¡Ojo! Recalculando DATA_DIR de nuevo.

                    # Añadimos la información del archivo encontrado a nuestra lista de resultados.
                    matches.append({
                        'name': file_name, # El nombre del archivo.
                        'path': relative_path.replace(os.sep, '/'), # La ruta relativa con barras web '/'
                        'is_dir': False, # No es un directorio.
                        'is_file': True # Confirmamos que es un archivo.
                    })

        # Después de recorrer todo, ordenamos los resultados.
        # Ponemos las carpetas primero, luego los archivos, y dentro de cada grupo, por nombre alfabéticamente (sin importar mayúsculas/minúsculas).
        matches.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

        print(f"/api/search: Búsqueda completada. Encontrados {len(matches)} resultados para '{search_term}'.")
        print(f"--- Fin /api/search ---\n")

        # Preparamos la respuesta exitosa con los resultados.
        return jsonify({
            'success': True, # ¡Todo bien!
            'results': matches, # La lista de coincidencias encontradas.
            'message': f'Se encontraron {len(matches)} resultados para "{search_term}"', # Un mensaje amigable para el usuario.
            'search_term': search_term # También devolvemos el término por si el frontend lo necesita.
        })
    except Exception as e:
        # Si ocurre algún error inesperado durante la búsqueda (ej. permisos, archivo corrupto), lo capturamos.
        print(f"/api/search: Error durante la búsqueda desde {full_current_path} con el término '{search_term}': {e}. Enviando error.")
        print(f"--- Fin /api/search ---\n")
        # Enviamos un mensaje de error al frontend.
        return jsonify({
            'success': False,
            'message': f'Error al realizar la búsqueda: {str(e)}' # Descripción del error.
        })
