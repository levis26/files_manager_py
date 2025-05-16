import os # De nuevo, necesitamos el módulo 'os' para hablar con el sistema de archivos: crear carpetas, archivos, verificar si existen, etc.
from flask import Blueprint, request, jsonify # Importamos lo básico de Flask para las rutas API y manejar las peticiones y respuestas en JSON.
from utils import get_full_path # ¡Importante! Traemos nuestra función de 'utils' para asegurarnos de que las rutas sean seguras y absolutas.

# Creamos otro Blueprint, esta vez para agrupar todas las rutas que tienen que ver con la creación
# (crear directorios y crear archivos). Lo llamamos 'creation_bp'.
creation_bp = Blueprint('creation_bp', __name__)

# --- Endpoint para crear un directorio ---
# Definimos una ruta API que responderá a peticiones POST en '/api/create_dir'.
# Usamos POST porque estamos enviando datos (el nombre de la carpeta y dónde crearla)
# para hacer un cambio en el servidor (crear algo).
@creation_bp.route('/api/create_dir', methods=['POST'])
def create_directory():
    """
    Esta función maneja las peticiones para crear nuevos directorios.
    Es como el cerebro detrás del botón "Crear Carpeta" en el frontend.
    """
    # Cuando el frontend envía una petición POST con JSON, 'request.get_json()' lo extrae.
    # Aquí esperamos un diccionario con 'path' (dónde crearla, puede ser la raíz '') y 'name' (el nombre de la nueva carpeta).
    data = request.get_json()
    path = data.get('path', '') # Obtenemos la ruta del directorio padre. Si no viene, asumimos la raíz.
    name = data.get('name', '') # Obtenemos el nombre que queremos para la nueva carpeta.

    # Primero, una validación simple: ¿Nos dieron un nombre para la carpeta?
    # Si el nombre está vacío, ¡no podemos crear nada! Mandamos un error.
    if not name:
        return jsonify({
            'success': False,
            'message': 'Name is required' # Mensaje para el frontend.
        })

    # Ok, tenemos nombre. Ahora, construimos la ruta COMPLETA donde debería estar la nueva carpeta.
    # 'os.path.join' es genial porque une partes de ruta de forma correcta sin importar si estás en Windows, Linux, etc.
    new_dir_relative_path = os.path.join(path, name) # Esto nos da la ruta relativa (ej: 'documentos/nueva_carpeta').
    # ¡Pero necesitamos la ruta ABSOLUTA y SEGURA! Para eso, usamos nuestra fiel 'get_full_path'.
    full_path = get_full_path(new_dir_relative_path)

    # Antes de crear la carpeta, vamos a verificar que el directorio padre (donde queremos crearla) sea válido y exista.
    # De nuevo, usamos 'get_full_path' para el padre y 'os.path.isdir' para verificar si es un directorio existente.
    full_parent_path = get_full_path(path)

    # Si la ruta del padre no es válida (get_full_path devolvió None) o si no es un directorio existente...
    if not full_parent_path or not os.path.isdir(full_parent_path):
         return jsonify({
            'success': False,
            'message': 'Invalid parent directory path or parent does not exist' # Error específico para el padre.
        })

    # También verificamos que la ruta COMPLETA de la nueva carpeta sea válida dentro de nuestro 'DATA_DIR'.
    # Si el nombre o la combinación de ruta+nombre era "mala", 'get_full_path' ya nos habría dado None para 'full_path'.
    if not full_path:
         return jsonify({
            'success': False,
            'message': 'Invalid new directory name or path' # Error si la ruta final no es válida.
        })

    # Ahora, una comprobación crucial: ¿Ya existe algo (un archivo o una carpeta) con ese nombre en ese lugar?
    # No queremos sobrescribir accidentalmente algo o causar un error.
    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': f"Directory '{name}' already exists in this location" # Error si ya existe.
        })

    # ¡Si pasamos todas las validaciones, podemos intentar crear la carpeta!
    try:
        # 'os.makedirs' es genial porque si las carpetas "padre" de la nueva ruta no existen, ¡también las crea!
        # 'exist_ok=False' le dice que lance un error si la carpeta ya existe. Como ya lo comprobamos antes, esto es seguro.
        os.makedirs(full_path, exist_ok=False)
        # Si llegamos aquí, ¡todo bien! Mandamos un mensaje de éxito.
        return jsonify({
            'success': True,
            'message': f"Directory '{name}' created successfully"
        })
    except Exception as e:
        # Si ocurre *cualquier* otro error al intentar crear la carpeta (ej. permisos, nombre raro, etc.)...
        # Capturamos el error y lo imprimimos en consola para saber qué pasó.
        print(f"Error creating directory {full_path}: {e}")
        # Y le enviamos la descripción del error al frontend.
        return jsonify({
            'success': False,
            'message': str(e)
        })

# --- Endpoint para crear un archivo ---
# Similar a crear directorio, esta ruta maneja peticiones POST a '/api/create_file'.
@creation_bp.route('/api/create_file', methods=['POST'])
def create_file():
    """
    Esta función maneja las peticiones para crear nuevos archivos.
    Es el motor detrás del botón "Crear Archivo".
    """
    # Obtenemos los datos JSON del frontend. Esperamos 'path' (directorio donde crearlo),
    # 'name' (nombre del archivo) y 'content' (el texto que irá dentro del archivo).
    data = request.get_json()
    path = data.get('path', '') # Ruta del directorio padre (puede ser la raíz).
    name = data.get('name', '') # Nombre que queremos para el nuevo archivo.
    content = data.get('content', '') # El contenido que tendrá el archivo.

    # Validamos que al menos nos den un nombre para el archivo.
    if not name:
        return jsonify({
            'success': False,
            'message': 'Name is required' # Mensaje para el frontend.
        })

    # Construimos la ruta COMPLETA y SEGURA para el nuevo archivo, igual que con las carpetas.
    new_file_relative_path = os.path.join(path, name)
    full_path = get_full_path(new_file_relative_path)

    # Verificamos que el directorio padre sea válido y exista, igual que antes.
    full_parent_path = get_full_path(path)
    if not full_parent_path or not os.path.isdir(full_parent_path):
         return jsonify({
            'success': False,
            'message': 'Invalid parent directory path or parent does not exist' # Error para el padre.
        })

    # Verificamos que la ruta COMPLETA para el nuevo archivo sea válida dentro de 'DATA_DIR'.
    if not full_path:
         return jsonify({
            'success': False,
            'message': 'Invalid new file name or path' # Error si la ruta final no es válida.
        })

    # Comprobamos si ya existe algo con ese nombre en esa ubicación.
    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': f"File '{name}' already exists in this location" # Error si ya existe un archivo o carpeta con ese nombre.
        })

    # ¡Todo validado! Intentamos crear el archivo y escribir el contenido.
    try:
        # 'with open(...) as f:' es la forma segura de abrir y cerrar archivos en Python.
        # 'full_path': La ruta donde crear el archivo.
        # 'w': Modo de escritura ('w' significa "write"). Si el archivo no existe, lo crea; si existe, LO BORRA y crea uno nuevo (¡ojo!).
        # 'encoding='utf-8'': Es MUY importante especificar la codificación para evitar problemas con caracteres especiales. UTF-8 es el estándar.
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content) # Escribimos el contenido que nos llegó del frontend en el archivo.

        # ¡Archivo creado y escrito exitosamente!
        return jsonify({
            'success': True,
            'message': f"File '{name}' created successfully"
        })
    except Exception as e:
        # Si hay algún error al crear o escribir el archivo (ej. permisos, disco lleno, nombre inválido, etc.)...
        # Imprimimos el error en consola.
        print(f"Error creating file {full_path}: {e}")
        # Y enviamos el error al frontend.
        return jsonify({
            'success': False,
            'message': str(e)
        })