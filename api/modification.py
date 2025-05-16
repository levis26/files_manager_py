import os # El módulo 'os' es esencial aquí para interactuar con el sistema de archivos: remover, renombrar, verificar existencias, tamaños, etc.
import shutil # Importamos 'shutil' porque nos da herramientas de alto nivel para archivos, ¡como borrar directorios con todo dentro de forma recursiva!
import traceback # Este módulo es súper útil para depurar. Nos permite obtener información detallada (el "traceback") cuando ocurre un error, ¡así sabemos exactamente dónde falló algo!
from flask import Blueprint, request, jsonify # Lo básico de Flask: Blueprints para organizar rutas, request para obtener datos de las peticiones y jsonify para mandar respuestas JSON.
# Importamos nuestras funciones clave de 'utils.py':
# - get_full_path: Para asegurarnos de que cualquier ruta que nos llegue del frontend sea segura y esté dentro de nuestra carpeta 'data'.
# - get_data_dir_abs: Para obtener la ruta absoluta y segura de nuestra carpeta 'data', ¡importante para no borrarla por accidente!
from utils import get_full_path, get_data_dir_abs

# Creamos un Blueprint para todas las rutas que modifican el sistema de archivos (añadir contenido, borrar, renombrar).
# Lo llamamos 'modification_bp'.
modification_bp = Blueprint('modification_bp', __name__)

# --- Endpoint para añadir contenido a un archivo ---
# Esta ruta responde a peticiones POST en '/api/append_file'.
# La usamos cuando queremos agregar texto al final de un archivo existente.
@modification_bp.route('/api/append_file', methods=['POST'])
def append_file():
    """
    Esta función maneja las peticiones para añadir contenido al final de un archivo.
    Piensa en esto como la lógica detrás de un editor simple que solo permite agregar al final.
    """
    # Obtenemos los datos que el frontend nos envía en formato JSON.
    # Esperamos 'path' (la ruta del archivo al que añadir) y 'content' (el texto a añadir).
    data = request.get_json()
    path = data.get('path', '') # Obtenemos la ruta del archivo. Si no viene, es una cadena vacía.
    content = data.get('content', '').strip() # Obtenemos el contenido. Usamos .strip() para quitar espacios al inicio/final.

    # --- Logueo para ir viendo qué datos nos llegan ---
    print(f"\n--- /api/append_file ---")
    print(f"Ruta recibida del frontend: '{path}'")
    # Solo imprimimos una parte del contenido para no llenar el log si el texto es muy largo.
    print(f"Contenido recibido (primeros 50 chars): '{content[:50]}...'")

    # Validaciones básicas:
    # 1. ¿Nos enviaron una ruta? Si no, no sabemos a qué archivo añadir.
    if not path:
        print(f"/api/append_file: La ruta está vacía. Enviando error.")
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': 'Path is required'
        })

    # 2. ¿Nos enviaron contenido (después de quitar espacios)? Si está vacío, no hay nada que añadir.
    if not content:
        print(f"/api/append_file: El contenido está vacío después del strip. Enviando error.")
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': 'Content cannot be empty'
        })

    # ¡Hora de la seguridad! Convertimos la ruta que nos llegó a una ruta COMPLETA y SEGURA.
    # Si la ruta no es válida o intenta salirse de nuestro 'data_dir', 'get_full_path' devuelve None.
    full_path = get_full_path(path)
    print(f"/api/append_file: get_full_path devolvió: '{full_path}'")

    # Seguimos validando la ruta obtenida:
    # Verificamos que 'full_path' no sea None (ruta inválida) Y que realmente exista en el sistema.
    # --- Logueo extra para la verificación de existencia ---
    print(f"/api/append_file: Verificando existencia de '{full_path}'...")
    if not full_path or not os.path.exists(full_path):
        print(f"/api/append_file: Invalid full_path ('{full_path}') o la ruta NO existe para la ruta del frontend '{path}'. Enviando error.")
        print(f"--- Fin /api/append_file ---\n")
        # Mensaje para el frontend: decimos que la ruta es inválida o no es un archivo (para mantener la consistencia).
        return jsonify({
            'success': False,
            'message': 'Invalid file path or item is not a file'
        })
    print(f"/api/append_file: La ruta '{full_path}' existe.")

    # Y lo más importante para añadir contenido: ¡La ruta debe apuntar a un ARCHIVO, no a una carpeta!
    print(f"/api/append_file: Verificando si '{full_path}' es un archivo...")
    if not os.path.isfile(full_path):
        print(f"/api/append_file: Full path '{full_path}' NO es un archivo. Enviando error.")
        print(f"--- Fin /api/append_file ---\n")
         # El mismo mensaje para el frontend, ya que el resultado final es que no puede añadir contenido.
        return jsonify({
            'success': False,
            'message': 'Invalid file path or item is not a file'
        })
    print(f"/api/append_file: La ruta '{full_path}' es un archivo.")

    # ¡Si pasamos todas las validaciones, podemos intentar añadir el contenido!
    try:
        # Abrimos el archivo de forma segura con 'with open(...)'.
        # 'full_path': La ruta del archivo.
        # 'a': ¡Este es el modo clave! Es el modo de 'append' (añadir). Abre el archivo para escribir al final. Si no existe, lo crea.
        # 'encoding='utf-8'': Fundamental para manejar texto correctamente.
        with open(full_path, 'a', encoding='utf-8') as f:
            # Una pequeña mejora: añadimos un salto de línea antes de cada contenido que añadimos.
            # Pero solo si el archivo YA tiene algo, para que no empiece con un salto de línea vacío.
            # 'os.path.getsize' nos da el tamaño del archivo en bytes. Si es mayor que 0, tiene contenido.
            if os.path.getsize(full_path) > 0:
                 f.write('\n') # Añadimos un salto de línea.
            f.write(content) # Escribimos el contenido que nos llegó.

        print(f"/api/append_file: Contenido añadido exitosamente a '{full_path}'.")
        print(f"--- Fin /api/append_file ---\n")
        # Si todo salió bien, mandamos un mensaje de éxito. Usamos os.path.basename(path) para mostrar solo el nombre del archivo al usuario.
        return jsonify({
            'success': True,
            'message': f"Content appended to '{os.path.basename(path)}' successfully"
        })
    except OSError as e:
        # Capturamos errores específicos del sistema operativo (ej. permisos, disco lleno).
        # Es bueno diferenciar estos de otros errores generales.
        # --- Logueo robusto y traceback ---
        error_path_display = full_path if full_path is not None else 'None' # Aseguramos mostrar la ruta aunque fuera None (aunque no debería llegar aquí).
        print(f"/api/append_file: OS Error añadiendo contenido a {error_path_display}: {e}. Enviando error.")
        traceback.print_exc() # Imprimimos el traceback COMPLETO para ayudar a depurar.
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': str(e) # Enviamos el error exacto del sistema operativo.
        })
    except Exception as e:
        # Capturamos cualquier otro tipo de error inesperado que pudiera ocurrir.
        # --- Logueo robusto y traceback ---
        error_path_display = full_path if full_path is not None else 'None' # De nuevo, logueo robusto.
        print(f"/api/append_file: Error inesperado añadiendo contenido a {error_path_display}: {e}. Enviando error.")
        traceback.print_exc() # ¡Imprimimos el traceback para saber exactamente qué falló!
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}' # Un mensaje más general para el usuario.
        })

# --- Endpoint para eliminar un archivo o directorio ---
# Esta ruta responde a peticiones POST en '/api/delete'.
# Se usa tanto para borrar archivos como para borrar carpetas (¡y su contenido!).
@modification_bp.route('/api/delete', methods=['POST'])
def delete_item():
    """
    Esta función maneja las peticiones para borrar archivos o directorios.
    ¡Hay que tener cuidado con esta! :)
    """
    # Obtenemos los datos JSON. Esperamos 'path' (la ruta del elemento a borrar).
    data = request.get_json()
    path = data.get('path', '') # La ruta del archivo o carpeta a eliminar.

    # --- Logueo para ver qué elemento quieren borrar ---
    print(f"\n--- /api/delete ---")
    print(f"Ruta recibida del frontend (elemento a borrar): '{path}'")

    # Validamos que nos hayan dado una ruta.
    if not path:
        print(f"/api/delete: La ruta está vacía. Enviando error.")
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': 'Path is required'
        })

    # Obtenemos la ruta COMPLETA y SEGURA del elemento a borrar.
    full_path = get_full_path(path)
    print(f"/api/delete: get_full_path devolvió: '{full_path}'")

    # Si 'get_full_path' devolvió None, la ruta no es válida o segura.
    if not full_path:
        print(f"/api/delete: Ruta inválida después de get_full_path para '{path}'. Enviando error.")
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    # ¡Crucial! Verificamos que el elemento a borrar realmente EXISTA antes de intentar borrarlo.
    # Así evitamos errores si el frontend intenta borrar algo que ya no está.
    print(f"/api/delete: Verificando existencia de '{full_path}'...")
    if not os.path.exists(full_path):
        print(f"/api/delete: La ruta completa '{full_path}' NO existe. Enviando error.")
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': 'Item not found' # Mensaje para el frontend.
        })
    print(f"/api/delete: La ruta '{full_path}' existe.")

    # Si el elemento existe y la ruta es válida, intentamos borrarlo.
    try:
        # Comprobamos si es un archivo...
        if os.path.isfile(full_path):
            print(f"/api/delete: Intentando borrar archivo: '{full_path}'")
            os.remove(full_path) # Usamos os.remove() para borrar archivos.
            print(f"/api/delete: Archivo '{full_path}' borrado exitosamente.")
            print(f"--- Fin /api/delete ---\n")
            # Mandamos éxito con el nombre del archivo borrado.
            return jsonify({
                'success': True,
                'message': f"File '{os.path.basename(path)}' deleted successfully"
            })
        # ...o si es un directorio.
        elif os.path.isdir(full_path):
            print(f"/api/delete: Intentando borrar directorio: '{full_path}'")
            # ¡PELIGRO! No queremos que alguien pueda borrar nuestra carpeta raíz 'data'.
            # Comparamos la ruta que quieren borrar con la ruta absoluta y segura de 'data_dir'.
            # --- Usamos nuestra función segura para obtener la ruta de DATA_DIR ---
            try:
                data_dir_abs = get_data_dir_abs() # Obtenemos la ruta absoluta y verificada de DATA_DIR.
            except RuntimeError as e:
                 # Si no se inicializó DATA_DIR, es un error interno grave.
                 print(f"/api/delete: Error obteniendo la ruta absoluta de DATA_DIR: {e}. Enviando error.")
                 print(f"--- Fin /api/delete ---\n")
                 return jsonify({
                    'success': False,
                    'message': 'Internal server error: DATA_DIR not initialized' # Error interno.
                 })

            # ¡LA VERIFICACIÓN! Si la ruta a borrar es exactamente la ruta de DATA_DIR...
            if full_path == data_dir_abs: # Comparamos las rutas absolutas y seguras.
                print(f"/api/delete: Se intentó borrar el directorio raíz DATA_DIR '{full_path}'. Enviando error.")
                print(f"--- Fin /api/delete ---\n")
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete the root directory' # Mensaje de seguridad.
                })
            # Si no es la raíz, ¡usamos shutil.rmtree para borrar el directorio y TODO lo que hay dentro!
            # Esta función es recursiva.
            shutil.rmtree(full_path)
            print(f"/api/delete: Directorio '{full_path}' borrado exitosamente (incluyendo contenido).")
            print(f"--- Fin /api/delete ---\n")
            # Mandamos éxito con el nombre del directorio borrado.
            return jsonify({
                'success': True,
                'message': f"Directory '{os.path.basename(path)}' and its contents deleted successfully"
            })
        else:
            # Este caso no debería pasar si get_full_path y os.path.exists funcionaron,
            # pero es una buena medida de robustez por si acaso.
            print(f"/api/delete: El elemento en '{full_path}' no es ni archivo ni directorio. Enviando error.")
            print(f"--- Fin /api/delete ---\n")
            return jsonify({
                'success': False,
                'message': 'Item is neither a file nor a directory'
            })
    except OSError as e:
        # Capturamos errores del sistema operativo al borrar (ej. permisos, archivo en uso).
        # --- Logueo robusto y traceback ---
        error_path_display = full_path if full_path is not None else 'None' # Logueo robusto.
        print(f"/api/delete: OS Error al borrar {error_path_display}: {e}. Enviando error.")
        traceback.print_exc() # Imprimimos el traceback para depurar.
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': str(e) # Enviamos el error exacto.
        })
    except Exception as e:
        # Capturamos cualquier otro error inesperado.
        # --- Logueo robusto y traceback ---
        error_path_display = full_path if full_path is not None else 'None' # Logueo robusto.
        print(f"/api/delete: Error inesperado al borrar {error_path_display}: {e}. Enviando error.")
        traceback.print_exc() # ¡Traceback completo!
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}' # Mensaje general.
        })

# --- Endpoint para renombrar un archivo o directorio ---
# Esta ruta responde a peticiones POST en '/api/rename_item'.
# Por ahora, solo permite renombrar elementos dentro del MISMO directorio.
@modification_bp.route('/api/rename_item', methods=['POST'])
def rename_item():
    """
    Esta función maneja las peticiones para renombrar archivos o directorios.
    Importante: Esta implementación solo permite cambiar el nombre, no moverlo a otro lugar.
    """
    # Usamos un try general aquí porque la validación inicial de data también puede fallar.
    try:
        # Obtenemos los datos JSON. Esperamos 'oldPath' (la ruta actual del elemento)
        # y 'newName' (el nuevo nombre que queremos ponerle).
        data = request.get_json()
        # Si no llega data o no es JSON, get_json() podría devolver None.
        if not data:
            print(f"\n--- /api/rename_item ---")
            print(f"Recibida data vacía. Enviando error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': 'Datos no válidos' # Mensaje claro para el frontend.
            })

        old_path = data.get('oldPath', '').strip() # La ruta original del elemento. Usamos strip().
        new_name = data.get('newName', '').strip() # El nuevo nombre deseado. Usamos strip().

        # --- Logueo para ver qué nos llegó ---
        print(f"\n--- /api/rename_item ---")
        print(f"oldPath recibida del frontend: '{old_path}'")
        print(f"newName recibido del frontend: '{new_name}'")

        # Validaciones básicas:
        # 1. ¿Tenemos la ruta original Y un nuevo nombre?
        if not old_path or not new_name:
            print(f"/api/rename_item: oldPath o newName están vacíos. Enviando error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': 'Por favor, ingrese una ruta y un nuevo nombre' # Mensaje útil.
            })

        # 2. ¿El nuevo nombre no está vacío después de quitar espacios?
        if not new_name: # Redundante si ya validamos arriba, pero más seguro si newName solo contiene espacios.
            print(f"/api/rename_item: newName está vacío después del strip. Enviando error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': 'El nuevo nombre no puede estar vacío'
            })

        # Para renombrar DENTRO del mismo directorio, necesitamos saber cuál es ese directorio padre.
        # 'os.path.dirname()' nos da la parte del "directorio" de una ruta.
        parent_dir_of_old_path = os.path.dirname(old_path)
        print(f"/api/rename_item: Directorio padre de oldPath: '{parent_dir_of_old_path}'")

        # Construimos la ruta COMPLETA que tendría el elemento CON EL NUEVO NOMBRE PERO EN EL MISMO DIRECTORIO padre.
        # Usamos 'os.path.join' para unir la ruta del padre con el nuevo nombre.
        new_path_in_same_dir = os.path.join(parent_dir_of_old_path, new_name)
        print(f"/api/rename_item: Ruta candidata con el nuevo nombre en el mismo dir: '{new_path_in_same_dir}'")

        # Ahora, ¡obtenemos las rutas COMPLETA y SEGURA para AMBOS caminos!
        # Es crucial que la NUEVA ruta también pase por 'get_full_path' para asegurar que no estamos renombrando
        # hacia una ubicación fuera de 'data_dir' usando '..'.
        full_old_path = get_full_path(old_path) # Ruta completa y segura del elemento original.
        full_new_path = get_full_path(new_path_in_same_dir) # Ruta completa y segura del elemento con el nuevo nombre.

        print(f"/api/rename_item: get_full_path(old_path) devolvió: '{full_old_path}'")
        print(f"/api/rename_item: get_full_path(new_path_in_same_dir) devolvió: '{full_new_path}'")

        # Validamos que la ruta original (segura) sea válida (no None).
        if not full_old_path:
            print(f"/api/rename_item: full_old_path inválida después de get_full_path para '{old_path}'. Enviando error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'Ruta inválida (antigua): {old_path}'
            })

        # Validamos que el elemento original realmente exista antes de intentar renombrarlo.
        print(f"/api/rename_item: Verificando existencia de la ruta antigua '{full_old_path}'...")
        if not os.path.exists(full_old_path):
            print(f"/api/rename_item: La ruta antigua completa '{full_old_path}' NO existe. Enviando error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'El archivo/directorio "{old_path}" no existe'
            })
        print(f"/api/rename_item: La ruta antigua '{full_old_path}' existe.")

        # Validamos que la NUEVA ruta (segura) también sea válida (no None).
        # Si 'get_full_path' para la nueva ruta dio None, significa que el 'newName' o la combinación
        # con el padre no era válida dentro de 'data_dir'.
        if not full_new_path:
            print(f"/api/rename_item: full_new_path inválida después de get_full_path para '{new_path_in_same_dir}'. Enviando error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'Ruta inválida (nueva): {new_name}' # Mensaje para el frontend.
            })

        # ¡MUY IMPORTANTE! Verificamos que NO exista ya un elemento con el nuevo nombre en esa ubicación.
        # No queremos sobrescribir nada.
        print(f"/api/rename_item: Verificando existencia de la ruta nueva '{full_new_path}'...")
        if os.path.exists(full_new_path):
            print(f"/api/rename_item: La ruta nueva completa '{full_new_path}' ya existe. Enviando error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'Ya existe un archivo/directorio con el nombre "{new_name}" en la misma ubicación'
            })
        print(f"/api/rename_item: La ruta nueva '{full_new_path}' no existe (¡bien!).")


        # Si pasamos todas las validaciones... ¡a renombrar!
        print(f"/api/rename_item: Intentando renombrar '{full_old_path}' a '{full_new_path}'")
        os.rename(full_old_path, full_new_path) # Usamos os.rename() para renombrar.
        print(f"/api/rename_item: Renombrado exitoso de '{full_old_path}' a '{full_new_path}'.")
        print(f"--- Fin /api/rename_item ---\n")

        # Si todo salió bien, mandamos éxito con los nombres original y nuevo.
        return jsonify({
            'success': True,
            'message': f'Renombrado exitosamente "{os.path.basename(old_path)}" a "{new_name}"'
        })
    except OSError as e:
        # Capturamos errores del sistema operativo al renombrar (ej. permisos, archivo en uso).
        # --- Logueo robusto y traceback ---
        # Aseguramos que mostramos las rutas en el log aunque fueran None (no deberían llegar aquí, pero por seguridad).
        error_old_path_display = full_old_path if full_old_path is not None else 'None'
        error_new_path_display = full_new_path if full_new_path is not None else 'None'
        print(f"/api/rename_item: OS Error al renombrar {error_old_path_display} a {error_new_path_display}: {e}. Enviando error.")
        traceback.print_exc() # Imprimimos el traceback.
        print(f"--- Fin /api/rename_item ---\n")
        return jsonify({
            'success': False,
            'message': f'Error al renombrar: {str(e)}' # Enviamos el error exacto.
        })
    except Exception as e:
        # Capturamos cualquier otro error inesperado durante el proceso de renombrar.
        # --- Logueo robusto y traceback ---
        error_old_path_display = full_old_path if full_old_path is not None else 'None'
        error_new_path_display = full_new_path if full_new_path is not None else 'None'
        print(f"/api/rename_item: Error inesperado al renombrar {error_old_path_display} a {error_new_path_display}: {e}. Enviando error.")
        traceback.print_exc() # ¡Traceback completo!
        print(f"--- Fin /api/rename_item ---\n")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}' # Mensaje general.
        })