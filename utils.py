import os # Este módulo es nuestro mejor amigo para todo lo relacionado con el sistema de archivos y rutas. ¡Lo necesitamos para todo!
import shutil # Importamos 'shutil', aunque en este archivo no lo usamos directamente, se importa aquí porque está relacionado con operaciones de archivos que otras partes del proyecto sí usan (como borrar directorios recursivamente en modification.py).

# --- Variables Globales Clave ---
# Estas variables guardarán la ruta absoluta de nuestra carpeta 'data' y la ruta raíz del proyecto.
# Las definimos como globales para que cualquier función en cualquier parte de la aplicación pueda acceder a ellas una vez que se inicializan.
# Inicialmente son None porque todavía no sabemos dónde está la carpeta 'data' hasta que la aplicación arranca y llama a 'initialize_paths'.
DATA_DIR = None # Aquí guardaremos la ruta COMPLETA y ABSOLUTA de nuestra carpeta 'data'.
PROJECT_ROOT = None # Aquí guardaremos la ruta COMPLETA y ABSOLUTA de la carpeta raíz del proyecto (donde está app.py).

# --- Función de Inicialización CRUCIAL ---
# Esta función es VITAL. Debe llamarse UNA VEZ al inicio de la aplicación (generalmente desde app.py).
# Su trabajo es descubrir dónde está la carpeta 'data' y guardar su ruta de forma segura en la variable global DATA_DIR.
def initialize_paths(project_root_path):
    """
    Esta función inicializa las variables globales PROJECT_ROOT y DATA_DIR.
    Recibe la ruta de la carpeta donde está app.py (la raíz del proyecto).
    DATA_DIR se calcula y se almacena como una ruta absoluta, ¡siempre segura!
    """
    # Para poder modificar las variables globales DATA_DIR y PROJECT_ROOT dentro de esta función, debemos usar la palabra clave 'global'.
    global DATA_DIR, PROJECT_ROOT

    # Obtenemos la ruta absoluta de la raíz del proyecto que nos pasaron. Esto evita problemas si el script se ejecuta desde un lugar diferente.
    PROJECT_ROOT = os.path.abspath(project_root_path)

    # Construimos la ruta completa a la carpeta 'data' uniendo la ruta raíz del proyecto con 'data'.
    # ¡Y la convertimos inmediatamente a su ruta absoluta! Esto garantiza que DATA_DIR SIEMPRE sea una ruta absoluta y limpia.
    DATA_DIR = os.path.abspath(os.path.join(PROJECT_ROOT, 'data'))

    # Ahora, verificamos si la carpeta 'data' realmente existe en el sistema de archivos.
    if not os.path.exists(DATA_DIR):
        # Si no existe, ¡la creamos! 'os.makedirs' es genial porque crea también los directorios padres si fuera necesario.
        os.makedirs(DATA_DIR)
        print(f"utils.py: Directorio DATA_DIR creado en: {DATA_DIR}") # Log para confirmar que la creamos.
    else:
        print(f"utils.py: Directorio DATA_DIR ya existe en: {DATA_DIR}") # Log para confirmar que ya estaba ahí.

# --- Función para obtener la ruta de DATA_DIR de forma segura ---
# Esta función es la forma recomendada de obtener la ruta de DATA_DIR en otras partes del código.
# Asegura que DATA_DIR ya haya sido inicializado.
def get_data_dir_abs():
    """
    Devuelve la ruta absoluta y segura de nuestra carpeta 'data'.
    Lanza un error si 'initialize_paths' no se llamó antes.
    """
    # Verificamos si la variable global DATA_DIR todavía es None. Si lo es, significa que initialize_paths no se ejecutó.
    if DATA_DIR is None:
        # Lanzamos un RuntimeError. Este tipo de error es bueno para indicar problemas graves de configuración o de que algo no se llamó en el orden correcto.
        raise RuntimeError("DATA_DIR no ha sido inicializado. Llama a initialize_paths() al inicio de la aplicación (ej. en app.py).")
    # Si DATA_DIR no es None, significa que ya está inicializado y contiene la ruta absoluta segura.
    return DATA_DIR # Devolvemos la ruta absoluta de DATA_DIR.

# --- Función CLAVE de Seguridad: Obtener y Validar Ruta Completa ---
# Esta es una de las funciones más importantes para la seguridad.
# Convierte una ruta que viene del usuario (del frontend) a una ruta completa y ABSOLUTA en el sistema de archivos,
# ¡PERO solo si esa ruta está DENTRO de nuestra carpeta 'data'!
def get_full_path(user_path):
    """
    Recibe una ruta 'user_path' (ej: 'documentos/mi_archivo.txt' o '../otro_lugar').
    Construye la ruta completa combinándola con DATA_DIR.
    Realiza comprobaciones de seguridad para PREVENIR ataques de "Directory Traversal" (intentos de salirse de DATA_DIR).
    Devuelve la ruta absoluta final si es segura y válida, de lo contrario, devuelve None.
    """
    # Primero, obtenemos la ruta absoluta y segura de DATA_DIR usando nuestra función dedicada.
    try:
        data_dir_abs = get_data_dir_abs()
    except RuntimeError as e:
        # Si DATA_DIR no estaba inicializado al llamar a esta función, logueamos el error y devolvemos None.
        print(f"utils.py: Error en get_full_path: {e}")
        return None # Si DATA_DIR no está listo, no podemos validar nada.

    # --- Logueo para ver el proceso de validación de rutas ---
    print(f"\n--- get_full_path ---")
    print(f"Ruta de usuario de entrada (del frontend): '{user_path}'")
    # Mostramos la ruta absoluta de DATA_DIR que usaremos como base.
    print(f"DATA_DIR configurado (absoluto): '{data_dir_abs}'")

    try:
        # Caso especial: Si la ruta de usuario está vacía, significa que el frontend quiere la raíz de 'data'.
        # En este caso, devolvemos directamente la ruta absoluta de DATA_DIR.
        if not user_path:
            print(f"Resultado: user_path vacío, devolviendo DATA_DIR absoluto = '{data_dir_abs}'")
            print(f"--- Fin get_full_path ---\n")
            return data_dir_abs # ¡La raíz es válida!

        # --- ¡CORRECCIÓN/AJUSTE aquí! ---
        # El frontend a menudo envía rutas que *ya* empiezan conceptualmente con 'data/' (ej: 'data/documentos/archivo').
        # Como nosotros vamos a unir la ruta recibida con la RUTA ABSOLUTA de DATA_DIR (ej: '/home/usuario/mi_app/data'),
        # si la ruta recibida empieza con 'data/', tendríamos algo como '/home/usuario/mi_app/data/data/documentos/archivo', lo cual está mal.
        # Esta parte del código intenta quitar ese prefijo 'data/' si existe para que la unión con el DATA_DIR absoluto sea correcta.
        processed_user_path = user_path
        # Comprobamos si la ruta recibida empieza con 'data/' (usando una barra '/' sin importar el OS, ya que viene del frontend).
        # NOTA: La robustez total de esta verificación depende de cómo el frontend construya las rutas.
        if processed_user_path.startswith('data/'):
            processed_user_path = processed_user_path[len('data/'):] # Quitamos el prefijo 'data/'.
            print(f"Prefijo 'data/' eliminado. Ruta de usuario procesada: '{processed_user_path}'")
        elif processed_user_path == 'data': # También manejamos el caso exacto en que la ruta sea solo 'data'.
             processed_user_path = '' # Si es solo 'data', la ruta relativa procesada es la cadena vacía (la raíz).
             print(f"Ruta 'data' manejada. Ruta de usuario procesada: '{processed_user_path}'")


        # Las rutas que vienen del frontend usan barras diagonales '/'. Los sistemas operativos pueden usar diferentes separadores ('\' en Windows).
        # Convertimos las barras diagonales a las barras correctas del sistema operativo.
        os_specific_path = processed_user_path.replace('/', os.sep)
        print(f"Convertido a separadores específicos del OS: '{os_specific_path}'")

        # Normalizamos la ruta específica del OS.
        # 'os.path.normpath()' limpia la ruta: maneja '.' (directorio actual), '..' (directorio padre), y múltiples barras (ej: 'a//b' -> 'a/b').
        # '.strip(os.sep)' quita cualquier separador al principio o final (evitando que alguien ponga '/../').
        normalized_os_path = os.path.normpath(os_specific_path).strip(os.sep)
        print(f"Ruta específica del OS normalizada: '{normalized_os_path}'")

        # Ahora, unimos la ruta ABSOLUTA de DATA_DIR con la parte de la ruta de usuario ya limpia y normalizada.
        # Esto nos da la ruta completa potencial dentro de nuestra carpeta 'data'.
        full_item_path_candidate = os.path.join(data_dir_abs, normalized_os_path)
        print(f"Ruta completa candidata (DATA_DIR + normalizada): '{full_item_path_candidate}'")

        # ¡Última y MÁS IMPORTANTE verificación de seguridad!
        # Convertimos la ruta candidata a su ruta absoluta final y resuelta. Esto resuelve cualquier '..' remanente o enlaces simbólicos.
        # Luego, comparamos esta ruta ABSOLUTA final con la ruta ABSOLUTA de DATA_DIR.
        # Si la ruta solicitada NO EMPIEZA con la ruta de DATA_DIR, significa que el usuario intentó salirse de nuestra carpeta 'data'.
        # Convertimos a minúsculas (.lower()) para que la comparación funcione igual en sistemas que no distinguen mayúsculas/minúsculas.
        requested_abs = os.path.abspath(full_item_path_candidate) # Obtenemos la ruta absoluta y resuelta final.
        print(f"Ruta absoluta solicitada (final): '{requested_abs}'")
        print(f"DATA_DIR absoluto para comparación: '{data_dir_abs}'")


        if not requested_abs.lower().startswith(data_dir_abs.lower()):
             # ¡Alerta de seguridad! La ruta intentó salirse de DATA_DIR.
             print(f"ALERTA DE SEGURIDAD: La ruta '{requested_abs}' NO empieza con DATA_DIR '{data_dir_abs}'. Devolviendo None.")
             print(f"--- Fin get_full_path ---\n")
             return None # Devolvemos None para indicar que la ruta no es segura.

        # Si pasamos esta verificación, la ruta es segura y válida dentro de DATA_DIR.
        print(f"Resultado: Ruta válida dentro de DATA_DIR. Devolviendo '{requested_abs}'")
        print(f"--- Fin get_full_path ---\n")
        return requested_abs # Devolvemos la ruta absoluta y segura.

    except Exception as e:
        # Capturamos cualquier otro error inesperado durante el procesamiento de la ruta (aparte del error de inicialización de DATA_DIR).
        print(f"Excepción inesperada en get_full_path para '{user_path}': {e}. Devolviendo None.")
        print(f"--- Fin get_full_path ---\n")
        return None # Si hay un error, consideramos la ruta no válida.

# --- Función para mostrar la ruta de forma legible en el frontend ---
# Esta función toma una ruta COMPLETA y ABSOLUTA y la convierte en un formato más amigable para el usuario,
# relativo a 'data/' (ej: 'data/documentos/').
def get_current_path_display(path):
    """
    Recibe una ruta 'path' (que debería ser una ruta absoluta válida dentro de DATA_DIR).
    Devuelve una cadena de texto amigable para mostrar en el frontend, como 'data/subcarpeta/'.
    """
    # Obtenemos la ruta absoluta de DATA_DIR de forma segura.
    try:
        data_dir_abs = get_data_dir_abs()
    except RuntimeError:
         # Si DATA_DIR no está inicializado, no podemos formatear la ruta.
         print("utils.py: Error: DATA_DIR no inicializado al obtener la ruta para visualización.")
         return 'Error de Ruta' # Devolvemos un mensaje de error.


    # Si la ruta que nos pasaron es exactamente la ruta absoluta de DATA_DIR...
    # Es decir, si estamos en el directorio raíz de 'data'.
    if os.path.abspath(path) == data_dir_abs:
        return 'data/' # Mostramos simplemente 'data/' en el frontend.

    # Si no estamos en la raíz, calculamos la ruta relativa a DATA_DIR.
    try:
        # 'os.path.relpath(path, start)' calcula la ruta para ir desde 'start' hasta 'path'.
        # Le pasamos la ruta actual (asegurándonos de que sea absoluta) y la ruta absoluta de DATA_DIR como punto de inicio.
        relative_path = os.path.relpath(os.path.abspath(path), data_dir_abs)
        # Las rutas relativas que devuelve os.path.relpath usan los separadores del OS.
        # Los reemplazamos por barras diagonales '/' para que se vean bien en la URL y en el frontend.
        display_path = relative_path.replace(os.sep, '/')

        # Añadimos una barra diagonal al final si la ruta original era un directorio (y no la raíz o '.').
        # Esto ayuda a diferenciar visualmente carpetas de archivos en la visualización de la ruta.
        if os.path.isdir(os.path.abspath(path)) and display_path and display_path != '.' and not display_path.endswith('/'):
             display_path += '/'

        # Si la ruta relativa es '.' (que a veces ocurre si path ya era DATA_DIR), la mostramos como vacía para la unión.
        if display_path == '.':
             display_path = ''
        # Finalmente, anteponemos 'data/' a la ruta relativa formateada para la visualización final.
        return 'data/' + display_path
    except ValueError:
        # Este error puede ocurrir si la ruta 'path' no está contenida dentro de 'data_dir_abs'.
        # Si get_full_path se usó correctamente, esta excepción no debería ocurrir, pero la manejamos por robustez.
        return 'Ruta Inválida' # Si la ruta no es válida en relación a DATA_DIR, mostramos un error.
    except Exception as e:
         # Capturamos cualquier otro error inesperado al formatear la ruta para mostrar.
         print(f"utils.py: Error inesperado en get_current_path_display para '{path}': {e}")
         return 'Error de Ruta' # Mensaje genérico de error de ruta.