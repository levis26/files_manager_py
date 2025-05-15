import os
from flask import Blueprint, request, jsonify
from utils import get_full_path # Import from utils

creation_bp = Blueprint('creation_bp', __name__)

@creation_bp.route('/api/create_dir', methods=['POST'])
def create_directory():
    """
    API endpoint to create a new directory.
    """
    data = request.get_json()
    path = data.get('path', '') # This is the parent directory path (can be "")
    name = data.get('name', '') # This is the new directory name

    if not name: # Only require name to be non-empty
        return jsonify({
            'success': False,
            'message': 'Name is required'
        })

    # Construct the full path for the new directory
    # Use os.path.join for cross-platform compatibility
    new_dir_relative_path = os.path.join(path, name)
    full_path = get_full_path(new_dir_relative_path)
    
    # Check if the parent directory is valid and exists
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

@creation_bp.route('/api/create_file', methods=['POST'])
def create_file():
    """
    API endpoint to create a new file.
    """
    data = request.get_json()
    path = data.get('path', '') # This is the parent directory path (can be "")
    name = data.get('name', '') # This is the new file name
    content = data.get('content', '')

    if not name: # Only require name to be non-empty
        return jsonify({
            'success': False,
            'message': 'Name is required'
        })

    # Construct the full path for the new file
    # Use os.path.join for cross-platform compatibility
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
