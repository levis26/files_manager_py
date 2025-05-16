# api/browse.py
import os
from flask import Blueprint, request, jsonify
# Importar las funciones necesarias desde utils.
# Es VITAL que importemos get_data_dir_abs() aquí para poder usarla dentro de browse_directory
# y obtener la ruta de DATA_DIR de forma segura.
# YA NO importamos DATA_DIR directamente aquí.
from utils import get_full_path, get_current_path_display, get_data_dir_abs # <-- ¡VERIFICA QUE ESTA LÍNEA ESTÉ ASÍ!

browse_bp = Blueprint('browse_bp', __name__)

@browse_bp.route('/api/browse')
def browse_directory():
    """
    API endpoint para explorar el contenido de un directorio.
    Recibe la ruta relativa desde el frontend.
    """
    current_path = request.args.get('path', '')
    # --- Logging para diagnóstico ---
    print(f"\n--- /api/browse ---")
    print(f"Recibida la ruta actual del frontend: '{current_path}'")

    # Obtener la ruta completa y validada usando la función de utilidad.
    # Si la ruta no es válida, get_full_path devuelve None.
    full_current_path = get_full_path(current_path)
    print(f"/api/browse: get_full_path nos devolvió: '{full_current_path}'")

    # Si get_full_path devuelve None, la ruta no es válida o segura.
    if not full_current_path:
        print(f"/api/browse: Ruta inválida después de get_full_path para '{current_path}'. Enviando error.")
        print(f"--- Fin /api/browse ---\n")
        return jsonify({
            'success': False,
            'message': 'Ruta no válida' # Mensaje de error para el frontend.
        })

    # --- Verificaciones de existencia y tipo de ruta ---
    print(f"/api/browse: Verificando si '{full_current_path}' existe...")
    if not os.path.exists(full_current_path):
        print(f"/api/browse: La ruta completa '{full_current_path}' NO existe. Enviando error.")
        print(f"--- Fin /api/browse ---\n")
        return jsonify({
            'success': False,
            'message': 'La ruta no existe' # Mensaje de error para el frontend.
        })
    print(f"/api/browse: La ruta '{full_current_path}' existe.")

    print(f"/api/browse: Verificando si '{full_current_path}' es un directorio...")
    if not os.path.isdir(full_current_path):
        print(f"/api/browse: La ruta completa '{full_current_path}' NO es un directorio. Enviando error.")
        print(f"--- Fin /api/browse ---\n")
        return jsonify({
            'success': False,
            'message': 'La ruta no es un directorio' # Mensaje de error para el frontend.
        })
    print(f"/api/browse: La ruta '{full_current_path}' es un directorio.")

    # Si todo está bien, procedemos a listar el contenido.
    items = []
    try:
        # Usamos os.scandir para listar de forma eficiente.
        with os.scandir(full_current_path) as entries:
            # ¡Paso CRUCIAL! Obtenemos la ruta absoluta y segura de DATA_DIR usando nuestra función.
            # Esto es necesario para calcular la ruta relativa de cada elemento.
            data_dir_abs = get_data_dir_abs() # <-- ¡VERIFICA QUE ESTA LÍNEA ESTÉ ASÍ!

            for entry in entries:
                # Obtenemos la ruta relativa de cada elemento listado con respecto a DATA_DIR.
                # Usamos os.path.relpath con la ruta absoluta de DATA_DIR obtenida por la función.
                relative_path = os.path.relpath(entry.path, data_dir_abs) # <-- ¡VERIFICA QUE ESTA LÍNEA USE data_dir_abs!

                items.append({
                    'name': entry.name, # Nombre del archivo o directorio.
                    # La ruta que enviamos al frontend debe ser relativa a DATA_DIR y usar barras diagonales.
                    'path': relative_path.replace(os.sep, '/'), # Reemplazamos separadores del OS por '/' para URLs.
                    'is_dir': entry.is_dir(), # Indicamos si es un directorio.
                    'is_file': entry.is_file() # Indicamos si es un archivo.
                })
        # Ordenamos los resultados: directorios primero, luego archivos, ambos alfabéticamente.
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        print(f"/api/browse: Lista de {len(items)} elementos cargada exitosamente en '{full_current_path}'.")

    except Exception as e:
        # Capturamos CUALQUIER error que ocurra durante la lectura del directorio o procesamiento.
        # Logueamos el error detalladamente en el terminal del servidor.
        print(f"/api/browse: Error al listar el directorio {full_current_path}: {e}")
        print(f"--- Fin /api/browse ---\n")
        # Enviamos un mensaje de error genérico al frontend.
        return jsonify({
            'success': False,
            'message': f'Error al cargar el directorio: {str(e)}' # Enviamos el error al frontend.
        })

    # Si todo salió bien, enviamos la respuesta de éxito con la lista de items y la ruta formateada para mostrar.
    print(f"/api/browse: Enviando respuesta exitosa para '{current_path}'.")
    print(f"--- Fin /api/browse ---\n")
    return jsonify({
        'success': True,
        'items': items, # La lista de archivos y directorios.
        'current_path_display': get_current_path_display(full_current_path) # La ruta formateada para el frontend.
    })