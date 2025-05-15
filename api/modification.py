import os
import shutil
from flask import Blueprint, request, jsonify
from utils import get_full_path, DATA_DIR # Import from utils

modification_bp = Blueprint('modification_bp', __name__)

@modification_bp.route('/api/append_file', methods=['POST'])
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

@modification_bp.route('/api/delete', methods=['POST'])
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
            'message': f'Error inesperado: {str(e)}'
        })

@modification_bp.route('/api/rename_item', methods=['POST'])
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
        # Use os.path.join for cross-platform compatibility
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

        # Check if an item with the new name already exists at the target location
        if os.path.exists(full_new_path):
            return jsonify({
                'success': False,
                'message': f'Ya existe un archivo/directorio con el nombre "{new_name}" en la misma ubicación'
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

