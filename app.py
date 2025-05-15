import os
from flask import Flask, render_template

# Importar Blueprints desde el paquete api
from api.browse import browse_bp
from api.file_content import file_content_bp
from api.creation import creation_bp
from api.modification import modification_bp
from api.search import search_bp

# Importar la función de inicialización de rutas desde utils.py
from utils import initialize_paths, DATA_DIR # También importamos DATA_DIR para el log inicial


# --- Anticopy Placeholder ---
# This string serves as a basic, easily identifiable marker.
# A real "anticopy" system is far more complex and would involve unique
# implementation details, code style, and logic flow.
PROJECT_ID = "SimpleFileManager_RenameFeature_ABC123_20250503"
# ---------------------------

app = Flask(__name__)
# Bootstrap(app) # Comentado
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Clave secreta para mensajes flash (aunque usamos principalmente alertas JS)

# --- Inicializar las rutas ANTES de registrar los Blueprints ---
# Obtener la ruta del directorio donde se encuentra app.py
app_dir = os.path.dirname(os.path.abspath(__file__))
initialize_paths(app_dir) # Pasar la ruta del directorio de app.py a utils

# Opcional: Verificar la ruta de DATA_DIR después de la inicialización
print(f"app.py: DATA_DIR configurado en: {DATA_DIR}")


# Registrar Blueprints
app.register_blueprint(browse_bp)
app.register_blueprint(file_content_bp)
app.register_blueprint(creation_bp)
app.register_blueprint(modification_bp)
app.register_blueprint(search_bp)


@app.route('/')
def index():
    """
    Página principal que muestra la interfaz del navegador de archivos.
    """
    return render_template('index.html')

# Nota: Las funciones de ayuda como get_full_path y get_current_path_display
# ahora se encuentran en utils.py y se importan donde son necesarias.

if __name__ == '__main__':
    # Ejecutar el servidor de desarrollo de Flask.
    # debug=True habilita la recarga automática y páginas de error detalladas.
    # Establecer a False en un entorno de producción.
    app.run(debug=True)
