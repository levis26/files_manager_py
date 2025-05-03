import os
import shutil
from flask import Flask, render_template, request, redirect, url_for, flash

# --- Anticopy Placeholder ---
# This string serves as a basic, easily identifiable marker.
# A real "anticopy" system is far more complex and would involve unique
# implementation details, code style, and logic flow.
PROJECT_ID = "SimpleFileManager_UniqueMarker_ABC123_20250503"
# ---------------------------

app = Flask(__name__)
# Set a secret key for flashing messages
app.secret_key = b'_5#y2L"F4Q8z\n\xec]/'

# Define the data directory path relative to the application file
DATA_DIR = 'data'

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
    Main page displaying the menu of available actions.
    """
    return render_template('index.html')

@app.route('/view_data/')
@app.route('/view_data/<path:subdir>')
def view_data(subdir=''):
    """
    View contents of the data directory or a specified subdirectory.
    The <path:subdir> allows Flask to capture the rest of the URL as the subdir.
    """
    # Construct the base path to list
    base_path = os.path.join(DATA_DIR, subdir)
    full_base_path = os.path.abspath(base_path) # Use absolute path for listing

    # Validate that the path to list exists and is within DATA_DIR
    abs_data_dir = os.path.abspath(DATA_DIR)
    if not os.path.exists(full_base_path) or not full_base_path.startswith(abs_data_dir):
         flash("Error: Directory not found or outside data path.", "error")
         return redirect(url_for('view_data')) # Redirect to root view if invalid

    items = []
    try:
        # List items in the directory
        with os.scandir(full_base_path) as entries:
            for entry in entries:
                # Determine the path relative to DATA_DIR for display and linking
                # This keeps the URLs clean and relative to the data root
                relative_path = os.path.relpath(entry.path, DATA_DIR)
                items.append({
                    'name': entry.name,
                    'path': relative_path,
                    'is_dir': entry.is_dir(),
                    'is_file': entry.is_file()
                })
        # Sort items: directories first, then files, both alphabetically
        items.sort(key=lambda x: (not x['is_dir'], x['name'].lower()))

    except FileNotFoundError:
        # This case should ideally be caught by the initial validation, but included for safety
        flash(f"Error: Directory '{subdir}' not found.", "error")
        return redirect(url_for('view_data'))
    except Exception as e:
        # Catch any other potential errors during directory listing
        flash(f"Error listing directory: {e}", "error")
        return redirect(url_for('view_data'))

    # Determine the parent directory path for the "Up" link
    parent_dir = ''
    if subdir: # If not at the data root
        # Split the subdirectory path and take all parts except the last one
        parent_dir_parts = subdir.rsplit('/', 1)
        if len(parent_dir_parts) > 1:
            parent_dir = parent_dir_parts[0]
        # If rsplit returns only one part, it means the current subdir is a top-level item,
        # so the parent is the data root ('')

    return render_template('view_data.html', current_dir=subdir, items=items, parent_dir=parent_dir)


@app.route('/create_directory', methods=['GET', 'POST'])
def create_directory():
    """
    Handle the creation of a new directory.
    GET: Display the form.
    POST: Process the form submission.
    """
    if request.method == 'POST':
        dir_path = request.form['dir_path'].strip() # Get path from form and remove leading/trailing whitespace
        if not dir_path:
            flash("Directory path cannot be empty.", "error")
            return redirect(url_for('create_directory'))

        full_path = get_full_path(dir_path)

        if full_path is None:
            flash("Invalid path provided. Please ensure it's relative to 'data/' and doesn't use '..' or absolute paths.", "error")
            return redirect(url_for('create_directory'))

        try:
            # os.makedirs creates intermediate directories if they don't exist
            os.makedirs(full_path)
            flash(f"Directory '{dir_path}' created successfully.", "success")
            # Redirect to view the parent directory or the root if it's a top-level dir
            parent_dir_for_redirect = os.path.dirname(dir_path)
            return redirect(url_for('view_data', subdir=parent_dir_for_redirect))
        except FileExistsError:
            flash(f"Error: Directory '{dir_path}' already exists.", "error")
        except OSError as e:
            flash(f"Error creating directory '{dir_path}': {e}", "error")
        except Exception as e:
             flash(f"An unexpected error occurred: {e}", "error")

    # For GET request or after a POST failure
    return render_template('create_dir.html')

@app.route('/create_file', methods=['GET', 'POST'])
def create_file():
    """
    Handle the creation of a new file with initial content.
    GET: Display the form.
    POST: Process the form submission.
    """
    if request.method == 'POST':
        file_path = request.form['file_path'].strip() # Get path from form and remove leading/trailing whitespace
        content = request.form['content'] # Get content from form
        if not file_path:
            flash("File path cannot be empty.", "error")
            return redirect(url_for('create_file'))

        full_path = get_full_path(file_path)

        if full_path is None:
            flash("Invalid path provided. Please ensure it's relative to 'data/' and doesn't use '..' or absolute paths.", "error")
            return redirect(url_for('create_file'))

        # Ensure parent directory exists before creating the file
        parent_dir = os.path.dirname(full_path)
        if not os.path.exists(parent_dir):
            try:
                # Create parent directories if they don't exist, exist_ok=True prevents error if dir exists
                os.makedirs(parent_dir, exist_ok=True)
            except OSError as e:
                flash(f"Error creating parent directory for '{file_path}': {e}", "error")
                return redirect(url_for('create_file'))

        try:
            # 'x' mode creates exclusively, fails if file exists.
            # This prevents accidentally overwriting existing files.
            with open(full_path, 'x') as f:
                f.write(content)
            flash(f"File '{file_path}' created successfully.", "success")
            # Redirect to view the parent directory or the root
            parent_dir_for_redirect = os.path.dirname(file_path)
            return redirect(url_for('view_data', subdir=parent_dir_for_redirect))
        except FileExistsError:
            flash(f"Error: File '{file_path}' already exists.", "error")
        except OSError as e:
            flash(f"Error creating file '{file_path}': {e}", "error")
        except Exception as e:
             flash(f"An unexpected error occurred: {e}", "error")

    # For GET request or after a POST failure
    return render_template('create_file.html')

@app.route('/append_file', methods=['GET', 'POST'])
def append_file():
    """
    Handle appending content to an existing file.
    GET: Display the form.
    POST: Process the form submission.
    """
    if request.method == 'POST':
        file_path = request.form['file_path'].strip() # Get path from form and remove leading/trailing whitespace
        content = request.form['content'] # Get content from form
        if not file_path:
            flash("File path cannot be empty.", "error")
            return redirect(url_for('append_file'))

        full_path = get_full_path(file_path)

        if full_path is None:
            flash("Invalid path provided. Please ensure it's relative to 'data/' and doesn't use '..' or absolute paths.", "error")
            return redirect(url_for('append_file'))

        # Check if the path points to an existing file
        if not os.path.isfile(full_path):
             flash(f"Error: '{file_path}' is not a file or does not exist.", "error")
             return redirect(url_for('append_file'))

        try:
            # 'a' mode appends to the end of the file. Creates the file if it doesn't exist,
            # but we already checked with os.path.isfile().
            with open(full_path, 'a') as f:
                f.write(content + '\n') # Add a newline for clarity with appended content
            flash(f"Content appended to file '{file_path}' successfully.", "success")
            # Redirect to view the parent directory or the root
            parent_dir_for_redirect = os.path.dirname(file_path)
            return redirect(url_for('view_data', subdir=parent_dir_for_redirect))
        except FileNotFoundError:
             # This should be caught by isfile() check, but included for robustness
             flash(f"Error: File '{file_path}' not found.", "error")
        except OSError as e:
            flash(f"Error appending to file '{file_path}': {e}", "error")
        except Exception as e:
             flash(f"An unexpected error occurred: {e}", "error")

    # For GET request or after a POST failure
    return render_template('append_file.html')

@app.route('/delete_item', methods=['GET', 'POST'])
def delete_item():
    """
    Handle deleting a file or directory. Directories are deleted recursively.
    GET: Display the form.
    POST: Process the form submission.
    """
    if request.method == 'POST':
        item_path = request.form['item_path'].strip() # Get path from form and remove leading/trailing whitespace
        if not item_path:
            flash("Item path cannot be empty.", "error")
            return redirect(url_for('delete_item'))

        full_path = get_full_path(item_path)

        if full_path is None:
            flash("Invalid path provided. Please ensure it's relative to 'data/' and doesn't use '..' or absolute paths.", "error")
            return redirect(url_for('delete_item'))

        # Determine if the path points to a file or directory
        if os.path.isfile(full_path):
            try:
                os.remove(full_path) # Delete the file
                flash(f"File '{item_path}' deleted successfully.", "success")
                # Redirect to view the parent directory or the root
                parent_dir_for_redirect = os.path.dirname(item_path)
                return redirect(url_for('view_data', subdir=parent_dir_for_redirect))
            except OSError as e:
                flash(f"Error deleting file '{item_path}': {e}", "error")
            except Exception as e:
                 flash(f"An unexpected error occurred: {e}", "error")

        elif os.path.isdir(full_path):
            try:
                # Use shutil.rmtree for recursive deletion of directories
                shutil.rmtree(full_path)
                flash(f"Directory '{item_path}' and its contents deleted successfully.", "success")
                # Redirect to the parent directory of the deleted item
                parent_dir_for_redirect = os.path.dirname(item_path)
                return redirect(url_for('view_data', subdir=parent_dir_for_redirect))
            except OSError as e:
                flash(f"Error deleting directory '{item_path}': {e}", "error")
            except Exception as e:
                 flash(f"An unexpected error occurred: {e}", "error")
        else:
            # If the path doesn't exist or isn't a file/directory (e.g., a broken symlink)
            flash(f"Error: '{item_path}' not found or is not a file/directory.", "error")

    # For GET request or after a POST failure
    return render_template('delete_item.html')

if __name__ == '__main__':
    # Run the Flask development server.
    # debug=True enables auto-reloading and detailed error pages.
    # Set to False in a production environment.
    app.run(debug=True)
