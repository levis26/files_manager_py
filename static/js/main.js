// Variables globales para rastrear el elemento seleccionado
let selectedItemPath = null;
let selectedItemIsFile = false;
let selectedItemElement = null; // Referencia al elemento DOM actualmente seleccionado
let currentPreviewContent = null; // Variable global para almacenar el contenido del modal

// Función para mostrar alertas con más detalles
function showAlert(type, message, extraInfo = '') {
    // console.log(`showAlert llamada: Tipo=${type}, Mensaje="${message}", InfoExtra="${extraInfo}"`); // Para depuración
    const alertDiv = document.createElement('div');
    // Utilizar clases de alerta de Bootstrap para el estilo
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';

    // Añadir icono basado en el tipo de alerta usando Bootstrap Icons
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

    // Insertar al principio del contenedor principal donde aparecerán las alertas
    const container = document.querySelector('.container'); // Seleccionar el contenedor principal de Bootstrap
    // console.log('Elemento "container" para la alerta:', container); // Para depuración
    if (!container) {
        console.error("No se encontró el elemento '.container' para mostrar la alerta.");
        // Fallback: Log to console if container not found
        console.log(`ALERTA (${type}): ${message} - ${extraInfo}`);
        return;
    }

    // Buscar el primer hijo que NO sea otra alerta para insertar antes de él
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
         // Si todos los hijos son alertas o el contenedor está vacío, simplemente agregar
        container.appendChild(alertDiv);
    }

    // Ocultar automáticamente después de 5 segundos
    setTimeout(() => {
        // Asegurarse de que el elemento aún existe antes de intentar cerrarlo
        if (alertDiv.parentNode) {
            const bsAlert = new bootstrap.Alert(alertDiv);
            bsAlert.close();
        }
    }, 5000);
}

// --- Eliminada: updateSidebarButtonStates ya no es necesaria ya que los botones de acción están en la lista de items ---
// function updateSidebarButtonStates() { ... }

// Función para manejar la selección de elementos en la lista del navegador
function selectItem(path, isFile, element) {
    // Limpiar el resaltado de la selección anterior
    if (selectedItemElement) {
        selectedItemElement.classList.remove('list-group-item-primary'); // Utilizar color primario de Bootstrap para el resaltado
    }

    // Establecer nueva selección
    selectedItemPath = path;
    selectedItemIsFile = isFile;
    selectedItemElement = element;

    // Añadir resaltado al elemento seleccionado
    if (selectedItemElement) {
        selectedItemElement.classList.add('list-group-item-primary');
    }

    // --- Eliminada: updateSidebarButtonStates ya no se llama aquí ---
    // updateSidebarButtonStates(); // Actualizar estados de los botones del sidebar basado en la nueva selección

    // Si se selecciona un archivo, previsualizarlo automáticamente
    if (isFile) {
        previewFile(path);
    } else {
        // Limpiar la previsualización si se selecciona un directorio o se limpia la selección
        const previewDiv = document.getElementById('file-preview');
        if (previewDiv) {
             previewDiv.innerHTML = `
                <div class="text-muted text-center py-5 d-flex align-items-center justify-content-center flex-grow-1">
                    <i class="bi bi-file-earmark-text fs-1 mb-3"></i>
                    <p>Selecciona un archivo para ver su contenido.</p>
                </div>
            `;
            // Hide maximize button
            const maximizeBtn = document.getElementById('maximizePreviewBtn');
            if (maximizeBtn) maximizeBtn.style.visibility = 'hidden';
             // Clear stored content
            currentPreviewContent = null;
        }
    }
}

// --- Eliminada: clearSelection ya no es necesaria si la selección se maneja solo en los items clickeables ---
// function clearSelection(event) { ... }

// Function to add click handler for the update button (now renamed to Recargar/Actualizar and placed in header)
function addUpdateButtonHandler() {
    // Assuming ID added as proposed earlier for robust selection
    const updateButton = document.getElementById('updateButton'); // ID del botón de Recargar/Actualizar en el header
    if (updateButton) {
        updateButton.addEventListener('click', async (e) => {
            e.preventDefault(); // Prevent any default behavior

            // Modificación clave: Llamar loadDirectoryContent con una cadena vacía
            // para cargar el contenido del directorio raíz ('data/').
            const rootPath = ''; // Representa el directorio raíz relativo a DATA_DIR

            try {
                // Cargar el contenido del directorio raíz
                await loadDirectoryContent(rootPath);
                // Actualizar el mensaje de éxito para reflejar que se ha vuelto a la raíz
                showAlert('success', 'Explorador actualizado', 'Se ha vuelto a la raíz principal.');
                 // Opcional: Limpiar la barra de búsqueda al volver a la raíz
                 const searchInput = document.getElementById('searchInput');
                 if(searchInput) {
                     searchInput.value = '';
                 }
                 // Opcional: Limpiar cualquier resultado de búsqueda si se mostraba
                 // La función loadDirectoryContent ya maneja esto al borrar el contenido anterior del navegador.

            } catch (error) {
                console.error('Error al volver a la raíz:', error);
                showAlert('danger', 'Error al actualizar', 'No se pudo volver a la raíz principal. Por favor, intenta nuevamente.');
            }
        });
    } else {
        // Log an error if the button element is not found (useful for debugging)
        console.error("Button with ID 'updateButton' not found.");
    }
}

// --- Eliminada: initializeUpdateButton era redundante con addUpdateButtonHandler ---
// function initializeUpdateButton() { ... }


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
        // --- Eliminada: updateSidebarButtonStates ya no se llama aquí ---
        // updateSidebarButtonStates(); // Disable action buttons

        // Clear preview when changing directories
        const previewDiv = document.getElementById('file-preview');
        if (previewDiv) {
                previewDiv.innerHTML = `
                <div class="text-muted text-center py-5 d-flex align-items-center justify-content-center flex-grow-1">
                    <i class="bi bi-file-earmark-text fs-1 mb-3"></i>
                    <p>Selecciona un archivo para ver su contenido.</p>
                </div>
            `;
             // Hide maximize button
            const maximizeBtn = document.getElementById('maximizePreviewBtn');
            if (maximizeBtn) maximizeBtn.style.visibility = 'hidden';
             // Clear stored content
            currentPreviewContent = null;
        }

        // Show loading state
        const browserContent = document.getElementById('browser-content');
         if (browserContent) {
              browserContent.innerHTML = `
                 <div class="text-muted text-center py-5 loading-state">
                     <div class="spinner-border text-primary" role="status">
                         <span class="visually-hidden">Cargando...</span>
                     </div>
                     <p class="mt-2">Cargando...</p>
                 </div>
             `;
         } else {
             console.error("Elemento '#browser-content' no encontrado.");
             showAlert('danger', 'Error interno', 'No se encontró el área de contenido del navegador.');
             return;
         }


        // Construct the API URL with the encoded path
        const response = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
        // Parse the JSON response
        const data = await response.json();

        if (data.success) {
            // Update the displayed current path
            document.getElementById('currentPath').textContent = data.current_path_display || 'data/'; // Ensure trailing slash for root display

            browserContent.innerHTML = ''; // Clear loading state or previous content

            // --- CÁLCULO MEJORADO DE LA RUTA PADRE ---
            let parentPath = '';
            if (path && path !== '') {
                // Eliminar barra final si existe
                const cleanPath = path.endsWith('/') ? path.slice(0, -1) : path;
                // Dividir por barras y filtrar segmentos vacíos
                const segments = cleanPath.split('/').filter(segment => segment !== '');
                
                if (segments.length > 0) {
                    segments.pop(); // Eliminar el último segmento
                    parentPath = segments.join('/'); // Unir el resto
                }
                // Si segments.length es 0 después de pop(), parentPath será '' (raíz)
            }
            // --------------------------------------------

            // Mostrar el botón de subir nivel
            const upButton = document.createElement('button');
            upButton.className = 'list-group-item list-group-item-action d-flex align-items-center';
            upButton.innerHTML = `
                <i class="bi bi-arrow-up-circle-fill me-2"></i>
                .. Subir nivel
            `;
            
            if (path !== '') { // Si no estamos en el directorio raíz
                upButton.onclick = (event) => {
                    event.stopPropagation();
                    loadDirectoryContent(parentPath); // Usar parentPath calculado
                };
                upButton.style.cursor = 'pointer';
            } else {
                upButton.style.opacity = '0.5';
                upButton.style.cursor = 'not-allowed';
                upButton.title = 'Ya estás en el directorio raíz';
            }

            browserContent.appendChild(upButton);


            // Crear un div para el contenido principal (items y mensaje de vacío)
            const contentDiv = document.createElement('div');
            contentDiv.className = 'list-group';

            // Si el directorio está vacío
            if (data.items.length === 0) {
                contentDiv.innerHTML = `
                    <div class="text-muted text-center py-5 empty-state">
                        <i class="bi bi-folder2-open fs-1 mb-3"></i>
                        <p>${path === '' ? 'Este directorio está vacío.' : 'Esta carpeta está vacía.'}</p>
                    </div>
                `;
            } else {
                // Si el directorio no está vacío, mostrar los items
                data.items.forEach(item => {
                    if (item.name === '..') return; // Skip the ".." item

                    const itemElement = document.createElement('button');
                    itemElement.className = 'list-group-item list-group-item-action d-flex justify-content-between align-items-center';

                    const iconClass = item.is_dir ? 'bi-folder-fill text-warning' : 'bi-file-earmark-fill text-primary';

                    itemElement.innerHTML = `
                        <div class="d-flex align-items-center flex-grow-1 text-start">
                            <i class="bi ${iconClass} me-2"></i>
                            ${escapeHTML(item.name)}
                        </div>
                        <div class="btn-group btn-group-sm" role="group" onclick="event.stopPropagation()" title="Acciones">
                            ${item.is_file ?
                                `<button type="button" class="btn btn-outline-secondary" onclick="setModalPath('appendModal', '${escapeHTML(item.path)}') ; return false;" title="Agregar Contenido">
                                    <i class="bi bi-plus-circle"></i>
                                </button>` : ''
                            }
                            <button type="button" class="btn btn-outline-secondary" onclick="setModalPath('renameModal', '${escapeHTML(item.path)}', '${escapeHTML(item.name)}') ; return false;" title="Renombrar">
                                <i class="bi bi-pencil"></i>
                            </button>
                            <button type="button" class="btn btn-outline-danger" onclick="setModalPath('deleteModal', '${escapeHTML(item.path)}') ; return false;" title="Eliminar">
                                <i class="bi bi-trash"></i>
                            </button>
                        </div>
                    `;

                    itemElement.addEventListener('click', (event) => {
                        if (!event.target.closest('.btn-group')) {
                            selectItem(item.path, item.is_file, itemElement);
                            if (item.is_dir) {
                                loadDirectoryContent(item.path);
                            }
                        }
                    });

                    contentDiv.appendChild(itemElement);
                });
            }

            // Agregar el contenido principal al browserContent
            browserContent.appendChild(contentDiv);

            // Optional: Show a success message for initial load, but might be too frequent
            // showAlert('success', 'Directorio cargado correctamente',
            //     `Mostrando ${data.items.length} elementos en ${data.current_path_display}`);
        } else {
            // If the API returns success: false, show the error message from the backend.
             console.error('Error API al cargar directorio:', data.message); // Log in browser console
             // Display the error state in the browser area.
             browserContent.innerHTML = `
                 <div class="text-muted text-center py-5 preview-error-state">
                     <i class="bi bi-x-circle-fill text-danger fs-1 mb-3"></i>
                     <p>Error al cargar el directorio:</p>
                     <p>${data.message || 'Por favor, intenta nuevamente'}</p> {/* Show backend message or a generic one */}
                 </div>
             `;
            // Show an alert to the user.
            showAlert('danger', 'Error al cargar el directorio', data.message || 'Por favor, intenta nuevamente');
        }
    } catch (error) {
        // Catch fetch request errors (e.g., network error, server not responding).
        console.error('Error al cargar el contenido del directorio:', error); // Log in browser console
         // Display a generic error state in the browser area.
         const browserContent = document.getElementById('browser-content');
         if (browserContent) {
              browserContent.innerHTML = `
                 <div class="text-muted text-center py-5 preview-error-state">
                     <i class="bi bi-x-circle-fill text-danger fs-1 mb-3"></i>
                     <p>Error de conexión o del servidor:</p>
                     <p>${error.message || 'No se pudo cargar el contenido del directorio.'}</p>
                 </div>
             `;
         }
        // Show an alert to the user.
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
        const maximizeBtn = document.getElementById('maximizePreviewBtn');

        if (!previewDiv) {
             console.error("Elemento '#file-preview' no encontrado.");
             showAlert('danger', 'Error interno', 'No se encontró el panel de previsualización.');
             if (maximizeBtn) maximizeBtn.style.visibility = 'hidden';
             currentPreviewContent = null;
             return;
        }

        if (data.success) {
            // Store the content globally for the modal
            currentPreviewContent = data.content;

            // Display the file path and content in the normal preview area
            previewDiv.innerHTML = `
                <div class="mb-2">
                    <small class="text-muted">Ruta: ${escapeHTML(path)}</small>
                </div>
                <pre class="bg-white p-2 rounded-3 overflow-auto flex-grow-1"><code>${escapeHTML(data.content)}</code></pre>
            `;
            // Show the maximize button
            if (maximizeBtn) maximizeBtn.style.visibility = 'visible';

            // showAlert('success', 'Archivo previsualizado correctamente', `Mostrando contenido de ${path}`); // Optional alert
        } else {
             // Display error message in the preview panel
             previewDiv.innerHTML = `
                <div class="text-muted text-center py-5 d-flex align-items-center justify-content-center flex-grow-1">
                    <i class="bi bi-x-circle-fill text-danger fs-4 mb-2"></i>
                    <p>Error al cargar el archivo:</p>
                    <p>${data.message || 'Desconocido'}</p>
                </div>
            `;
            // Hide maximize button on error
            if (maximizeBtn) maximizeBtn.style.visibility = 'hidden';
            // Clear stored content on error
            currentPreviewContent = null;

            showAlert('danger', 'Error al previsualizar el archivo', data.message || 'Por favor, intenta nuevamente');
        }
    } catch (error) {
        console.error('Error al previsualizar el archivo:', error);
         const previewDiv = document.getElementById('file-preview');
         if (previewDiv) {
             previewDiv.innerHTML = `
                <div class="text-muted text-center py-5 d-flex align-items-center justify-content-center flex-grow-1">
                    <i class="bi bi-x-circle-fill text-danger fs-4 mb-2"></i>
                    <p>Error de conexión o del servidor al previsualizar.</p>
                </div>
            `;
         }
         // Hide maximize button on error
        const maximizeBtn = document.getElementById('maximizePreviewBtn');
        if (maximizeBtn) maximizeBtn.style.visibility = 'hidden';
        // Clear stored content on error
        currentPreviewContent = null;

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
let searchTimeout; // Declared only once at the top level

async function searchFiles() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    // Get the current path from the displayed element
    const currentPathDisplay = document.getElementById('currentPath').textContent;
    // Extract the relative path by removing "Estás en: data/" prefix
    const currentPath = currentPathDisplay.replace('Estás en: ', '').trim(); // Get the full displayed path
    const relativePath = currentPath.startsWith('data/') ? currentPath.substring(5) : ''; // Get path relative to data/

    // Clear previous timeout if user is typing quickly
    if (searchTimeout) { // Referencing the top-level variable
        clearTimeout(searchTimeout); // Referencing the top-level variable
    }

    // If search term is empty, load the current directory content instead
    if (searchTerm.length === 0) {
        // Load the directory corresponding to the current displayed path
        loadDirectoryContent(relativePath);
        return;
    }

    // Format path for the API request (remove leading/trailing slashes if any)
    const formattedPath = relativePath ? relativePath.replace(/^\/|\/$/g, '') : '';

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
    window.searchTimeout = setTimeout(async () => { // Referencing the top-level variable via window
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
                loadDirectoryContent(formattedPath); // Revert to current directory view
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
        // Note: The onclick handler below is for the item element itself, not the buttons within it.
        // The buttons within the item element use setModalPath directly.
        // The item click should navigate for directories or select/preview for files.
        const itemClickAction = item.is_dir ? `loadDirectoryContent('${escapeHTML(item.path)}')` : `selectItem('${escapeHTML(item.path)}', true, this); previewFile('${escapeHTML(item.path)}')`;


        html += `
            <button type="button" class="list-group-item list-group-item-action d-flex justify-content-between align-items-center"
                    onclick="${itemClickAction}"> {/* Added onclick here for item navigation/selection */}
                <div class="d-flex align-items-center flex-grow-1 text-start">
                    <i class="bi ${icon} me-2"></i>
                    <span class="item-name">${highlightMatches(escapeHTML(item.name), escapeHTML(searchTerm))}</span>
                    <small class="text-muted ms-2">${escapeHTML(item.path)}</small>
                </div>
                 <div class="btn-group btn-group-sm" role="group" onclick="event.stopPropagation()" title="Acciones">
                    ${item.is_file ?
                            `<button type="button" class="btn btn-outline-secondary" onclick="setModalPath('appendModal', '${escapeHTML(item.path)}') ; return false;" title="Agregar Contenido">
                                <i class="bi bi-plus-circle"></i>
                            </button>` : ''
                        }
                        <button type="button" class="btn btn-outline-secondary" onclick="setModalPath('renameModal', '${escapeHTML(item.path)}', '${escapeHTML(item.name)}') ; return false;" title="Renombrar">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button type="button" class="btn btn-outline-danger" onclick="setModalPath('deleteModal', '${escapeHTML(item.path)}') ; return false;" title="Eliminar">
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

    const path = document.getElementById('createDirPath').value || ''; // Get parent path from modal input (e.g., '/' or 'some/dir')
    // The API expects the path relative to DATA_DIR, so if the modal shows '/', send ''
    const formattedPath = path === '/' ? '' : path; // Use path directly as it's relative to data/ or '' for root
    const name = document.getElementById('createDirName').value.trim(); // Get new directory name

    // console.log('Datos del formulario Crear Carpeta:', { path: path, name: name }); // Log raw form data
    // console.log('Datos a enviar a la API /api/create_dir:', { path: formattedPath, name: name }); // Log formatted data

    if (!name) {
         showAlert('danger', 'El nombre de la carpeta no puede estar vacío.');
         return;
    }

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/create_dir', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, name }), // Send formatted path
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/create_dir:', data); // Para verificar

        if (data.success) {
            // console.log('Directorio creado exitosamente, mostrando alerta.'); // Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createDirModal'));
            if (modal) modal.hide();
            // Reload the current directory content to show the new folder
            loadDirectoryContent(formattedPath); // Reload the parent directory
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

    const path = document.getElementById('createFilePath').value || ''; // Get parent path from modal input (e.g., '/' or 'some/dir')
    // The API expects the path relative to DATA_DIR, so if the modal shows '/', send ''
    const formattedPath = path === '/' ? '' : path; // Use path directly as it's relative to data/ or '' for root
    const name = document.getElementById('createFileName').value.trim(); // Get new file name
    const content = document.getElementById('createFileContent').value; // Get file content

    // console.log('Datos del formulario Crear Archivo:', { path: path, name: name, content: content }); // Log raw form data
    // console.log('Datos a enviar a la API /api/create_file:', { path: formattedPath, name: name, content: content }); // Log formatted data


    if (!name) {
         showAlert('danger', 'El nombre del archivo no puede estar vacío.');
         return;
    }

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/create_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, name, content }), // Send formatted path
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/create_file:', data); //Para verificar

        if (data.success) {
            // console.log('Archivo creado exitosamente, mostrando alerta.'); //Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('createFileModal'));
            if (modal) modal.hide();
            // Reload the current directory content to show the new file
            loadDirectoryContent(formattedPath); // Reload the parent directory
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
    // The path from setModalPath is already relative to data/ or '' for root
    const formattedPath = path; // Use path directly
    const content = document.getElementById('appendFileContent').value; // Get content to append

    // console.log('Datos del formulario Agregar Contenido:', { path: path, content: content }); // Log raw form data
    // console.log('Datos a enviar a la API /api/append_file:', { path: formattedPath, content: content }); // Log formatted data


    if (!content.trim()) {
         showAlert('danger', 'El contenido a agregar no puede estar vacío.');
         return;
    }

    try {
        // Send POST request to the backend API
        const response = await fetch('/api/append_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, content }), // Send formatted path
        });
        const data = await response.json(); // Parse JSON response
        // console.log('Respuesta de /api/append_file:', data); // Para verificar

        if (data.success) {
            // console.log('Contenido añadido exitosamente, mostrando alerta.'); // Para verificar
            // Hide the modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('appendModal'));
            if (modal) modal.hide();
            // Reload the parent directory content (or the file itself if you implement that)
            // Find the parent path of the modified file
            const parentPathParts = formattedPath.split('/');
            parentPathParts.pop(); // Remove the file name
            const parentPath = parentPathParts.join('/'); // Get the parent directory path
            loadDirectoryContent(parentPath); // Reload the parent directory
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

// Manejar envío del formulario de Eliminación
document.getElementById('deleteItemForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevenir envío por defecto del formulario
    // console.log('Evento submit de deleteItemForm activado!'); // Para depuración

    const path = document.getElementById('deleteItemPath').value || ''; // Obtener ruta del item del input del modal
     // La ruta de setModalPath ya está relativa a data/ o '' para la raíz
    const formattedPath = path; // Usar ruta directamente

    // console.log('Datos del formulario Eliminar Item:', { path: path }); // Log de datos del formulario
    // console.log('Datos a enviar a la API /api/delete:', { path: formattedPath }); // Log de datos formateados


    if (!path) {
         showAlert('danger', 'No se especificó ningún item para eliminar.');
         return;
    }

    try {
        // Enviar solicitud POST a la API del backend
        const response = await fetch('/api/delete', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath }), // Enviar ruta formateada
        });
        const data = await response.json(); // Procesar respuesta JSON
        // console.log('Respuesta de /api/delete:', data); // Para depuración

        if (data.success) {
            // console.log('Elemento eliminado exitosamente, mostrando alerta.'); // Para depuración
            // Ocultar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
            if (modal) modal.hide();
            // Recargar el contenido del directorio padre
            const parentPathParts = formattedPath.split('/');
            parentPathParts.pop(); // Eliminar el nombre del item
            const parentPath = parentPathParts.join('/'); // Obtener la ruta del directorio padre
            loadDirectoryContent(parentPath); // Recargar el directorio padre
            // Mostrar mensaje de éxito del backend
            showAlert('success', data.message);
        } else {
            // console.log('Fallo al eliminar elemento, mostrando alerta de error.'); // Para depuración
            // Mostrar mensaje de error del backend
            showAlert('danger', data.message || 'Error al eliminar el item');
        }
    } catch (error) {
        console.error('Error al eliminar elemento:', error); // Log error to console
        // Mostrar mensaje de error genérico para problemas de conexión o servidor
        showAlert('danger', 'Error de conexión o del servidor', error.message || 'No se pudo eliminar el item.');
    }
});

// Manejar envío del formulario de Renombrar
document.getElementById('renameItemForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevenir envío por defecto del formulario
    // console.log('Evento submit de renameItemForm activado!'); // Para depuración

    const oldPath = document.getElementById('renameItemPath').value.trim(); // Obtener ruta antigua del input del modal
    // La ruta de setModalPath ya está relativa a data/ o '' para la raíz
    const formattedOldPath = oldPath; // Usar ruta directamente
    const newName = document.getElementById('renameItemName').value.trim(); // Obtener nuevo nombre del input del modal

     // console.log('Datos del formulario Renombrar Item:', { oldPath: oldPath, newName: newName }); // Log de datos del formulario
    // console.log('Datos a enviar a la API /api/rename_item:', { oldPath: formattedOldPath, newName: newName }); // Log de datos formateados


    if (!oldPath || !newName) {
        showAlert('danger', 'Por favor, ingrese una ruta y un nuevo nombre');
        return;
    }

    try {
        // Enviar solicitud POST a la API del backend
        const response = await fetch('/api/rename_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                oldPath: formattedOldPath, // Enviar ruta antigua formateada
                newName: newName
            }),
        });
        const data = await response.json(); // Procesar respuesta JSON
        // console.log('Respuesta de /api/rename_item:', data); // Para depuración

        if (data.success) {
            // console.log('Elemento renombrado exitosamente, mostrando alerta.'); // Para depuración
            // Ocultar el modal
            const modal = bootstrap.Modal.getInstance(document.getElementById('renameModal'));
            if (modal) modal.hide();
            // Recargar el contenido del directorio padre
            const parentPathParts = formattedOldPath.split('/');
            parentPathParts.pop(); // Eliminar el nombre del item
            const parentPath = parentPathParts.join('/'); // Obtener la ruta del directorio padre
            loadDirectoryContent(parentPath); // Recargar el directorio padre
            // Mostrar mensaje de éxito del backend
            showAlert('success', data.message);
        } else {
            // console.log('Fallo al renombrar elemento, mostrando alerta de error.'); // Para depuración
            // Mostrar mensaje de error del backend
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
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
         searchInput.addEventListener('input', function() {
            // Clear previous timeout and set a new one for delayed search
            clearTimeout(window.searchTimeout); // Referencing the global searchTimeout
            window.searchTimeout = setTimeout(searchFiles, 300); // Referencing the global searchTimeout
        });
    } else {
        console.warn("Search input with ID 'searchInput' not found.");
    }


    // Load the initial directory content (root 'data' directory)
    loadDirectoryContent(''); // Load root directory on startup

    // Add handler for the "Recargar" button
    addUpdateButtonHandler();


    // Configure modals to clear their forms and set path inputs when shown/hidden
    ['createDirModal', 'createFileModal', 'appendModal', 'deleteModal', 'renameModal', 'previewModal'].forEach(modalId => {
        const modalElement = document.getElementById(modalId);
        if (modalElement) {
            // Add listener for when the modal is about to be shown
            modalElement.addEventListener('show.bs.modal', function() {
                // Get the current path from the displayed element
                const currentPathDisplayElement = document.getElementById('currentPath');
                let currentPath = '';
                if (currentPathDisplayElement) {
                     currentPath = currentPathDisplayElement.textContent.replace('Estás en: ', '').trim();
                }
                // The path to show in the modal for creation should be relative to data/
                // If currentPath is 'data/', show '/' in the modal input. Otherwise, show the path relative to data/.
                const pathForModalInput = currentPath === 'data/' ? '/' : currentPath.replace('data/', '');

                // Set the parent path in the creation modals
                if (modalId === 'createDirModal') {
                    const createDirPathInput = document.getElementById('createDirPath');
                    if (createDirPathInput) createDirPathInput.value = pathForModalInput;
                    else console.warn("createDirPath input not found in modal.");
                } else if (modalId === 'createFileModal') {
                    const createFilePathInput = document.getElementById('createFilePath');
                    if (createFilePathInput) createFilePathInput.value = pathForModalInput;
                    else console.warn("createFilePath input not found in modal.");
                } else if (modalId === 'previewModal') {
                    // When the preview modal is shown, populate its content area
                    const previewModalFileContent = document.getElementById('previewModalFileContent');
                    const previewModalFileName = document.getElementById('previewModalFileName');
                    const previewModalFilePath = document.getElementById('previewModalFilePath');

                    if (previewModalFileContent && previewModalFileName && previewModalFilePath) {
                         // Use the globally stored content and selected item path
                         previewModalFileContent.innerHTML = currentPreviewContent !== null ? escapeHTML(currentPreviewContent) : 'Error al cargar contenido.';
                         previewModalFileName.textContent = selectedItemPath ? selectedItemPath.split('/').pop() : 'Archivo';
                         // Display the path relative to data/ in the preview modal
                         previewModalFilePath.textContent = selectedItemPath ? `data/${selectedItemPath}` : 'N/A';
                    } else {
                         console.error("Elementos del modal de previsualización no encontrados.");
                         if (previewModalFileContent) previewModalFileContent.textContent = 'Error interno al preparar la previsualización.';
                    }
                }
                 // Note: setModalPath handles setting paths for append, delete, rename modals when their respective buttons are clicked.
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
                 // Note: We are NOT clearing selection automatically when modals close anymore.
                 // Selection is cleared when navigating directories or clicking outside items (if clearSelection was active).
            });
        } else {
            console.warn(`Modal element with ID "${modalId}" not found.`);
        }
    });

    // --- Sidebar Action Button Event Listeners ---
    // These buttons are now only for Create Dir and Create File, and they open the modals.
    // Append, Delete, Rename are handled by buttons within the item list.

    // Create Directory button - always enabled, opens modal with current path
    const sidebarCreateDirBtn = document.getElementById('sidebarCreateDirBtn');
    if (sidebarCreateDirBtn) {
        sidebarCreateDirBtn.addEventListener('click', () => {
            const modalElement = document.getElementById('createDirModal');
            if (modalElement) {
                const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                modalInstance.show(); // show.bs.modal listener will set the path
            } else {
                 console.warn("Create Dir modal element not found.");
                 showAlert('danger', 'Error interno', 'No se encontró el modal para crear directorio.');
            }
        });
    } else { console.warn("Sidebar Create Directory button with ID 'sidebarCreateDirBtn' not found."); } // Corrected warning message

    // Create File button - always enabled, opens modal with current path
    const sidebarCreateFileBtn = document.getElementById('sidebarCreateFileBtn');
     if (sidebarCreateFileBtn) {
        sidebarCreateFileBtn.addEventListener('click', () => {
            const modalElement = document.getElementById('createFileModal');
            if (modalElement) {
                const modalInstance = bootstrap.Modal.getInstance(modalElement) || new bootstrap.Modal(modalElement);
                modalInstance.show(); // show.bs.modal listener will set the path
            } else {
                 console.warn("Create File modal element not found.");
                 showAlert('danger', 'Error interno', 'No se encontró el modal para crear archivo.');
            }
        });
     } else { console.warn("Sidebar Create File button with ID 'sidebarCreateFileBtn' not found."); } // Corrected warning message


    // --- Eliminados: Los listeners de los botones de acción (Append, Delete, Rename) del sidebar ya no existen aquí.
    // Su funcionalidad se maneja ahora con los botones dentro de cada item en la lista del navegador. ---
    // const sidebarAppendBtn = document.getElementById('sidebarAppendBtn'); ... console.warn("Sidebar Append button not found.");
    // const sidebarDeleteBtn = document.getElementById('sidebarDeleteBtn'); ... console.warn("Sidebar Delete button not found.");
    // const sidebarRenameBtn = document.getElementById('sidebarRenameBtn'); ... console.warn("Sidebar Rename button not found.");


     // Maximize Preview Button - requires a file to be previewed
    const maximizePreviewBtn = document.getElementById('maximizePreviewBtn');
    if (maximizePreviewBtn) {
        maximizePreviewBtn.addEventListener('click', () => {
            // Check if there is content to show (a file was successfully previewed)
            if (currentPreviewContent !== null) {
                 const previewModalElement = document.getElementById('previewModal');
                 if (previewModalElement) {
                     const modalInstance = bootstrap.Modal.getInstance(previewModalElement) || new bootstrap.Modal(previewModalElement);
                     modalInstance.show(); // show.bs.modal listener will populate the content
                 } else {
                     console.warn("Preview modal element not found.");
                     showAlert('danger', 'Error interno', 'No se encontró el modal de previsualización.');
                 }
            } else {
                 showAlert('info', 'No hay contenido para maximizar.', 'Selecciona un archivo primero.');
            }
        });
    } else { console.warn("Maximize Preview button with ID 'maximizePreviewBtn' not found."); } // Corrected warning message


    // --- Eliminada: updateSidebarButtonStates ya no se llama en la inicialización ---
    // updateSidebarButtonStates(); // Initialize sidebar button states (they start disabled)
});