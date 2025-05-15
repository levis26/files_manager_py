import os
from flask import Blueprint, request, jsonify
from utils import get_full_path # Import from utils

search_bp = Blueprint('search_bp', __name__)

@search_bp.route('/api/search', methods=['GET'])
def search_files():
    """
    API endpoint to search files and directories.
    """
    search_term = request.args.get('term', '').lower()
    current_path = request.args.get('path', '') # Path to start the search from

    # --- Logging para diagnóstico ---
    print(f"\n--- /api/search ---")
    print(f"Received search_term: '{search_term}'")
    print(f"Received current_path from frontend: '{current_path}'")

    if not search_term:
        print(f"/api/search: Search term is empty. Sending error.")
        print(f"--- Fin /api/search ---\n")
        return jsonify({
            'success': False,
            'message': 'Por favor, ingrese un término de búsqueda'
        })

    full_current_path = get_full_path(current_path)
    print(f"/api/search: get_full_path returned: '{full_current_path}'")

    if not full_current_path:
        print(f"/api/search: Invalid path after get_full_path for '{current_path}'. Sending error.")
        print(f"--- Fin /api/search ---\n")
        return jsonify({
            'success': False,
            'message': 'Ruta de búsqueda no válida. Por favor, verifique la ruta actual'
        })

    # --- Añadido logging de existencia ---
    print(f"/api/search: Checking existence of search path '{full_current_path}'...")
    if not os.path.exists(full_current_path):
        print(f"/api/search: Search path '{full_current_path}' does NOT exist. Sending error.")
        print(f"--- Fin /api/search ---\n")
        return jsonify({
            'success': False,
            'message': 'El directorio especificado para la búsqueda no existe'
        })
    print(f"/api/search: Search path '{full_current_path}' exists.")


    try:
        matches = []
        # Recursively search through directories starting from full_current_path
        print(f"/api/search: Starting recursive search from '{full_current_path}'...")
        for root, dirs, files in os.walk(full_current_path):
            # Search in directory names
            for dir_name in dirs:
                if search_term in dir_name.lower():
                    dir_path = os.path.join(root, dir_name)
                    # Get the path relative to DATA_DIR for frontend display
                    # Use os.path.relpath and replace os.sep for cross-platform compatibility
                    # Need to import DATA_DIR here or pass it from app.py if not global in utils
                    # Assuming DATA_DIR is globally accessible from utils after initialize_paths
                    relative_path = os.path.relpath(dir_path, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))) # Re-calculating DATA_DIR here is risky
                    matches.append({
                        'name': dir_name,
                        'path': relative_path.replace(os.sep, '/'), # Use forward slashes for frontend
                        'is_dir': True,
                        'is_file': False
                    })
            
            for file_name in files:
                if search_term in file_name.lower():
                    file_path = os.path.join(root, file_name)
                    # Get the path relative to DATA_DIR for frontend display
                    # Use os.path.relpath and replace os.sep for cross-platform compatibility
                     # Need to import DATA_DIR here or pass it from app.py if not global in utils
                    # Assuming DATA_DIR is globally accessible from utils after initialize_paths
                    relative_path = os.path.relpath(file_path, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))) # Re-calculating DATA_DIR here is risky
                    matches.append({
                        'name': file_name,
                        'path': relative_path.replace(os.sep, '/'), # Use forward slashes for frontend
                        'is_dir': False,
                        'is_file': True
                    })
        
        # Sort results: directories first, then files, both alphabetically
        matches.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        
        print(f"/api/search: Search completed. Found {len(matches)} results for '{search_term}'.")
        print(f"--- Fin /api/search ---\n")

        return jsonify({
            'success': True,
            'results': matches,
            'message': f'Se encontraron {len(matches)} resultados para "{search_term}"',
            'search_term': search_term
        })
    except Exception as e:
        print(f"/api/search: Error during search from {full_current_path} with term '{search_term}': {e}. Sending error.")
        print(f"--- Fin /api/search ---\n")
        return jsonify({
            'success': False,
            'message': f'Error al realizar la búsqueda: {str(e)}'
        })
