import os
from flask import Blueprint, request, jsonify
from utils import get_full_path, get_current_path_display, DATA_DIR # Import from utils

browse_bp = Blueprint('browse_bp', __name__)

@browse_bp.route('/api/browse')
def browse_directory():
    """
    API endpoint to browse directory contents.
    """
    current_path = request.args.get('path', '')
    # --- Logging para diagnóstico ---
    print(f"\n--- /api/browse ---")
    print(f"Received current_path from frontend: '{current_path}'")

    full_current_path = get_full_path(current_path)
    print(f"/api/browse: get_full_path returned: '{full_current_path}'")

    if not full_current_path:
        print(f"/api/browse: Invalid path after get_full_path for '{current_path}'. Sending error.")
        print(f"--- Fin /api/browse ---\n")
        return jsonify({
            'success': False,
            'message': 'Invalid path'
        })

    if not os.path.exists(full_current_path):
        print(f"/api/browse: Full path '{full_current_path}' does NOT exist. Sending error.")
        print(f"--- Fin /api/browse ---\n")
        return jsonify({
            'success': False,
            'message': 'Path does not exist'
        })

    if not os.path.isdir(full_current_path):
        print(f"/api/browse: Full path '{full_current_path}' is NOT a directory. Sending error.")
        print(f"--- Fin /api/browse ---\n")
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
                    'path': relative_path.replace(os.sep, '/'), # Use forward slashes for frontend
                    'is_dir': entry.is_dir(),
                    'is_file': entry.is_file()
                })
        # Sort directories first, then files, both alphabetically
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))
        print(f"/api/browse: Successfully listed {len(items)} items in '{full_current_path}'.")

    except Exception as e:
        # Log the error on the server side
        print(f"/api/browse: Error browsing directory {full_current_path}: {e}")
        print(f"--- Fin /api/browse ---\n")
        return jsonify({
            'success': False,
            'message': str(e)
        })

    print(f"/api/browse: Sending success response for '{current_path}'.")
    print(f"--- Fin /api/browse ---\n")
    return jsonify({
        'success': True,
        'items': items,
        'current_path_display': get_current_path_display(full_current_path)
    })
