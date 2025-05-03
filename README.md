# files_manager_py
File and Directory Management ApplicationThis is a simple web application built with Python and Flask to manage files and directories within a designated data folder. It provides a basic graphical interface accessible via a web browser to perform common file system operations.FeaturesThe application supports the following operations within the data directory:View Contents: Browse the contents of the data directory and its subdirectories.Create Directory: Create new directories at a specified path within data.Create File: Create new files at a specified path within data with initial content.Append to File: Add new content to the end of an existing file within data.Delete File: Delete a specific file within data.Delete Directory: Recursively delete a directory and all its contents within data.Project StructureThe project follows a simple structure:/project_root
├── app.py              # The main Flask application file
├── data/               # Directory for file and directory storage
└── templates/          # Directory for HTML templates
    ├── index.html      # Main menu page
    ├── create_dir.html # Form for creating directories
    ├── create_file.html # Form for creating files
    ├── append_file.html # Form for appending to files
    ├── delete_item.html # Form for deleting files/directories
    └── view_data.html  # Page to view data directory contents
The data/ directory is automatically created when the application runs if it doesn't exist.SetupTo run this project, you need Python installed on your system. It is highly recommended to use a virtual environment to manage dependencies.Clone or download the project files:Save the app.py file and create the templates directory with the HTML files inside it. Ensure the data directory is created at the same level as app.py.Navigate to the project directory:Open your terminal or command prompt and change your current directory to the project_root.cd /path/to/your/project_root
Create a virtual environment:python3 -m venv .venv
This creates a virtual environment named .venv in your project directory.Activate the virtual environment:On Linux/macOS:source .venv/bin/activate
On Windows:.venv\Scripts\activate
You should see (.venv) at the beginning of your terminal prompt, indicating the virtual environment is active.Install dependencies:With the virtual environment active, install Flask:pip install Flask
How to RunActivate your virtual environment (if not already active):source .venv/bin/activate # Linux/macOS
# OR
.venv\Scripts\activate # Windows
Run the Flask application:python app.py
Access the application:Open your web browser and go to http://127.0.0.1:5000/.The terminal running app.py will show server logs. Press CTRL+C in the terminal to stop the server.UsageOnce the application is running and you access http://127.0.0.1:5000/ in your browser, you will see the main menu.Click on the links to navigate to the different forms for creating, appending, or deleting items.Use the "View Data Directory Contents" link to browse the data folder and see the results of your operations.When prompted for a path, provide the path relative to the data/ directory (e.g., my_folder/my_file.txt or new_directory). Do not use leading slashes (/) or .. at the beginning of paths.Anticopy NoteAs requested, a symbolic identifier (PROJECT_ID) is included in the app.py file. Please note that this is a basic marker and does not provide robust protection against code sharing or detection of AI-generated content. The true value of your project lies in your understanding, unique implementation choices, and the learning process.