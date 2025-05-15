import os
import shutil
import traceback # Importar módulo traceback
from flask import Blueprint, request, jsonify
# Import get_full_path and the new get_data_dir_abs function
# Remove the direct import of DATA_DIR
from utils import get_full_path, get_data_dir_abs

modification_bp = Blueprint('modification_bp', __name__)

@modification_bp.route('/api/append_file', methods=['POST'])
def append_file():
    """
    API endpoint to append content to a file.
    """
    data = request.get_json()
    path = data.get('path', '') # This is the file path
    content = data.get('content', '').strip()

    # --- Logging para diagnóstico ---
    print(f"\n--- /api/append_file ---")
    print(f"Received path from frontend: '{path}'")
    print(f"Received content: '{content[:50]}...'") # Log first 50 chars of content


    if not path:
        print(f"/api/append_file: Path is empty. Sending error.")
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': 'Path is required'
        })

    if not content:
        print(f"/api/append_file: Content is empty after strip. Sending error.")
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': 'Content cannot be empty'
        })

    full_path = get_full_path(path)
    print(f"/api/append_file: get_full_path returned: '{full_path}'")

    # Check if path is valid AND points to an existing file
    # --- Añadido logging de existencia y tipo ---
    print(f"/api/append_file: Checking existence of '{full_path}'...")
    if not full_path or not os.path.exists(full_path):
        print(f"/api/append_file: Invalid full_path ('{full_path}') or path does NOT exist for frontend path '{path}'. Sending error.")
        print(f"--- Fin /api/append_file ---\n")
        # Note: Message kept for frontend consistency, even if full_path is None.
        return jsonify({
            'success': False,
            'message': 'Invalid file path or item is not a file'
        })
    print(f"/api/append_file: Path '{full_path}' exists.")

    print(f"/api/append_file: Checking if '{full_path}' is a file...")
    if not os.path.isfile(full_path):
        print(f"/api/append_file: Full path '{full_path}' is NOT a file. Sending error.")
        print(f"--- Fin /api/append_file ---\n")
         # Note: Message kept for frontend consistency, even if full_path is not a file.
        return jsonify({
            'success': False,
            'message': 'Invalid file path or item is not a file'
        })
    print(f"/api/append_file: Path '{full_path}' is a file.")


    try:
        # Append content with UTF-8 encoding
        with open(full_path, 'a', encoding='utf-8') as f:
            # Add a newline only if the file is not empty to avoid leading newlines
            if os.path.getsize(full_path) > 0:
                 f.write('\n')
            f.write(content)

        print(f"/api/append_file: Successfully appended content to '{full_path}'.")
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': True,
            'message': f"Content appended to '{os.path.basename(path)}' successfully"
        })
    except OSError as e:
        # --- Modificación aquí: Manejar el caso de full_path=None en el log ---
        # full_path should not be None here due to checks above, but keep robust logging
        error_path_display = full_path if full_path is not None else 'None'
        print(f"/api/append_file: OS Error appending to file {error_path_display}: {e}. Sending error.")
        # Imprimir traceback para OSError también, por si acaso
        traceback.print_exc()
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        # --- Modificación aquí: Manejar el caso de full_path=None en el log e imprimir traceback ---
         # full_path should not be None here, but keep robust logging
        error_path_display = full_path if full_path is not None else 'None'
        print(f"/api/append_file: Unexpected error appending to file {error_path_display}: {e}. Sending error.")
        traceback.print_exc() # Imprimir el traceback completo
        print(f"--- Fin /api/append_file ---\n")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        })


@modification_bp.route('/api/delete', methods=['POST'])
def delete_item():
    """
    API endpoint to delete a file or directory.
    """
    data = request.get_json()
    path = data.get('path', '') # This is the path of the item to delete

    # --- Logging para diagnóstico ---
    print(f"\n--- /api/delete ---")
    print(f"Received path from frontend: '{path}'")

    if not path:
        print(f"/api/delete: Path is empty. Sending error.")
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': 'Path is required'
        })

    full_path = get_full_path(path)
    print(f"/api/delete: get_full_path returned: '{full_path}'")

    if not full_path:
        print(f"/api/delete: Invalid path after get_full_path for '{path}'. Sending error.")
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    # --- Crucial check: Ensure the item to be deleted actually exists ---
    print(f"/api/delete: Checking existence of '{full_path}'...")
    if not os.path.exists(full_path):
        print(f"/api/delete: Full path '{full_path}' does NOT exist. Sending error.")
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': 'Item not found'
        })
    print(f"/api/delete: Path '{full_path}' exists.")


    try:
        if os.path.isfile(full_path):
            print(f"/api/delete: Attempting to delete file: '{full_path}'")
            os.remove(full_path)
            print(f"/api/delete: Successfully deleted file '{full_path}'.")
            print(f"--- Fin /api/delete ---\n")
            return jsonify({
                'success': True,
                'message': f"File '{os.path.basename(path)}' deleted successfully"
            })
        elif os.path.isdir(full_path):
            print(f"/api/delete: Attempting to delete directory: '{full_path}'")
            # Prevent accidental deletion of the root DATA_DIR
            # --- CORRECCIÓN AQUÍ: Usar get_data_dir_abs() para obtener la ruta absoluta de DATA_DIR ---
            try:
                data_dir_abs = get_data_dir_abs()
            except RuntimeError as e:
                 print(f"/api/delete: Error obtaining DATA_DIR absolute path: {e}. Sending error.")
                 print(f"--- Fin /api/delete ---\n")
                 return jsonify({
                    'success': False,
                    'message': 'Internal server error: DATA_DIR not initialized'
                 })

            if full_path == data_dir_abs: # Compare against the reliably obtained absolute DATA_DIR
                print(f"/api/delete: Attempted to delete root DATA_DIR '{full_path}'. Sending error.")
                print(f"--- Fin /api/delete ---\n")
                return jsonify({
                    'success': False,
                    'message': 'Cannot delete the root directory'
                })
            shutil.rmtree(full_path) # Recursive deletion
            print(f"/api/delete: Successfully deleted directory '{full_path}'.")
            print(f"--- Fin /api/delete ---\n")
            return jsonify({
                'success': True,
                'message': f"Directory '{os.path.basename(path)}' and its contents deleted successfully"
            })
        else:
            # Should not be reached if get_full_path and os.path.exists work as expected,
            # but good for robustness.
            print(f"/api/delete: Item at '{full_path}' is neither file nor directory. Sending error.")
            print(f"--- Fin /api/delete ---\n")
            return jsonify({
                'success': False,
                'message': 'Item is neither a file nor a directory'
            })
    except OSError as e:
        # --- Modificación aquí: Manejar el caso de full_path=None en el log e imprimir traceback ---
        # full_path should not be None here due to checks above, but keep robust logging
        error_path_display = full_path if full_path is not None else 'None'
        print(f"/api/delete: OS Error deleting {error_path_display}: {e}. Sending error.")
        traceback.print_exc() # Imprimir traceback para OSError
        print(f"--- Fin /api/delete ---\n")
        return jsonify({
            'success': False,
            'message': str(e)
        })
    except Exception as e:
        # --- Modificación aquí: Manejar el caso de full_path=None en el log e imprimir traceback ---
         # full_path should not be None here, but keep robust logging
        error_path_display = full_path if full_path is not None else 'None'
        print(f"/api/delete: Unexpected error deleting {error_path_display}: {e}. Sending error.")
        traceback.print_exc() # Imprimir el traceback completo
        print(f"--- Fin /api/delete ---\n")
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
            print(f"\n--- /api/rename_item ---")
            print(f"Received empty data. Sending error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': 'Datos no válidos'
            })

        old_path = data.get('oldPath', '').strip() # Path of the item to rename
        new_name = data.get('newName', '').strip() # New name for the item

        # --- Logging para diagnóstico ---
        print(f"\n--- /api/rename_item ---")
        print(f"Received oldPath from frontend: '{old_path}'")
        print(f"Received newName from frontend: '{new_name}'")


        if not old_path or not new_name:
            print(f"/api/rename_item: oldPath or newName is empty. Sending error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': 'Por favor, ingrese una ruta y un nuevo nombre'
            })

        if not new_name: # Check if new name is empty after strip()
            print(f"/api/rename_item: newName is empty after strip. Sending error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': 'El nuevo nombre no puede estar vacío'
            })

        # Get the parent directory of the original item's path
        parent_dir_of_old_path = os.path.dirname(old_path)
        print(f"/api/rename_item: Parent directory of oldPath: '{parent_dir_of_old_path}'")

        # Construct the full path for the new name within the SAME parent directory
        # Use os.path.join for cross-platform compatibility
        new_path_in_same_dir = os.path.join(parent_dir_of_old_path, new_name)
        print(f"/api/rename_item: Candidate new path in same dir: '{new_path_in_same_dir}'")


        # Get the full, validated paths
        full_old_path = get_full_path(old_path)
        full_new_path = get_full_path(new_path_in_same_dir) # Ensure new path is also within DATA_DIR
        print(f"/api/rename_item: get_full_path(old_path) returned: '{full_old_path}'")
        print(f"/api/rename_item: get_full_path(new_path_in_same_dir) returned: '{full_new_path}'")


        if not full_old_path:
            print(f"/api/rename_item: Invalid full_old_path after get_full_path for '{old_path}'. Sending error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'Ruta inválida (antigua): {old_path}'
            })

        # Check that the old item exists before attempting to rename
        print(f"/api/rename_item: Checking existence of old path '{full_old_path}'...")
        if not os.path.exists(full_old_path):
            print(f"/api/rename_item: Full old path '{full_old_path}' does NOT exist. Sending error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'El archivo/directorio "{old_path}" no existe'
            })
        print(f"/api/rename_item: Old path '{full_old_path}' exists.")


        # Check if the full path for the new name is valid (within DATA_DIR).
        # get_full_path already handles this, so checking if full_new_path is None is sufficient.
        if not full_new_path:
            print(f"/api/rename_item: Invalid full_new_path after get_full_path for '{new_path_in_same_dir}'. Sending error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'Ruta inválida (nueva): {new_name}'
            })

        # Check if an item with the new name already exists at the target location
        print(f"/api/rename_item: Checking existence of new path '{full_new_path}'...")
        if os.path.exists(full_new_path):
            print(f"/api/rename_item: Full new path '{full_new_path}' already exists. Sending error.")
            print(f"--- Fin /api/rename_item ---\n")
            return jsonify({
                'success': False,
                'message': f'Ya existe un archivo/directorio con el nombre "{new_name}" en la misma ubicación'
            })
        print(f"/api/rename_item: New path '{full_new_path}' does not exist (good).")


        # Perform the rename operation
        print(f"/api/rename_item: Attempting to rename '{full_old_path}' to '{full_new_path}'")
        os.rename(full_old_path, full_new_path)
        print(f"/api/rename_item: Successfully renamed '{full_old_path}' to '{full_new_path}'.")
        print(f"--- Fin /api/rename_item ---\n")

        return jsonify({
            'success': True,
            'message': f'Renombrado exitosamente "{os.path.basename(old_path)}" a "{new_name}"'
        })
    except OSError as e:
        # --- Modificación aquí: Manejar el caso de full_old_path=None en el log e imprimir traceback ---
        # full_old_path and full_new_path should not be None here, but keep robust logging
        error_old_path_display = full_old_path if full_old_path is not None else 'None'
        error_new_path_display = full_new_path if full_new_path is not None else 'None'
        print(f"/api/rename_item: OS Error renaming {error_old_path_display} to {error_new_path_display}: {e}. Sending error.")
        traceback.print_exc() # Imprimir traceback para OSError
        print(f"--- Fin /api/rename_item ---\n")
        return jsonify({
            'success': False,
            'message': f'Error al renombrar: {str(e)}'
        })
    except Exception as e:
        # --- Modificación aquí: Manejar el caso de full_old_path=None en el log e imprimir traceback ---
         # full_old_path and full_new_path should not be None here, but keep robust logging
        error_old_path_display = full_old_path if full_old_path is not None else 'None'
        error_new_path_display = full_new_path if full_new_path is not None else 'None'
        print(f"/api/rename_item: Unexpected error renaming {error_old_path_display} to {error_new_path_display}: {e}. Sending error.")
        traceback.print_exc() # Imprimir el traceback completo
        print(f"--- Fin /api/rename_item ---\n")
        return jsonify({
            'success': False,
            'message': f'Error inesperado: {str(e)}'
        })