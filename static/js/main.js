// Global variables to track the selected item
let selectedItemPath = null;
let selectedItemIsFile = false;
let selectedItemElement = null; // Reference to the currently selected DOM element

// Function to show alerts with more details
function showAlert(type, message, extraInfo = '') {
    // console.log(`showAlert llamada: Tipo=${type}, Mensaje="${message}", InfoExtra="${extraInfo}"`); // Para verificar
    const alertDiv = document.createElement('div');
    // Use Bootstrap alert classes for styling
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    
    // Add icon based on alert type using Bootstrap Icons
    const iconClass = type === 'danger' ? 'bi-exclamation-triangle-fill' :
                    type === 'success' ? 'bi-check-circle-fill' :
                    type === 'warning' ? 'bi-exclamation-triangle-fill' :
                    'bi-info-circle-fill';
    
    alertDiv.innerHTML = `
        <div class="d-flex align-items-center">
            <i class="bi ${iconClass} me-2"></i>
            <div>
                ${message}
                ${extraInfo ? `<small class="text-muted d-block">${extraInfo}</small>` : ''}
            </div>
        </div>
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insert at the beginning of the main container where alerts should appear
    const container = document.querySelector('.container'); // Target the main Bootstrap container
    // console.log('Elemento "container" para la alerta:', container); //Para verificar
    if (!container) { 
        console.error("No se encontró el elemento '.container' para mostrar la alerta.");
        // Fallback: Log to console if container not found
        console.log(`ALERTA (${type}): ${message} - ${extraInfo}`);
        return;
    }
    
    // Find the first child that is NOT another alert to insert before it
    let firstNonAlertChild = null;
    for (let i = 0; i < container.children.length; i++) {
        if (!container.children[i].classList.contains('alert')) {
            firstNonAlertChild = container.children[i];
            break;
        }
    }

    if (firstNonAlertChild) {
        container.insertBefore(alertDiv, firstNonAlertChild);
    } else {
         // If all children are alerts or container is empty, just append
        container.appendChild(alertDiv);
    }
    
    // Auto-hide after 5 seconds
    setTimeout(() => {
        // Ensure the element still exists before trying to close
        if (alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

// Function to update the state of sidebar action buttons based on selection
function updateSidebarButtonStates() {
    const appendBtn = document.getElementById('sidebarAppendBtn');
    const deleteBtn = document.getElementById('sidebarDeleteBtn');
    const renameBtn = document.getElementById('sidebarRenameBtn');

    if (selectedItemPath === null) {
        // No item selected - disable append, delete, rename
        if (appendBtn) appendBtn.disabled = true;
        if (deleteBtn) deleteBtn.disabled = true;
        if (renameBtn) renameBtn.disabled = true;
    } else {
        // Item is selected - enable delete and rename
        if (deleteBtn) deleteBtn.disabled = false;
        if (renameBtn) renameBtn.disabled = false;

        // Enable append only if the selected item is a file
        if (appendBtn) appendBtn.disabled = !selectedItemIsFile;
    }
}

// Function to handle item selection in the browser list
function selectItem(path, isFile, element) {
    // Clear previous selection highlight
    if (selectedItemElement) {
        selectedItemElement.classList.remove('list-group-item-primary'); // Use Bootstrap primary color for highlight
    }

    // Set new selection
    selectedItemPath = path;
    selectedItemIsFile = isFile;
    selectedItemElement = element;

    // Add highlight to the selected element
    if (selectedItemElement) {
        selectedItemElement.classList.add('list-group-item-primary');
    }

    // Update sidebar button states based on the new selection
    updateSidebarButtonStates();

    // If a file is selected, preview it automatically
    if (isFile) {
        previewFile(path);
    } else {
        // Clear preview if a directory is selected or selection is cleared
        const previewDiv = document.getElementById('file-preview');
        if (previewDiv) {
             previewDiv.innerHTML = `
                <div class="text-muted text-center py-5 d-flex align-items-center justify-content-center flex-grow-1">
                    Selecciona un archivo para ver su contenido
                </div>
            `;
        }
    }
}

// Function to clear the current selection
function clearSelection(event) {
    // Check if the click target is within an item element or a button within an item
    // If not, clear the selection
    const target = event.target;
    const isItemElement = target.classList.contains('list-group-item');
    const isButtonInItem = target.closest('.btn-group');

    if (!isItemElement && !isButtonInItem) {
        if (selectedItemElement) {
            selectedItemElement.classList.remove('list-group-item-primary');
        }
        selectedItemPath = null;
        selectedItemIsFile = false;
        selectedItemElement = null;
        updateSidebarButtonStates(); // Disable action buttons
         // Clear preview when selection is cleared
        const previewDiv = document.getElementById('file-preview');
        if (previewDiv) {
             previewDiv.innerHTML = `
                <div class="text-muted text-center py-5 d-flex align-items-center justify-content-center flex-grow-1">
                    Selecciona un archivo para ver su contenido
                </div>
            `;
        }
    }
}


// Function to load directory content from the backend API
async function loadDirectoryContent(path = '') {
    try {
        // Clear any previous selection before loading new content
        if (selectedItemElement) {
            selectedItemElement.classList.remove('list-group-item-primary');
        }
        selectedItemPath = null;
        selectedItemIsFile = false;
        selectedItemElement = null;
        updateSidebarButtonStates(); // Disable action buttons

        // Construct the API URL with the encoded path
        const response = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
        // Parse the JSON response
        const data = await response.json();
        
        if (data.success) {
            // Update the displayed current path
            document.getElementById('currentPath').textContent = data.current_path_display || 'data/'; // Ensure trailing slash for root display
            
            const browserContent = document.getElementById('browser-content');
            browserContent.innerHTML = ''; // Clear previous content
            
            // Show "Up Level" button if not in the root directory
            if (path) {
                // Calculate the parent path
                const parentPath = path.split('/').slice(0, -1).join('/');
                const upButton = document.createElement('button'); // Use button for better click handling
                upButton.className = 'list-group-item list-group-item-action d-flex align-items-center';
                 // Use an anonymous function to correctly pass the parentPath
                upButton.onclick = (event) => {
                    event.stopPropagation(); // Prevent selecting the "Up Level" button itself
                    loadDirectoryContent(parentPath);
                };
                upButton.innerHTML = `
                    <i class="bi bi-arrow-up-circle-fill me-2"></i>
                    Subir nivel
                `;
                browserContent.appendChild(upButton);
            }
            
            // Display directories first, then files
            data.items.forEach(item => {
                const itemElement = document.createElement('button'); // Use button for better click handling
                itemElement.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';
                
                const iconClass = item.is_dir ? 'bi-folder-fill text-warning' : 'bi-file-earmark-fill text-primary';
                
                itemElement.innerHTML = `
                    <div class="d-flex align-items-center flex-grow-1 text-start">
                        <i class="bi ${iconClass} me-2"></i>
                        ${item.name}
                    </div>
                    <div class="btn-group btn-group-sm" role="group" onclick="event.stopPropagation()"> ${item.is_file ? 
                            `<button type="button" class="btn btn-outline-secondary" onclick="setModalPath('appendModal', '${item.path}')" title="Agregar Contenido">
                                <i class="bi bi-plus-circle"></i>
                            </button>` : ''
                        }
                        <button type="button" class="btn btn-outline-secondary" onclick="setModalPath('renameModal', '${item.path}', '${item.name}')" title="Renombrar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger" onclick="setModalPath('deleteModal', '${item.path}')" title="Eliminar">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                 // Add click listener for item selection
                itemElement.addEventListener('click', (event) => {
                     // Prevent selecting the item if a button within it was clicked
                     if (!event.target.closest('.btn-group')) {
                        selectItem(item.path, item.is_file, itemElement);
                        // If it's a directory, load its content on click
                        if (item.is_dir) {
                            loadDirectoryContent(item.path);
                        }
                     }
                });

                browserContent.appendChild(itemElement);
            });
            
            // Optional: Show a success message for initial load, but might be too frequent
            // showAlert('success', 'Directorio cargado correctamente', 
            //     `Mostrando ${data.items.length} elementos en ${data.current_path_display}`);
        } else {
            // Show error message from the backend
            showAlert('danger', 'Error al cargar el directorio', data.message || 'Por favor, intenta nuevamente');
        }
    } catch (error) {
        console.error('Error al cargar el contenido del directorio:', error);
        // Show a generic error message in case of network issues or unhandled exceptions
        showAlert('danger', 'Error de conexión o del servidor', 
            'No se pudo cargar el contenido del directorio. Por favor, verifica la consola para más detalles.');
    }
}

// Function to preview file content
async function previewFile(path) {
    try {
        const response = await fetch(`/api/get-file-content?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        const previewDiv = document.getElementById('file-preview');
        if (!previewDiv) {
             console.error("Elemento '#file-preview' no encontrado.");
             showAlert('danger', 'Error interno', 'No se encontró el panel de previsualización.');
             return;
        }

        if (data.success) {
            // Display the file path and content
            previewDiv.innerHTML = `
                <div class="mb-2">
                    <small class="text-muted">Ruta: ${path}</small>
                </div>
                <pre class="bg-white p-2 rounded-3 overflow-auto flex-grow-1"><code>${escapeHTML(data.content)}</code></pre>
            `;
            // showAlert('success', 'Archivo previsualizado correctamente', `Mostrando contenido de ${path}`); // Optional alert
        } else {
             // Display error message in the preview panel
             previewDiv.innerHTML = `
                <div class="text-muted text-center py-5">
                    <i class="bi bi-x-circle-fill text-danger fs-4 mb-2"></i>
                    <p>Error al cargar el archivo: ${data.message || 'Desconocido'}</p>
                </div>
            `;
            showAlert('danger', 'Error al previsualizar el archivo', data.message || 'Por favor, intenta nuevamente');
        }
    } catch (error) {
        console.error('Error al previsualizar el archivo:', error);
         const previewDiv = document.getElementById('file-preview');
         previewDiv.innerHTML = `
            <div class="text-muted text-center py-5">
                <i class="bi bi-x-circle-fill text-danger fs-4 mb-2"></i>
                <p>Error de conexión o del servidor al previsualizar.</p>
            </div>
        `;
        showAlert('danger', 'Error de conexión o del servidor', 
            'No se pudo previsualizar el archivo. Por favor, verifica la consola para más detalles.');
    }
}

// Helper function to escape HTML characters for safe display in <pre><code>
function escapeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}


// Function to update the current content in the append modal preview area
async function updateAppendModalContent(path) {
    try {
        const response = await fetch(`/api/get-file-content?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        const previewArea = document.getElementById('appendFileContentPreview');
         if (!previewArea) {
             console.error("Elemento '#appendFileContentPreview' no encontrado.");
             return; // Cannot update if element doesn't exist
         }

        if (data.success) {
            previewArea.value = data.content;
            // showAlert('success', 'Contenido actual cargado', `Para ${path}`); // Optional alert
        } else {
            // Display error or clear preview if content cannot be loaded
            previewArea.value = `Error al cargar contenido: ${data.message || 'Desconocido'}`;
             console.error('Error al cargar contenido para previsualización en modal de append:', data.message);
        }
    } catch (error) {
        console.error('Error al cargar el contenido del archivo para previsualización en modal de append:', error);
         const previewArea = document.getElementById('appendFileContentPreview');
         if (previewArea) {
             previewArea.value = `Error de conexión o del servidor al cargar contenido.`;
         }
    }
}

// Function to set modal specific data before showing it
function setModalPath(modalId, path, currentName = '') {
    const modalElement = document.getElementById(modalId);
    if (!modalElement) {
        console.error(`Modal con ID "${modalId}" no encontrado.`);
        showAlert('danger', 'Error interno', `Modal "${modalId}" no encontrado.`);
        return;
    }
    // const modal = new bootstrap.Modal(modalElement); // Don't create a new modal instance here

    // Set the path in the corresponding modal input field
    if (modalId === 'renameModal') {
        document.getElementById('renameItemPath').value = path;
        document.getElementById('renameItemName').value = currentName; // Pre-fill with current name
    } else if (modalId === 'deleteModal') {
        document.getElementById('deleteItemPath').value = path;
        // Optionally display the item name in the modal confirmation text
        const itemNameDisplay = document.getElementById('deleteItemNameDisplay');
        if (itemNameDisplay) {
             itemNameDisplay.textContent = `"${path.split('/').pop()}"`;
        }
    } else if (modalId === 'appendModal') {
        document.getElementById('appendFilePath').value = path;
        updateAppendModalContent(path); // Load and display current content for append
    } 
    // Note: createDirModal and createFileModal paths are set via the 'show.bs.modal' listener

    // Now, show the modal using Bootstrap's API
    const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
    modalInstance.show();
}

// Function to handle file search
let searchTimeout;

async function searchFiles() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    // Get the current path from the displayed element
    const currentPathDisplay = document.getElementById('currentPath').textContent;
    // Extract the relative path by removing "data/" prefix
    const currentPath = currentPathDisplay.startsWith('data/') ? currentPathDisplay.substring(5) : '';
    
    // Clear previous timeout if user is typing quickly
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // If search term is empty, load the current directory content instead
    if (searchTerm.length === 0) {
        loadDirectoryContent(currentPath);
        return;
    }

    // Format path for the API request (remove leading/trailing slashes if any)
    const formattedPath = currentPath ? currentPath.replace(/^\/|\/$/g, '') : '';
    
    // Show a loading indicator in the browser content area
    const browserContent = document.getElementById('browser-content');
    browserContent.innerHTML = `
        <div class="text-center py-4">
            <div class="spinner-border text-primary" role="status">
                <span class="visually-hidden">Buscando...</span>
            </div>
            <p class="mt-2">Buscando "${escapeHTML(searchTerm)}"...</p>
        </div>
    `;

    // Add a small delay before searching to avoid excessive requests
    searchTimeout = setTimeout(async () => {
        try {
            // Perform the search API call
            const response = await fetch(`/api/search?term=${encodeURIComponent(searchTerm)}&path=${encodeURIComponent(formattedPath)}`);
            const data = await response.json();
            
            if (data.success) {
                // Display search results
                displaySearchResults(data.results, searchTerm);
                 // showAlert('success', data.message); // Optional alert for search results count
            } else {
                // Show error message from backend and revert to current directory view
                showAlert('danger', data.message || 'Error en la búsqueda');
                loadDirectoryContent(formattedPath);
            }
        } catch (error) {
            console.error('Error al realizar la búsqueda:', error);
            // Show a generic error message
            showAlert('danger', 'Error de conexión o del servidor', 
                'No se pudo realizar la búsqueda. Por favor, verifica la consola para más detalles.');
            // Revert to current directory view on error
            loadDirectoryContent(formattedPath);
        }
    }, 300); // 300ms delay
}

// Function to display search results in the browser content area
function displaySearchResults(results, searchTerm) {
    const browserContent = document.getElementById('browser-content');
    browserContent.innerHTML = ''; // Clear previous content

    if (results.length === 0) {
        browserContent.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-search" style="font-size: 2rem;"></i>
                <h5 class="mt-3">No se encontraron resultados para "${escapeHTML(searchTerm)}"</h5>
                <button class="btn btn-primary mt-3" onclick="loadDirectoryContent('')">
                    <i class="bi bi-arrow-left"></i> Volver al explorador
                </button>
            </div>
        `;
        return;
    }

    let html = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <h5><i class="bi bi-search me-2"></i>Resultados para "${escapeHTML(searchTerm)}"</h5>
                <p class="text-muted small">${results.length} elementos encontrados</p>
            </div>
            <button class="btn btn-outline-secondary btn-sm" onclick="loadDirectoryContent('')">
                <i class="bi bi-arrow-left"></i> Volver
            </button>
        </div>
        <div class="list-group"> `;

    results.forEach(item => {
        const icon = item.is_dir ? 'bi-folder-fill text-warning' : 'bi-file-earmark-fill text-primary';
        // Determine the action when clicking the item based on type
        const itemClickAction = item.is_dir ? `loadDirectoryContent('${item.path}')` : `previewFile('${item.path}')`;
        
        html += `
            <button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center">
                <div class="d-flex align-items-center flex-grow-1 text-start" onclick="${itemClickAction}">
                    <i class="bi ${icon} me-2"></i>
                    <span class="item-name">${highlightMatches(escapeHTML(item.name), escapeHTML(searchTerm))}</span>
                    <small class="text-muted ms-2">${item.path}</small>
                </div>
                <div class="btn-group btn-group-sm" role="group" onclick="event.stopPropagation()"> ${item.is_file ? 
                        `<button type="button" class="btn btn-outline-secondary" onclick="setModalPath('appendModal', '${item.path}')" title="Agregar Contenido">
                            <i class="bi bi-plus-circle"></i>
                        </button>` : ''
                    }
                    <button type="button" class="btn btn-outline-secondary" onclick="setModalPath('renameModal', '${item.path}', '${item.name}')" title="Renombrar">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button type="button" class="btn btn-outline-danger" onclick="setModalPath('deleteModal', '${item.path}')" title="Eliminar">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </button>
        `;
    });

    html += `</div>`; // Close list-group
    browserContent.innerHTML = html;
}

// Function to highlight search term matches in item names
function highlightMatches(text, searchTerm) {
    if (!searchTerm) return text;
    // Use a regular expression to find all occurrences of the search term (case-insensitive)
    const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
    // Replace matches with the same text wrapped in a highlight span
    return text.replace(regex, '<span class="bg-warning text-dark rounded-1 px-1">$1</span>');
}

// Helper function to escape special characters for use in a regular expression
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // $& means the whole matched string
}

// --- Form Submission Handlers ---

// Handle Create Directory Form Submission
document.getElementById('createDirForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent default form submission
    // console.log('Evento submit de createDirForm activado!'); // Para verificar
    
    const path = document.getElementById('createDirPath').value || ''; // Get parent path from modal input
    const formattedPath = path === '/' ? '' : path.replace(/^\/|\/$/g, ''); // Clean up path format, handle root as ""
    const name = document.getElementById('createDirName').value.trim(); // Get new directory name

    if (!name) {
         showAlert('danger', 'El nombre de la carpeta no puede estar vacío.');
         return;
    }
    
    // console.log('Carga de solicitud para crear directorio:', { path: formattedPath, name }); // Para verificar

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/create_dir', { 
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, name }),
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/create_dir:', data); // Para verificar
        
        if (data.success) {
            // console.log('Directorio creado exitosamente, mostrando alerta.'); // Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createDirModal'));
            if (modal) modal.hide();
            // Reload the current directory content to show the new folder
            loadDirectoryContent(formattedPath);
            // Show success message from the backend
            showAlert('success', data.message); 
        } else {
            // console.log('Fallo al crear directorio, mostrando alerta de error.'); // Para verificar
            // Show error message from the backend
            showAlert('danger', data.message || 'Error al crear el directorio');
        }
    } catch (error) {
        console.error('Error al crear directorio:', error); // Log error to console
        // Show a generic error message for network/server issues
        showAlert('danger', 'Error de conexión o del servidor', error.message || 'No se pudo crear la carpeta.');
    }
});

// Handle Create File Form Submission
document.getElementById('createFileForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent default form submission
    // console.log('Evento submit de createFileForm activado!'); //Para verificar

    const path = document.getElementById('createFilePath').value || ''; // Get parent path from modal input
    const formattedPath = path === '/' ? '' : path.replace(/^\/|\/$/g, ''); // Clean up path format, handle root as ""
    const name = document.getElementById('createFileName').value.trim(); // Get new file name
    const content = document.getElementById('createFileContent').value; // Get file content

    if (!name) {
         showAlert('danger', 'El nombre del archivo no puede estar vacío.');
         return;
    }
    
    // console.log('Carga de solicitud para crear archivo:', { path: formattedPath, name, content }); // Para verificar

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/create_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, name, content }),
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/create_file:', data); //Para verificar

        if (data.success) {
            // console.log('Archivo creado exitosamente, mostrando alerta.'); //Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createFileModal'));
            if (modal) modal.hide();
            // Reload the current directory content to show the new file
            loadDirectoryContent(formattedPath);
            // Show success message from the backend
            showAlert('success', data.message); 
        } else {
            // console.log('Fallo al crear archivo, mostrando alerta de error.'); //Para verificar
            // Show error message from the backend
            showAlert('danger', data.message || 'Error al crear el archivo');
        }
    } catch (error) {
        console.error('Error al crear archivo:', error); // Log error to console
        // Show a generic error message for network/server issues
        showAlert('danger', 'Error de conexión o del servidor', error.message || 'No se pudo crear el archivo.');
    }
});

// Handle Append File Form Submission
document.getElementById('appendFileForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent default form submission
    // console.log('Evento submit de appendFileForm activado!'); // Para verificar

    const path = document.getElementById('appendFilePath').value || ''; // Get file path from modal input
    const formattedPath = path ? path.replace(/^\/|\/$/g, '') : ''; // Clean up path format
    const content = document.getElementById('appendFileContent').value; // Get content to append

    if (!content.trim()) {
         showAlert('danger', 'El contenido a agregar no puede estar vacío.');
         return;
    }
    
    // console.log('Carga de solicitud para añadir contenido:', { path: formattedPath, content }); // Para verificar

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/append_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, content }),
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/append_file:', data); // Para verificar
        
        if (data.success) {
            // console.log('Contenido añadido exitosamente, mostrando alerta.'); // Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('appendModal'));
            if (modal) modal.hide();
            // Reload the parent directory content (or the file itself if you implement that)
            const parentPath = formattedPath.split('/').slice(0, -1).join('/');
            loadDirectoryContent(parentPath); 
            // Show success message from the backend
            showAlert('success', data.message); 
        } else {
            // console.log('Fallo al añadir contenido, mostrando alerta de error.'); // Para verificar
            // Show error message from the backend
            showAlert('danger', data.message || 'Error al agregar contenido');
        }
    } catch (error) {
        console.error('Error al añadir contenido:', error); // Log error to console
        // Show a generic error message for network/server issues
        showAlert('danger', 'Error de conexión o del servidor', error.message || 'No se pudo agregar el contenido.');
    }
});

// Handle Delete Item Form Submission
document.getElementById('deleteItemForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent default form submission
    // console.log('Evento submit de deleteItemForm activado!'); // Para verificar

    const path = document.getElementById('deleteItemPath').value || ''; // Get item path from modal input
    const formattedPath = path ? path.replace(/^\/|\/$/g, '') : ''; // Clean up path format
    // const itemName = path.split('/').pop(); // Item name can be obtained from backend message

    if (!path) {
         showAlert('danger', 'No se especificó ningún item para eliminar.');
         return;
    }
    
    // console.log('Carga de solicitud para eliminar item:', { path: formattedPath }); // Para verificar

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath }),
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/delete:', data); //Para verificar
        
        if (data.success) {
            // console.log('Elemento eliminado exitosamente, mostrando alerta.'); //Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
            if (modal) modal.hide();
            // Reload the parent directory content
            const parentPath = formattedPath.split('/').slice(0, -1).join('/');
            loadDirectoryContent(parentPath);
            // Show success message from the backend
            showAlert('success', data.message); 
        } else {
            // console.log('Fallo al eliminar elemento, mostrando alerta de error.'); //Para verificar
            // Show error message from the backend
            showAlert('danger', data.message || 'Error al eliminar el item');
        }
    } catch (error) {
        console.error('Error al eliminar elemento:', error); // Log error to console
        // Show a generic error message for network/server issues
        showAlert('danger', 'Error de conexión o del servidor', error.message || 'No se pudo eliminar el item.');
    }
});

// Handle Rename Item Form Submission
document.getElementById('renameItemForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent default form submission
    // console.log('Evento submit de renameItemForm activado!'); // Para verificar

    const oldPath = document.getElementById('renameItemPath').value.trim(); // Get old path from modal input
    const newName = document.getElementById('renameItemName').value.trim(); // Get new name from modal input
    
    // console.log('Carga de solicitud para renombrar item:', { oldPath: oldPath, newName: newName }); // Para verificar

    if (!oldPath || !newName) {
        showAlert('danger', 'Por favor, ingrese una ruta y un nuevo nombre');
        return;
    }

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/rename_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                oldPath: oldPath,
                newName: newName
            }),
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/rename_item:', data); // Para verificar
        
        if (data.success) {
            // console.log('Elemento renombrado exitosamente, mostrando alerta.'); // Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('renameModal'));
            if (modal) modal.hide();
            // Reload the parent directory content
            const parentPath = oldPath.split('/').slice(0, -1).join('/');
            loadDirectoryContent(parentPath);
            // Show success message from the backend
            showAlert('success', data.message); 
        } else {
            // console.log('Fallo al renombrar elemento, mostrando alerta de error.'); // Para verificar
            // Show error message from the backend
            showAlert('danger', data.message || 'Error al renombrar');
        }
    } catch (error) {
        console.error('Error al renombrar:', error); // Log error to console
        // Show a generic error message for network/server issues
        showAlert('danger', 'Error de conexión o del servidor', error.message || 'No se pudo renombrar el item.');
    }
});


// --- Initialization ---

// Initialize the file browser and set up event listeners when the DOM is fully loaded
document.addEventListener('DOMContentLoaded', () => {
    // Set up the search input listener
    document.getElementById('searchInput').addEventListener('input', function() {
        // Clear previous timeout and set a new one for delayed search
        clearTimeout(window.searchTimeout);
        window.searchTimeout = setTimeout(searchFiles, 300); // Search after 300ms of inactivity
    });
    
    // Load the initial directory content (root 'data' directory)
    loadDirectoryContent();
    
    // Configure modals to clear their forms and set path inputs when shown/hidden
    ['createDirModal', 'createFileModal', 'appendModal', 'deleteModal', 'renameModal'].forEach(modalId => {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            // Add listener for when the modal is about to be shown
            modalElement.addEventListener('show.bs.modal', function() {
                // Get the current path from the displayed element
                const currentPathDisplay = document.getElementById('currentPath').textContent;
                // Extract the relative path by removing "data/" prefix
                const currentPath = currentPathDisplay.startsWith('data/') ? currentPathDisplay.substring(5) : '';

                // Set the parent path in the creation modals
                if (modalId === 'createDirModal') {
                    document.getElementById('createDirPath').value = currentPath || '/'; // Use '/' for root display in modal
                } else if (modalId === 'createFileModal') {
                    document.getElementById('createFilePath').value = currentPath || '/'; // Use '/' for root display in modal
                }
                // For appendModal, renameModal, deleteModal, the path is set by setModalPath when clicking the item button.
                // We now handle sidebar button clicks separately below.
            });

             // Add listener for when the modal is hidden
            modalElement.addEventListener('hidden.bs.modal', function() {
                const form = this.querySelector('form');
                if (form) {
                    form.reset(); // Reset the form fields
                }
                 // Clear file preview in append modal
                if (modalId === 'appendModal') {
                     const previewArea = document.getElementById('appendFileContentPreview');
                     if (previewArea) {
                         previewArea.value = '';
                     }
                }
                 // Clear selection when any modal is closed
                 if (selectedItemElement) {
                    selectedItemElement.classList.remove('list-group-item-primary');
                }
                selectedItemPath = null;
                selectedItemIsFile = false;
                selectedItemElement = null;
                updateSidebarButtonStates(); // Disable action buttons
                // Clear preview when selection is cleared
                const previewDiv = document.getElementById('file-preview');
                if (previewDiv) {
                        previewDiv.innerHTML = `
                        <div class="text-muted text-center py-5 d-flex align-items-center justify-content-center flex-grow-1">
                            Selecciona un archivo para ver su contenido
                        </div>
                    `;
                }
            });
        } else {
            console.warn(`Modal element with ID "${modalId}" not found.`);
        }
    });

    // --- Sidebar Action Button Event Listeners ---
    // These buttons now rely on item selection

    // Create Directory button - always enabled, opens modal with current path
    const sidebarCreateDirBtn = document.getElementById('sidebarCreateDirBtn');
    if (sidebarCreateDirBtn) {
        sidebarCreateDirBtn.addEventListener('click', () => {
            const modalElement = document.getElementById('createDirModal');
            if (modalElement) {
                const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                modalInstance.show(); // show.bs.modal listener will set the path
            }
        });
    } else { console.warn("Sidebar Create Directory button not found."); }

    // Create File button - always enabled, opens modal with current path
    const sidebarCreateFileBtn = document.getElementById('sidebarCreateFileBtn');
     if (sidebarCreateFileBtn) {
        sidebarCreateFileBtn.addEventListener('click', () => {
            const modalElement = document.getElementById('createFileModal');
            if (modalElement) {
                const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                modalInstance.show(); // show.bs.modal listener will set the path
            }
        });
     } else { console.warn("Sidebar Create File button not found."); }


    // Append Content button - requires a selected file
    const sidebarAppendBtn = document.getElementById('sidebarAppendBtn');
    if (sidebarAppendBtn) {
        sidebarAppendBtn.addEventListener('click', () => {
            if (selectedItemPath && selectedItemIsFile) {
                setModalPath('appendModal', selectedItemPath); // Open modal and set path
            } else {
                showAlert('warning', 'Por favor, selecciona un archivo para agregar contenido.');
            }
        });
    } else { console.warn("Sidebar Append button not found."); }

    // Delete button - requires a selected item (file or directory)
    const sidebarDeleteBtn = document.getElementById('sidebarDeleteBtn');
    if (sidebarDeleteBtn) {
        sidebarDeleteBtn.addEventListener('click', () => {
            if (selectedItemPath) {
                setModalPath('deleteModal', selectedItemPath); // Open modal and set path
            } else {
                showAlert('warning', 'Por favor, selecciona un archivo o directorio para eliminar.');
            }
        });
    } else { console.warn("Sidebar Delete button not found."); }


    // Rename button - requires a selected item (file or directory)
    const sidebarRenameBtn = document.getElementById('sidebarRenameBtn');
     if (sidebarRenameBtn) {
        sidebarRenameBtn.addEventListener('click', () => {
            if (selectedItemPath) {
                 // Need the item name for the rename modal - get it from the path
                 const itemName = selectedItemPath.split('/').pop();
                setModalPath('renameModal', selectedItemPath, itemName); // Open modal and set path and name
            } else {
                showAlert('warning', 'Por favor, selecciona un archivo o directorio para renombrar.');
            }
        });
     } else { console.warn("Sidebar Rename button not found."); }


    // Initialize sidebar button states (they start disabled)
    updateSidebarButtonStates();
});
