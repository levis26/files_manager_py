import os
from flask import Blueprint, request, jsonify
from utils import get_full_path # Import from utils

file_content_bp = Blueprint('file_content_bp', __name__)

@file_content_bp.route('/api/get-file-content')
def get_file_content():
    """
    API endpoint to get file content.
    """
    path = request.args.get('path', '')
    # --- Logging para diagnóstico ---
    print(f"\n--- /api/get-file-content ---")
    print(f"Received path from frontend: '{path}'")

    full_path = get_full_path(path)
    print(f"/api/get-file-content: get_full_path returned: '{full_path}'")
    
    # Validate path and ensure it's an existing file
    # --- Añadido logging de existencia y tipo ---
    print(f"/api/get-file-content: Checking existence of '{full_path}'...")
    if not full_path or not os.path.exists(full_path):
         print(f"/api/get-file-content: Invalid full_path ('{full_path}') or path does NOT exist for frontend path '{path}'. Sending error.")
         print(f"--- Fin /api/get-file-content ---\n")
         return jsonify({
            'success': False,
            'message': 'Invalid file path or not a file' # Message kept for frontend consistency
        })
    print(f"/api/get-file-content: Path '{full_path}' exists.")

    print(f"/api/get-file-content: Checking if '{full_path}' is a file...")
    if not os.path.isfile(full_path):
         print(f"/api/get-file-content: Full path '{full_path}' is NOT a file. Sending error.")
         print(f"--- Fin /api/get-file-content ---\n")
         return jsonify({
            'success': False,
            'message': 'Invalid file path or not a file' # Message kept for frontend consistency
        })
    print(f"/api/get-file-content: Path '{full_path}' is a file.")


    try:
        # Read file content with UTF-8 encoding
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"/api/get-file-content: Successfully read content from '{full_path}'.")
        print(f"--- Fin /api/get-file-content ---\n")
        return jsonify({
            'success': True,
            'content': content
        })
    except Exception as e:
        print(f"/api/get-file-content: Error reading file {full_path}: {e}. Sending error.")
        print(f"--- Fin /api/get-file-content ---\n")
        return jsonify({
            'success': False,
            'message': str(e)
        })
