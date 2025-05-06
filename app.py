import os
import shutil
from flask import Flask, render_template, request, jsonify, flash
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
        if not os.path.exists(requested_abs):
            parent_dir = os.path.dirname(requested_abs)
            if os.path.exists(parent_dir):
                return requested_abs
            return None
            
        return requested_abs
    except Exception:
        return None

# Ensure the data directory exists when the app starts
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

@app.route('/')
def index():
    return render_template('index.html', current_context_path='')

def get_current_path_display(path):
    """
    Returns a human-readable display of the current path
    """
    if not path:
        return 'data'
    
    # Get the relative path from DATA_DIR
    relative_path = os.path.relpath(path, DATA_DIR)
    
    # Split into components
    components = relative_path.split(os.sep)
    
    # Create the display path
    display_path = 'data/'
    if components:
        display_path += '/'.join(components)
    
    return display_path

@app.route('/api/browse')
def browse_directory():
    current_path = request.args.get('path', '')
    full_current_path = get_full_path(current_path)
    
    if not full_current_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    try:
        items = []
        for item in os.listdir(full_current_path):
            item_path = os.path.join(full_current_path, item)
            
            # Get the relative path from DATA_DIR
            relative_path = os.path.relpath(item_path, DATA_DIR)
            
            # Ensure the relative path starts with a slash
            if not relative_path.startswith('/'):
                relative_path = '/' + relative_path
            
            items.append({
                'name': item,
                'path': relative_path,
                'is_dir': os.path.isdir(item_path),
                'is_file': os.path.isfile(item_path)
            })
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

        return jsonify({
            'success': True,
            'items': items,
            'current_path_display': get_current_path_display(full_current_path)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/create_directory', methods=['POST'])
def create_directory():
    data = request.get_json()
    path = data.get('path', '')
    name = data.get('name', '')
    
    if not name:
        return jsonify({
            'success': False,
            'message': 'Name is required'
        })

    full_path = get_full_path(os.path.join(path, name))
    
    if not full_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    try:
        os.makedirs(full_path)
        return jsonify({
            'success': True,
            'message': 'Directory created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/create_file', methods=['POST'])
def create_file():
    data = request.get_json()
    path = data.get('path', '')
    name = data.get('name', '')
    content = data.get('content', '')
    
    if not name:
        return jsonify({
            'success': False,
            'message': 'Name is required'
        })

    full_path = get_full_path(os.path.join(path, name))
    
    if not full_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    try:
        with open(full_path, 'w') as f:
            f.write(content)
        return jsonify({
            'success': True,
            'message': 'File created successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/append_file', methods=['POST'])
def append_file():
    data = request.get_json()
    path = data.get('path', '')
    content = data.get('content', '')
    
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

    try:
        with open(full_path, 'a') as f:
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

@app.route('/api/delete_item', methods=['POST'])
def delete_item():
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

    try:
        if os.path.isdir(full_path):
            shutil.rmtree(full_path)
        else:
            os.remove(full_path)
        return jsonify({
            'success': True,
            'message': 'Item deleted successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/rename_item', methods=['POST'])
def rename_item():
    data = request.get_json()
    old_path = data.get('old_path', '')
    new_name = data.get('new_name', '')
    
    if not old_path or not new_name:
        return jsonify({
            'success': False,
            'message': 'Path and new name are required'
        })

    old_full_path = get_full_path(old_path)
    new_full_path = get_full_path(os.path.join(os.path.dirname(old_path), new_name))
    
    if not old_full_path or not new_full_path:
        return jsonify({
            'success': False,
            'message': 'Invalid paths'
        })

    try:
        os.rename(old_full_path, new_full_path)
        return jsonify({
            'success': True,
            'message': 'Item renamed successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'message': str(e)
        })

if __name__ == '__main__':
    app.run(debug=True)

# Ensure the data directory exists when the app starts
if not os.path.exists(DATA_DIR):
    os.makedirs(DATA_DIR)

def get_full_path(user_path):
    """
    Constructs the full path within DATA_DIR and validates it to prevent
    directory traversal vulnerabilities.
    Returns the absolute path if valid, otherwise returns None.
    """
    # Basic security: Reject paths starting with '/' or '..'
    if user_path.startswith('/') or user_path.startswith('..'):
         return None # Invalid path attempt

    # Join data directory and user input path
    # Use os.path.normpath to normalize the path (e.g., resolve './')
    full_path = os.path.normpath(os.path.join(DATA_DIR, user_path))

    # More robust security: Resolve absolute paths and check if they are
    # truly within the absolute path of DATA_DIR.
    try:
        abs_data_dir = os.path.abspath(DATA_DIR)
        abs_full_path = os.path.abspath(full_path)

        # Check if the resolved path starts with the absolute data directory path
        # and is not just the data directory itself if the user input was empty or '.'
        # Add os.sep to ensure it's inside a subdirectory, not just the data dir itself
        # unless the path is the data directory itself.
        if not abs_full_path.startswith(abs_data_dir + os.sep) and abs_full_path != abs_data_dir:
            return None # Path is outside DATA_DIR

        return abs_full_path
    except Exception as e:
        # Log any exceptions during path validation
        print(f"Path validation error for user path '{user_path}': {e}")
        return None


@app.route('/')
def index():
    """
    Main page displaying the file browser interface.
    """
    return render_template('index.html')

@app.route('/api/browse')
def browse_directory():
    """
    API endpoint to browse directory contents.
    """
    current_path = request.args.get('path', '')
    full_current_path = os.path.join(DATA_DIR, current_path)
    abs_full_current_path = os.path.abspath(full_current_path)
    abs_data_dir = os.path.abspath(DATA_DIR)

    if not os.path.exists(abs_full_current_path) or not abs_full_current_path.startswith(abs_data_dir):
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    if not os.path.isdir(abs_full_current_path):
        return jsonify({
            'success': False,
            'message': 'Path is not a directory'
        })

    items = []
    try:
        with os.scandir(abs_full_current_path) as entries:
            for entry in entries:
                relative_path = os.path.relpath(entry.path, DATA_DIR)
                items.append({
                    'name': entry.name,
                    'path': relative_path,
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
        'currentPath': current_path,
        'items': items
    })

@app.route('/api/create_dir', methods=['POST'])
def create_directory():
    """
    API endpoint to create a new directory.
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
    if not full_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    try:
        os.makedirs(full_path, exist_ok=True)
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
    if not full_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    try:
        with open(full_path, 'w') as f:
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
    """
    data = request.get_json()
    path = data.get('path', '')
    content = data.get('content', '').strip()  # Eliminar espacios en blanco al inicio y final

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
    if not full_path:
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    try:
        # Verificar si el archivo existe y tiene contenido
        if os.path.exists(full_path) and os.path.getsize(full_path) > 0:
            # Si el archivo tiene contenido, agregar una nueva línea antes del contenido nuevo
            with open(full_path, 'a') as f:
                f.write('\n' + content)
        else:
            # Si el archivo está vacío, escribir el contenido directamente
            with open(full_path, 'w') as f:
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

@app.route('/api/delete', methods=['POST'])
def delete_item():
    """
    API endpoint to delete a file or directory.
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
        else:
            return jsonify({
                'success': False,
                'message': 'Item not found'
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
    # If the path doesn't exist or isn't a file/directory (e.g., a broken symlink)
    flash(f"Error: '{item_path}' not found or is not a file/directory.", "error")

    # If there was an error, redirect back to the form, preserving context
    return redirect(url_for('delete_item', current_context_path=current_context_path))

    # For GET request, render the form template.
    return render_template('delete_item.html', current_context_path=current_context_path)

@app.route('/rename_item', methods=['GET', 'POST'])
def rename_item():
    """
    Handle renaming a file or directory.
    GET: Display the form with the current item path.
    POST: Process the rename operation.
    """
    # Get the original item path from query parameters for GET request
    original_path = request.args.get('item_path', '').strip()
    # Get the context path (directory we were viewing) for redirects
    current_context_path = request.args.get('current_context_path', '').strip()


    if request.method == 'POST':
        # Get original and new paths from form data for POST request
        original_path = request.form['original_path'].strip()
        new_name = request.form['new_name'].strip()
        current_context_path = request.form.get('current_context_path', '').strip() # Get context path for POST

        if not original_path or not new_name:
            flash("Original path and new name cannot be empty.", "error")
            # Redirect back to the rename form with original path and context
            return redirect(url_for('rename_item', item_path=original_path, current_context_path=current_context_path))

        # Construct the full original path and validate it
        full_original_path = get_full_path(original_path)

        if full_original_path is None:
            flash("Invalid original path provided.", "error")
            return redirect(url_for('index', current_path=current_context_path)) # Redirect to context or root

        # Check if the original item exists
        if not os.path.exists(full_original_path):
            flash(f"Error: Original item '{original_path}' not found.", "error")
            return redirect(url_for('index', current_path=current_context_path)) # Redirect to context or root

        # Determine the parent directory of the original item
        parent_dir_of_original = os.path.dirname(original_path)

        # Construct the full new path using the parent directory of the original item
        # This prevents moving the item to a different directory during rename
        new_relative_path = os.path.join(parent_dir_of_original, new_name)
        full_new_path = get_full_path(new_relative_path)


        if full_new_path is None:
             flash("Invalid new name provided.", "error")
             # Redirect back to the rename form with original path and context
             return redirect(url_for('rename_item', item_path=original_path, current_context_path=current_context_path))


        # Prevent renaming if the new path already exists
        if os.path.exists(full_new_path):
            flash(f"Error: An item named '{new_relative_path}' already exists.", "error")
            # Redirect back to the rename form with original path and context
            return redirect(url_for('rename_item', item_path=original_path, current_context_path=current_context_path))


        try:
            # Perform the rename operation
            os.rename(full_original_path, full_new_path)
            flash(f"Item '{original_path}' renamed to '{new_relative_path}' successfully.", "success")
            # Redirect back to the parent directory where the rename happened
            return redirect(url_for('index', current_path=parent_dir_of_original))
        except OSError as e:
            flash(f"Error renaming item '{original_path}': {e}", "error")
        except Exception as e:
             flash(f"An unexpected error occurred: {e}", "error")

        # If there was an error, redirect back to the rename form
        return redirect(url_for('rename_item', item_path=original_path, current_context_path=current_context_path))


    # For GET request, render the form template.
    # We need to ensure the original_path is valid before displaying the form
    full_original_path_check = get_full_path(original_path)
    if full_original_path_check is None or not os.path.exists(full_original_path_check):
         flash("Error: Item to rename not found or invalid path.", "error")
         return redirect(url_for('index', current_path=current_context_path)) # Redirect to context or root

    # Extract just the current name from the original path for the form placeholder
    current_name = os.path.basename(original_path)

    return render_template('rename_item.html',
                           original_path=original_path,
                           current_name=current_name,
                           current_context_path=current_context_path)


if __name__ == '__main__':
    # Run the Flask development server.
    # debug=True enables auto-reloading and detailed error pages.
    # Set to False in a production environment.
    app.run(debug=True)


# Añadir esta nueva ruta para manejar búsquedas
@app.route('/api/search', methods=['GET'])
def search_files():
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