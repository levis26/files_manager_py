import os
import shutil
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for # Added redirect, url_for
from flask_bootstrap import Bootstrap

# --- Anticopy Placeholder ---
# This string serves as a basic, easily identifiable marker.
# A real "anticopy" system is far more complex and would involve unique
# implementation details, code style, and logic flow.
PROJECT_ID = "SimpleFileManager_RenameFeature_ABC123_20250503"
# ---------------------------

app = Flask(__name__)
Bootstrap(app)
# Set a secret key for flashing messages
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Define the data directory path relative to the application file
DATA_DIR = 'data'

# Helper function to get full path with security checks
# --- Keeping this one ---
def get_full_path(user_path):
    """
    Constructs the full path within DATA_DIR and validates it to prevent
    directory traversal vulnerabilities.
    Returns the absolute path if valid, otherwise returns None.
    """
    try:
        # Si no se proporciona una ruta, devolver el directorio de datos
        if not user_path:
            return os.path.abspath(DATA_DIR)

        # Normalizar la ruta y eliminar caracteres no deseados
        # os.path.normpath handles '..' and '.' for security.
        # .strip('/') is fine as it removes leading/trailing slashes, ensuring relative paths are treated consistently.
        normalized_path = os.path.normpath(user_path).strip('/')
        
        # Unir con DATA_DIR para obtener la ruta completa
        full_path = os.path.join(DATA_DIR, normalized_path)
        
        # Obtener la ruta absoluta del directorio de datos
        data_dir_abs = os.path.abspath(DATA_DIR)
        
        # Obtener la ruta absoluta de la ruta solicitada
        requested_abs = os.path.abspath(full_path)
        
        # Verificar si la ruta solicitada está dentro del directorio de datos
        if os.path.commonpath([data_dir_abs, requested_abs]) != data_dir_abs:
            return None
            
        # Si la ruta no existe y estamos creando un nuevo directorio o archivo, permitirlo
        # Ensure the parent directory exists for creation.
        if not os.path.exists(requested_abs):
            parent_dir = os.path.dirname(requested_abs)
            # Allow creation directly in DATA_DIR or in an existing subdirectory
            if os.path.exists(parent_dir) or parent_dir == data_dir_abs:
                return requested_abs
            return None # Parent directory does not exist
            
        return requested_abs
    except Exception: # Catch all exceptions for path validation issues
        return None

# Ensure the data directory exists when the app starts
# --- Keeping this one (first occurrence) ---
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def index():
    """
    Main page displaying the file browser interface.
    """
    return render_template('index.html')

def get_current_path_display(path):
    """
    Returns a human-readable display of the current path.
    This function is used by the /api/browse endpoint to return the display path.
    """
    if not path:
        return 'data'
    
    # Get the relative path from DATA_DIR
    relative_path = os.path.relpath(path, DATA_DIR)
    
    # Split into components
    components = relative_path.split(os.sep)
    
    # Create the display path
    display_path = 'data/'
    if components and components != ['']: # Ensure components is not empty after split (e.g., for DATA_DIR itself)
        display_path += '/'.join(components)
    
    return display_path

@app.route('/api/browse')
def browse_directory():
    """
    API endpoint to browse directory contents.
    --- Keeping this one (the last, more complete definition) ---
    """
    current_path = request.args.get('path', '')
    full_current_path = get_full_path(current_path)
    
    if not full_current_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    if not os.path.exists(full_current_path):
        return jsonify({
            'success': False,
            'message': 'Path does not exist'
        })

    if not os.path.isdir(full_current_path):
        return jsonify({
            'success': False,
            'message': 'Path is not a directory'
        })

    items = []
    try:
        with os.scandir(full_current_path) as entries:
            for entry in entries:
                relative_path = os.path.relpath(entry.path, DATA_DIR)
                items.append({
                    'name': entry.name,
                    'path': relative_path, # Paths from here DO NOT start with '/'
                    'is_dir': entry.is_dir(),
                    'is_file': entry.is_file()
                })
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

    return jsonify({
        'success': True,
        'items': items,
        'current_path_display': get_current_path_display(full_current_path)
    })

@app.route('/api/get-file-content')
def get_file_content():
    """
    API endpoint to get file content.
    --- Keeping this one (only one definition exists) ---
    """
    path = request.args.get('path', '')
    full_path = get_full_path(path)
    
    if not full_path or not os.path.isfile(full_path):
        return jsonify({
            'success': False,
            'message': 'Invalid file path or not a file'
        })

    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/create_dir', methods=['POST'])
def create_directory():
    """
    API endpoint to create a new directory.
    --- Keeping this one (the last definition) ---
    """
    data = request.get_json()
    path = data.get('path', '')
    name = data.get('name', '')

    if not path or not name:
        return jsonify({
            'success': False,
            'message': 'Path and name are required'
        })

    full_path = get_full_path(os.path.join(path, name))
    if not full_path: # get_full_path ensures parent exists and path is valid for creation
        return jsonify({
            'success': False,
            'message': 'Invalid path for creation or parent directory does not exist'
        })
    
    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': f"Directory '{name}' already exists"
        })

    try:
        os.makedirs(full_path, exist_ok=False) # exist_ok=False because we check existence
        return jsonify({
            'success': True,
            'message': f"Directory '{name}' created successfully"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/create_file', methods=['POST'])
def create_file():
    """
    API endpoint to create a new file.
    --- Keeping this one (the last definition) ---
    """
    data = request.get_json()
    path = data.get('path', '')
    name = data.get('name', '')
    content = data.get('content', '')

    if not path or not name:
        return jsonify({
            'success': False,
            'message': 'Path and name are required'
        })

    full_path = get_full_path(os.path.join(path, name))
    if not full_path: # get_full_path ensures parent exists and path is valid for creation
        return jsonify({
            'success': False,
            'message': 'Invalid path for creation or parent directory does not exist'
        })

    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': f"File '{name}' already exists"
        })

    try:
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({
            'success': True,
            'message': f"File '{name}' created successfully"
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/append_file', methods=['POST'])
def append_file():
    """
    API endpoint to append content to a file.
    --- Keeping this one (the last definition) ---
    """
    data = request.get_json()
    path = data.get('path', '')
    content = data.get('content', '').strip()

    if not path:
        return jsonify({
            'success': False,
            'message': 'Path is required'
        })

    if not content:
        return jsonify({
            'success': False,
            'message': 'Content cannot be empty'
        })

    full_path = get_full_path(path)
    if not full_path or not os.path.isfile(full_path): # Ensure it's an existing file
        return jsonify({
            'success': False,
            'message': 'Invalid file path or item is not a file'
        })

    try:
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            # If the file has content, add a newline before new content
            with open(full_path, 'a', encoding='utf-8') as f:
                f.write('\n' + content)
        else:
            # If the file is empty or doesn't exist, write content directly
            with open(full_path, 'w', encoding='utf-8') as f: # Changed mode to 'w' for empty file creation
                f.write(content)

        return jsonify({
            'success': True,
            'message': 'Content appended successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/delete', methods=['POST']) # Note: endpoint name is delete
def delete_item():
    """
    API endpoint to delete a file or directory.
    --- Keeping this one (the last definition) ---
    """
    data = request.get_json()
    path = data.get('path', '')

    if not path:
        return jsonify({
            'success': False,
            'message': 'Path is required'
        })

    full_path = get_full_path(path)
    if not full_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })
    
    if not os.path.exists(full_path): # Check if item exists before trying to delete
        return jsonify({
            'success': False,
            'message': 'Item not found'
        })

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            return jsonify({
                'success': True,
                'message': f"File '{path}' deleted successfully"
            })
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)
            return jsonify({
                'success': True,
                'message': f"Directory '{path}' and its contents deleted successfully"
            })
        else: # Should not be reached if get_full_path and os.path.exists work as expected
            return jsonify({
                'success': False,
                'message': 'Item is neither a file nor a directory'
            })
    except OSError as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/rename_item', methods=['POST'])
def rename_item():
    """
    API endpoint to rename a file or directory.
    --- Keeping this one (the last API definition) ---
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos no válidos'
            })

        old_path = data.get('oldPath', '').strip()
        new_name = data.get('newName', '').strip()

        if not old_path or not new_name:
            return jsonify({
                'success': False,
                'message': 'Por favor, ingrese una ruta y un nuevo nombre'
            })

        if not new_name: # Check if new name is empty after strip()
            return jsonify({
                'success': False,
                'message': 'El nuevo nombre no puede estar vacío'
            })

        parent_dir = os.path.dirname(old_path)
        new_path = os.path.join(parent_dir, new_name)

        full_old_path = get_full_path(old_path)
        full_new_path = get_full_path(new_path) # This ensures the new path is valid and its parent exists

        if not full_old_path:
            return jsonify({
                'success': False,
                'message': f'Ruta inválida (antigua): {old_path}'
            })

        if not full_new_path:
            return jsonify({
                'success': False,
                'message': f'Ruta inválida (nueva) o directorio padre inexistente para: {new_name}'
            })

        if not os.path.exists(full_old_path):
            return jsonify({
                'success': False,
                'message': f'El archivo/directorio "{old_path}" no existe'
            })

        if os.path.exists(full_new_path):
            return jsonify({
                'success': False,
                'message': f'Ya existe un archivo/directorio con el nombre "{new_name}" en la misma ubicación'
            })

        old_parent_abs = os.path.dirname(full_old_path)
        new_parent_abs = os.path.dirname(full_new_path)
        if old_parent_abs != new_parent_abs:
            return jsonify({
                'success': False,
                'message': 'No se puede mover el archivo/directorio a un directorio diferente. Solo se permite renombrar en la misma ubicación.'
            })

        os.rename(full_old_path, full_new_path)

        return jsonify({
            'success': True,
            'message': f'Renombrado exitosamente "{old_path}" a "{new_name}"'
        })
    except OSError as e:
        return jsonify({
            'success': False,
            'message': f'Error al renombrar: {str(e)}'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        })

@app.route('/rename_item', methods=['GET', 'POST'])
def rename_item_view():
    """
    Handle renaming a file or directory via a traditional Flask view (not API).
    GET: Display the form with the current item path.
    POST: Process the rename operation.
    --- Keeping this one (it's a separate view, not an API endpoint used by main.js for modals) ---
    """
    original_path = request.args.get('item_path', '').strip()
    current_context_path = request.args.get('current_context_path', '').strip()

    if request.method == 'POST':
        original_path = request.form['original_path'].strip()
        new_name = request.form['new_name'].strip()
        current_context_path = request.form.get('current_context_path', '').strip()

        if not original_path or not new_name:
            flash("Original path and new name cannot be empty.", "error")
            return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

        full_original_path = get_full_path(original_path)

        if full_original_path is None:
            flash("Invalid original path provided.", "error")
            return redirect(url_for('index', current_path=current_context_path))

        if not os.path.exists(full_original_path):
            flash(f"Error: Original item '{original_path}' not found.", "error")
            return redirect(url_for('index', current_path=current_context_path))

        parent_dir_of_original = os.path.dirname(original_path)
        new_relative_path = os.path.join(parent_dir_of_original, new_name)
        full_new_path = get_full_path(new_relative_path)

        if full_new_path is None:
             flash("Invalid new name provided.", "error")
             return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

        if os.path.exists(full_new_path):
            flash(f"Error: An item named '{new_relative_path}' already exists.", "error")
            return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

        try:
            os.rename(full_original_path, full_new_path)
            flash(f"Item '{original_path}' renamed to '{new_relative_path}' successfully.", "success")
            return redirect(url_for('index', current_path=parent_dir_of_original))
        except OSError as e:
            flash(f"Error renaming item '{original_path}': {e}", "error")
        except Exception as e:
             flash(f"An unexpected error occurred: {e}", "error")

        return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

    full_original_path_check = get_full_path(original_path)
    if full_original_path_check is None or not os.path.exists(full_original_path_check):
         flash("Error: Item to rename not found or invalid path.", "error")
         return redirect(url_for('index', current_path=current_context_path))

    current_name = os.path.basename(original_path)

    return render_template('rename_item.html',
                           original_path=original_path,
                           current_name=current_name,
                           current_context_path=current_context_path)


@app.route('/api/search', methods=['GET'])
def search_files():
    """
    API endpoint to search files and directories.
    --- Keeping this one (only one definition exists) ---
    """
    search_term = request.args.get('term', '').lower()
    current_path = request.args.get('path', '')
    
    if not search_term:
        return jsonify({
            'success': False,
            'message': 'Por favor, ingrese un término de búsqueda'
        })

    full_current_path = get_full_path(current_path)
    
    if not full_current_path:
        return jsonify({
            'success': False,
            'message': 'Ruta no válida. Por favor, verifique la ruta actual'
        })

    if not os.path.exists(full_current_path):
        return jsonify({
            'success': False,
            'message': 'El directorio especificado no existe'
        })

    try:
        matches = []
        # Recursively search through directories
        for root, dirs, files in os.walk(full_current_path):
            # Search in directory names
            for dir_name in dirs:
                if search_term in dir_name.lower():
                    dir_path = os.path.join(root, dir_name)
                    relative_path = os.path.relpath(dir_path, DATA_DIR)
                    matches.append({
                        'name': dir_name,
                        'path': relative_path,
                        'is_dir': True,
                        'is_file': False
                    })
            
            # Search in file names
            for file_name in files:
                if search_term in file_name.lower():
                    file_path = os.path.join(root, file_name)
                    relative_path = os.path.relpath(file_path, DATA_DIR)
                    matches.append({
                        'name': file_name,
                        'path': relative_path,
                        'is_dir': False,
                        'is_file': True
                    })
        
        # Sort results: directories first, then files
        matches.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        return jsonify({
            'success': True,
            'results': matches,
            'message': f'Se encontraron {len(matches)} resultados',
            'search_term': search_term
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': f'Error al realizar la búsqueda: {str(e)}'
        })

if __name__ == '__main__':
    # Run the Flask development server.
    # debug=True enables auto-reloading and detailed error pages.
    # Set to False in a production environment.
    app.run(debug=True)