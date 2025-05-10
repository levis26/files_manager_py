import os
import shutil
from flask import Flask, render_template, request, jsonify, flash, redirect, url_for
# from flask_bootstrap import Bootstrap # Comentado, ya que no es estrictamente necesario para la API

# --- Anticopy Placeholder ---
PROJECT_ID = "SimpleFileManager_RenameFeature_ABC123_20250503"
# ---------------------------

app = Flask(__name__)
# Bootstrap(app) # Comentado
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/' # Clave secreta para mensajes flash (aunque usamos principalmente alertas JS)

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
        # If no path is provided (e.g., for the root directory), return the absolute DATA_DIR.
        if not user_path:
            return os.path.abspath(DATA_DIR)

        # Normalize the path: resolve '..' and '.', and remove redundant separators.
        # .strip('/') ensures the path is truly relative to DATA_DIR if it was provided with leading/trailing slashes.
        normalized_path = os.path.normpath(user_path).strip('/')
        
        # Join DATA_DIR with the normalized user path to get the full intended path.
        full_item_path = os.path.join(DATA_DIR, normalized_path)
        
        # Get the absolute path of DATA_DIR for comparison.
        data_dir_abs = os.path.abspath(DATA_DIR)
        
        # Get the absolute, resolved path of the user's requested item.
        requested_abs = os.path.abspath(full_item_path)
        
        # Crucial security check: Ensure the requested absolute path is within DATA_DIR.
        # os.path.commonpath returns the longest common sub-path. If it's not DATA_DIR itself,
        # it means the requested path is outside DATA_DIR (e.g., via '..').
        if os.path.commonpath([data_dir_abs, requested_abs]) != data_dir_abs:
            return None # Path is outside DATA_DIR, potentially a traversal attempt.

        # If the path is valid and within DATA_DIR, return its absolute form.
        # Existence check is done by the calling function (e.g., os.path.exists() in delete_item).
        return requested_abs
    except Exception:
        # Catch any unexpected errors during path processing (e.g., invalid characters).
        return None

# Ensure the data directory exists when the app starts
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
    # Handle the case where relative_path is just '.' for the root
    if components and components != ['.']:
        display_path += '/'.join(components)
    
    return display_path

@app.route('/api/browse')
def browse_directory():
    """
    API endpoint to browse directory contents.
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
        # Use os.scandir for efficiency
        with os.scandir(full_current_path) as entries:
            for entry in entries:
                # Get the path relative to the DATA_DIR for frontend use
                relative_path = os.path.relpath(entry.path, DATA_DIR)
                items.append({
                    'name': entry.name,
                    # The path sent to the frontend should be relative to DATA_DIR
                    'path': relative_path,
                    'is_dir': entry.is_dir(),
                    'is_file': entry.is_file()
                })
        # Sort directories first, then files, both alphabetically
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    except Exception as e:
        # Log the error on the server side
        print(f"Error browsing directory {full_current_path}: {e}")
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
    """
    path = request.args.get('path', '')
    full_path = get_full_path(path)
    
    # Validate path and ensure it's an existing file
    if not full_path or not os.path.isfile(full_path):
        return jsonify({
            'success': False,
            'message': 'Invalid file path or not a file'
        })

    try:
        # Read file content with UTF-8 encoding
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        print(f"Error getting file content for {full_path}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/create_dir', methods=['POST'])
def create_directory():
    """
    API endpoint to create a new directory.
    """
    data = request.get_json()
    path = data.get('path', '') # This is the parent directory path (can be "")
    name = data.get('name', '') # This is the new directory name

    # --- MODIFICACIÓN AQUÍ: Permitir path vacío para la raíz ---
    if not name: # Only require name to be non-empty
        return jsonify({
            'success': False,
            'message': 'Name is required' # Changed message for clarity
        })

    # Construct the full path for the new directory
    new_dir_relative_path = os.path.join(path, name)
    full_path = get_full_path(new_dir_relative_path)
    
    # Check if the parent directory is valid and exists
    # If path is "", get_full_path("") returns the absolute DATA_DIR.
    full_parent_path = get_full_path(path)

    # Ensure the parent path is valid and is a directory
    if not full_parent_path or not os.path.isdir(full_parent_path):
         return jsonify({
            'success': False,
            'message': 'Invalid parent directory path or parent does not exist'
        })

    # Check if the full path for the new directory is valid (within DATA_DIR)
    if not full_path:
         return jsonify({
            'success': False,
            'message': 'Invalid new directory name or path'
        })

    # Check if an item with the same name already exists at the target location
    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': f"Directory '{name}' already exists in this location"
        })

    try:
        os.makedirs(full_path, exist_ok=False) # exist_ok=False because we check existence above
        return jsonify({
            'success': True,
            'message': f"Directory '{name}' created successfully"
        })
    except Exception as e:
        print(f"Error creating directory {full_path}: {e}")
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
    path = data.get('path', '') # This is the parent directory path (can be "")
    name = data.get('name', '') # This is the new file name
    content = data.get('content', '')

    # --- MODIFICACIÓN AQUÍ: Permitir path vacío para la raíz ---
    if not name: # Only require name to be non-empty
        return jsonify({
            'success': False,
            'message': 'Name is required' # Changed message for clarity
        })

    # Construct the full path for the new file
    new_file_relative_path = os.path.join(path, name)
    full_path = get_full_path(new_file_relative_path)

    # Check if the parent directory is valid and exists
    full_parent_path = get_full_path(path)
    if not full_parent_path or not os.path.isdir(full_parent_path):
         return jsonify({
            'success': False,
            'message': 'Invalid parent directory path or parent does not exist'
        })

    # Check if the full path for the new file is valid (within DATA_DIR)
    if not full_path:
         return jsonify({
            'success': False,
            'message': 'Invalid new file name or path'
        })

    # Check if an item with the same name already exists at the target location
    if os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': f"File '{name}' already exists in this location"
        })

    try:
        # Create file with write mode and UTF-8 encoding
        with open(full_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return jsonify({
            'success': True,
            'message': f"File '{name}' created successfully"
        })
    except Exception as e:
        print(f"Error creating file {full_path}: {e}")
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
    path = data.get('path', '') # This is the file path
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
    # Check if path is valid AND points to an existing file
    if not full_path or not os.path.isfile(full_path):
        return jsonify({
            'success': False,
            'message': 'Invalid file path or item is not a file'
        })

    try:
        # Append content with UTF-8 encoding
        with open(full_path, 'a', encoding='utf-8') as f:
            # Add a newline only if the file is not empty to avoid leading newlines
            if os.path.getsize(full_path) > 0:
                 f.write('\n')
            f.write(content)

        return jsonify({
            'success': True,
            'message': f"Content appended to '{os.path.basename(path)}' successfully"
        })
    except Exception as e:
        print(f"Error appending to file {full_path}: {e}")
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
    path = data.get('path', '') # This is the path of the item to delete

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
    
    # --- Crucial check: Ensure the item to be deleted actually exists ---
    if not os.path.exists(full_path):
        return jsonify({
            'success': False,
            'message': 'Item not found'
        })

    try:
        if os.path.isfile(full_path):
            os.remove(full_path)
            return jsonify({
                'success': True,
                'message': f"File '{os.path.basename(path)}' deleted successfully"
            })
        elif os.path.isdir(full_path):
            # Prevent accidental deletion of the root DATA_DIR
            if full_path == os.path.abspath(DATA_DIR):
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete the root directory'
                })
            shutil.rmtree(full_path) # Recursive deletion
            return jsonify({
                'success': True,
                'message': f"Directory '{os.path.basename(path)}' and its contents deleted successfully"
            })
        else:
            # Should not be reached if get_full_path and os.path.exists work as expected,
            # but good for robustness.
            return jsonify({
                'success': False,
                'message': 'Item is neither a file nor a directory'
            })
    except OSError as e:
        print(f"OS Error deleting {full_path}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        print(f"Unexpected error deleting {full_path}: {e}")
        return jsonify({
            'success': False,
            'message': str(e)
        })

@app.route('/api/rename_item', methods=['POST'])
def rename_item():
    """
    API endpoint to rename a file or directory.
    Note: This implementation only allows renaming within the same directory.
    """
    try:
        data = request.get_json()
        if not data:
            return jsonify({
                'success': False,
                'message': 'Datos no válidos'
            })

        old_path = data.get('oldPath', '').strip() # Path of the item to rename
        new_name = data.get('newName', '').strip() # New name for the item

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

        # Get the parent directory of the original item's path
        parent_dir_of_old_path = os.path.dirname(old_path)
        # Construct the full path for the new name within the SAME parent directory
        new_path_in_same_dir = os.path.join(parent_dir_of_old_path, new_name)

        # Get the full, validated paths
        full_old_path = get_full_path(old_path)
        full_new_path = get_full_path(new_path_in_same_dir)

        if not full_old_path:
            return jsonify({
                'success': False,
                'message': f'Ruta inválida (antigua): {old_path}'
            })
        
        # Check that the old item exists before attempting to rename
        if not os.path.exists(full_old_path):
            return jsonify({
                'success': False,
                'message': f'El archivo/directorio "{old_path}" no existe'
            })

        # Check if the full path for the new name is valid (within DATA_DIR)
        if not full_new_path:
             return jsonify({
                'success': False,
                'message': f'Ruta inválida (nueva): {new_name}'
            })

        # Check if an item with the new name already exists in the target location
        if os.path.exists(full_new_path):
            return jsonify({
                'success': False,
                'message': f'Ya existe un archivo/directorio con el nombre "{new_name}" en la misma ubicación'
            })

        # --- This check is now redundant because we constructed new_path_in_same_dir ---
        # Keeping the check as a safeguard, though it should always be true now
        if os.path.dirname(full_old_path) != os.path.dirname(full_new_path):
             print(f"SECURITY ALERT: Attempted rename across directories: {full_old_path} to {full_new_path}")
             return jsonify({
                'success': False,
                'message': 'Operación de renombrado inválida (intento de mover)'
            })


        # Perform the rename operation
        os.rename(full_old_path, full_new_path)

        return jsonify({
            'success': True,
            'message': f'Renombrado exitosamente "{os.path.basename(old_path)}" a "{new_name}"'
        })
    except OSError as e:
        print(f"OS Error renaming {full_old_path} to {full_new_path}: {e}")
        return jsonify({
            'success': False,
            'message': f'Error al renombrar: {str(e)}'
        })
    except Exception as e:
        print(f"Unexpected error renaming {full_old_path} to {full_new_path}: {e}")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        })

# --- Keeping the traditional Flask view for rename_item_view if it's still needed elsewhere ---
# @app.route('/rename_item', methods=['GET', 'POST'])
# def rename_item_view():
#     """
#     Handle renaming a file or directory via a traditional Flask view (not API).
#     GET: Display the form with the current item path.
#     POST: Process the rename operation.
#     """
#     original_path = request.args.get('item_path', '').strip()
#     current_context_path = request.args.get('current_context_path', '').strip()

#     if request.method == 'POST':
#         original_path = request.form['original_path'].strip()
#         new_name = request.form['new_name'].strip()
#         current_context_path = request.form.get('current_context_path', '').strip()

#         if not original_path or not new_name:
#             flash("Original path and new name cannot be empty.", "error")
#             return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

#         full_original_path = get_full_path(original_path)

#         if full_original_path is None:
#             flash("Invalid original path provided.", "error")
#             return redirect(url_for('index', current_path=current_context_path))

#         if not os.path.exists(full_original_path):
#             flash(f"Error: Original item '{original_path}' not found.", "error")
#             return redirect(url_for('index', current_path=current_context_path))

#         parent_dir_of_original = os.path.dirname(original_path)
#         new_relative_path = os.path.join(parent_dir_of_original, new_name)
#         full_new_path = get_full_path(new_relative_path)

#         if full_new_path is None:
#              flash("Invalid new name provided.", "error")
#              return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

#         if os.path.exists(full_new_path):
#             flash(f"Error: An item named '{new_relative_path}' already exists.", "error")
#             return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

#         try:
#             os.rename(full_original_path, full_new_path)
#             flash(f"Item '{original_path}' renamed to '{new_relative_path}' successfully.", "success")
#             return redirect(url_for('index', current_path=parent_dir_of_original))
#         except OSError as e:
#             flash(f"Error renaming item '{original_path}': {e}", "error")
#         except Exception as e:
#              flash(f"An unexpected error occurred: {e}", "error")

#         return redirect(url_for('rename_item_view', item_path=original_path, current_context_path=current_context_path))

#     full_original_path_check = get_full_path(original_path)
#     if full_original_path_check is None or not os.path.exists(full_original_path_check):
#          flash("Error: Item to rename not found or invalid path.", "error")
#          return redirect(url_for('index', current_path=current_context_path))

#     current_name = os.path.basename(original_path)

#     return render_template('rename_item.html',
#                            original_path=original_path,
#                            current_name=current_name,
#                            current_context_path=current_context_path)


@app.route('/api/search', methods=['GET'])
def search_files():
    """
    API endpoint to search files and directories.
    """
    search_term = request.args.get('term', '').lower()
    current_path = request.args.get('path', '') # Path to start the search from
    
    if not search_term:
        return jsonify({
            'success': False,
            'message': 'Por favor, ingrese un término de búsqueda'
        })

    full_current_path = get_full_path(current_path)
    
    if not full_current_path:
        return jsonify({
            'success': False,
            'message': 'Ruta de búsqueda no válida. Por favor, verifique la ruta actual'
        })

    if not os.path.exists(full_current_path):
        return jsonify({
            'success': False,
            'message': 'El directorio especificado para la búsqueda no existe'
        })

    try:
        matches = []
        # Recursively search through directories starting from full_current_path
        for root, dirs, files in os.walk(full_current_path):
            # Search in directory names
            for dir_name in dirs:
                if search_term in dir_name.lower():
                    dir_path = os.path.join(root, dir_name)
                    # Get the path relative to DATA_DIR for frontend display
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
                    # Get the path relative to DATA_DIR for frontend display
                    relative_path = os.path.relpath(file_path, DATA_DIR)
                    matches.append({
                        'name': file_name,
                        'path': relative_path,
                        'is_dir': False,
                        'is_file': True
                    })
        
        # Sort results: directories first, then files, both alphabetically
        matches.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        return jsonify({
            'success': True,
            'results': matches,
            'message': f'Se encontraron {len(matches)} resultados para "{search_term}"',
            'search_term': search_term
        })
    except Exception as e:
        print(f"Error during search from {full_current_path} with term '{search_term}': {e}")
        return jsonify({
            'success': False,
            'message': f'Error al realizar la búsqueda: {str(e)}'
        })

if __name__ == '__main__':
    # Run the Flask development server.
    # debug=True enables auto-reloading and detailed error pages.
    # Set to False in a production environment.
    app.run(debug=True)
