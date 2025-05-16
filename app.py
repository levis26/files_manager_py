# api/app.py
import os
from flask import Flask, render_template

# Importar Blueprints desde el paquete api
from api.browse import browse_bp
from api.file_content import file_content_bp
from api.creation import creation_bp
from api.modification import modification_bp
from api.search import search_bp

# Importar la función de inicialización de rutas y la función para obtener DATA_DIR.
# Es VITAL que importemos get_data_dir_abs() aquí para poder usarla.
# YA NO importamos DATA_DIR directamente aquí, ya que su valor global está en utils
# y se obtiene de forma segura con get_data_dir_abs().
from utils import initialize_paths, get_data_dir_abs # <-- ¡ESTA ES LA LÍNEA CORREGIDA!

# --- Espacio Reservado para Anticopia ---
# Este string sirve como un marcador básico y fácil de identificar.
# Un sistema "anticopia" real es mucho más complejo e involucraría detalles únicos
# de implementación, estilo de código y flujo lógico.
PROJECT_ID = "SimpleFileManager_RenameFeature_ABC123_20250503"
# ---------------------------

# Creamos la instancia de nuestra aplicación Flask. ¡Esto es el inicio de todo!
app = Flask(__name__)
# Bootstrap(app) # Comentado, si se usara Flask-Bootstrap, se descomentaría.
# La clave secreta es importante para la seguridad (sesiones, mensajes flash).
# Debe ser un valor difícil de adivinar y secreto.
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Clave secreta (usada principalmente para flash messages)

# --- ¡Paso CRUCIAL! Inicializar las rutas ANTES de registrar los Blueprints ---
# Esto configura de forma segura dónde está nuestra carpeta 'data' en el sistema de archivos.
# Obtenemos la ruta absoluta del directorio donde se encuentra este archivo 'app.py'.
app_dir = os.path.dirname(os.path.abspath(__file__))
# Llamamos a la función de utilidades y le pasamos la ruta raíz de nuestro proyecto.
initialize_paths(app_dir)

# Opcional: Verificar la ruta de DATA_DIR después de la inicialización.
# Ahora obtenemos el valor seguro llamando a la función get_data_dir_abs().
# Esto demuestra que la inicialización funcionó y que la función se importó bien.
print(f"app.py: DATA_DIR configurado en: {get_data_dir_abs()}") # <-- Esta línea ahora debería funcionar

# --- Registrar Blueprints ---
# Conectamos cada Blueprint (grupo de rutas de API) a la aplicación Flask principal.
app.register_blueprint(browse_bp)
app.register_blueprint(file_content_bp)
app.register_blueprint(creation_bp)
app.register_blueprint(modification_bp)
app.register_blueprint(search_bp)


# --- Ruta principal ---
# Define la ruta para la página de inicio ('/').
@app.route('/')
def index():
    """
    Maneja la solicitud para la página principal y renderiza el HTML de la interfaz.
    """
    # Renderiza el archivo 'index.html' que contiene la estructura de la interfaz.
    return render_template('index.html')

# Nota: Las funciones de ayuda como get_full_path y get_current_path_display
# se encuentran en 'utils.py' y se importan en los archivos de Blueprint que las necesitan.

# --- Bloque de ejecución principal ---
# Esto asegura que el servidor solo arranque si ejecutas este archivo directamente.
if __name__ == '__main__':
    # Inicia el servidor de desarrollo de Flask.
    # debug=True es útil para el desarrollo (recarga automática, errores detallados).
    # ¡Cambia a False en producción!
    app.run(debug=True)