// Función para mostrar alertas
function showAlert(type, message) {
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert alert-${type} alert-dismissible fade show`;
    alertDiv.role = 'alert';
    alertDiv.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
    `;
    
    // Insertar al principio del contenedor
    const container = document.querySelector('.container');
    if (container.firstChild) {
        container.insertBefore(alertDiv, container.firstChild);
    } else {
        container.appendChild(alertDiv);
    }
    
    // Auto-ocultar después de 5 segundos
    setTimeout(() => {
        const bsAlert = new bootstrap.Alert(alertDiv);
        bsAlert.close();
    }, 5000);
}

// Función para cargar el contenido de un directorio
async function loadDirectoryContent(path = '') {
    try {
        const response = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        if (data.success) {
            // Actualizar la ruta actual mostrada
            document.getElementById('currentPath').textContent = data.current_path_display || 'data';
            
            const browserContent = document.getElementById('browser-content');
            browserContent.innerHTML = '';
            
            // Mostrar botón para subir un nivel si no estamos en la raíz
            if (path) {
                const parentPath = path.split('/').slice(0, -1).join('/');
                const upDiv = document.createElement('div');
                upDiv.className = 'd-flex align-items-center mb-2';
                upDiv.innerHTML = `
                    <i class="bi bi-arrow-up-circle-fill me-2"></i>
                    <a href="#" class="text-decoration-none" onclick="loadDirectoryContent('${parentPath}')">
                        Subir nivel
                    </a>
                `;
                browserContent.appendChild(upDiv);
            }
            
            // Mostrar directorios primero
            data.items.filter(item => item.is_dir).forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'd-flex justify-content-between align-items-center mb-2 p-2 border-bottom';
                itemDiv.innerHTML = `
                    <div>
                        <i class="bi bi-folder-fill text-warning me-2"></i>
                        <a href="#" class="text-decoration-none" onclick="loadDirectoryContent('${item.path}')">
                            ${item.name}
                        </a>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-secondary" onclick="setModalPath('renameModal', '${item.path}', '${item.name}')">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="setModalPath('deleteModal', '${item.path}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                browserContent.appendChild(itemDiv);
            });
            
            // Mostrar archivos después
            data.items.filter(item => item.is_file).forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'd-flex justify-content-between align-items-center mb-2 p-2 border-bottom';
                itemDiv.innerHTML = `
                    <div>
                        <i class="bi bi-file-earmark-fill text-primary me-2"></i>
                        <a href="#" class="text-decoration-none" onclick="previewFile('${item.path}')">
                            ${item.name}
                        </a>
                    </div>
                    <div class="btn-group">
                        <button class="btn btn-sm btn-outline-secondary" onclick="setModalPath('appendModal', '${item.path}')">
                            <i class="bi bi-plus-circle"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-secondary" onclick="setModalPath('renameModal', '${item.path}', '${item.name}')">
                            <i class="bi bi-pencil"></i>
                        </button>
                        <button class="btn btn-sm btn-outline-danger" onclick="setModalPath('deleteModal', '${item.path}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                `;
                browserContent.appendChild(itemDiv);
            });
        } else {
            showAlert('danger', data.message || 'Error al cargar el directorio');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al cargar el contenido del directorio');
    }
}

// Función para previsualizar un archivo
async function previewFile(path) {
    try {
        const response = await fetch(`/api/preview?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        if (data.success) {
            const modal = new bootstrap.Modal(document.getElementById('previewModal'));
            document.getElementById('previewFileName').textContent = path.split('/').pop();
            document.getElementById('previewFileContent').textContent = data.content;
            modal.show();
        } else {
            showAlert('danger', data.message || 'Error al previsualizar el archivo');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al previsualizar el archivo');
    }
}

// Función para establecer la ruta en los modales
function setModalPath(modalId, path, currentName = '') {
    const modalElement = document.getElementById(modalId);
    const modal = new bootstrap.Modal(modalElement);
    
    // Establecer la ruta en el modal correspondiente
    if (modalId === 'renameModal') {
        document.getElementById('renameItemPath').value = path;
        document.getElementById('renameItemName').value = currentName;
    } else if (modalId === 'deleteModal') {
        document.getElementById('deleteItemPath').value = path;
    } else if (modalId === 'appendModal') {
        document.getElementById('appendFilePath').value = path;
    } else if (modalId === 'createDirModal' || modalId === 'createFileModal') {
        document.getElementById(`${modalId === 'createDirModal' ? 'createDirPath' : 'createFilePath'}`).value = path;
    }
    
    modal.show();
}

// Función para buscar archivos
let searchTimeout;

async function searchFiles() {
    const searchTerm = document.getElementById('searchInput').value.trim();
    const currentPath = document.getElementById('currentPath').textContent.replace('data/', '');
    
    // Limpiar el timeout anterior si existe
    if (searchTimeout) {
        clearTimeout(searchTimeout);
    }
    
    // Si el término de búsqueda está vacío, volver a mostrar el contenido normal
    if (searchTerm.length === 0) {
        loadDirectoryContent(currentPath);
        return;
    }

    // Asegurar que la ruta está correctamente formateada
    const formattedPath = currentPath ? currentPath.replace(/^\/|\/$/g, '') : '';
    
    // Mostrar indicador de carga
    const browserContent = document.getElementById('browser-content');
    browserContent.innerHTML = '<div class="text-center py-4"><div class="spinner-border text-primary" role="status"><span class="visually-hidden">Buscando...</span></div></div>';

    // Agregar un delay de 300ms para evitar búsquedas innecesarias
    searchTimeout = setTimeout(async () => {
        try {
            const response = await fetch(`/api/search?term=${encodeURIComponent(searchTerm)}&path=${encodeURIComponent(formattedPath)}`);
            const data = await response.json();
            
            if (data.success) {
                displaySearchResults(data.results, searchTerm);
            } else {
                showAlert('danger', data.message || 'Error en la búsqueda');
                loadDirectoryContent(formattedPath);
            }
        } catch (error) {
            console.error('Error:', error);
            showAlert('danger', 'Error al realizar la búsqueda');
            loadDirectoryContent(formattedPath);
        }
    }, 300);
}

// Función para mostrar los resultados de búsqueda
function displaySearchResults(results, searchTerm) {
    const browserContent = document.getElementById('browser-content');
    
    if (results.length === 0) {
        browserContent.innerHTML = `
            <div class="text-center py-4">
                <i class="bi bi-search" style="font-size: 2rem;"></i>
                <h5 class="mt-3">No se encontraron resultados para "${searchTerm}"</h5>
                <button class="btn btn-primary mt-3" onclick="loadDirectoryContent()">
                    <i class="bi bi-arrow-left"></i> Volver al explorador
                </button>
            </div>
        `;
        return;
    }

    let html = `
        <div class="d-flex justify-content-between align-items-center mb-3">
            <div>
                <h5><i class="bi bi-search me-2"></i>Resultados para "${searchTerm}"</h5>
                <p class="text-muted">${results.length} elementos encontrados</p>
            </div>
            <button class="btn btn-outline-secondary" onclick="loadDirectoryContent()">
                <i class="bi bi-arrow-left"></i> Volver
            </button>
        </div>
        <ul class="list-group">
    `;

    results.forEach(item => {
        const icon = item.is_dir ? 'bi-folder-fill text-warning' : 'bi-file-earmark-fill text-primary';
        
        html += `
            <li class="list-group-item d-flex justify-content-between align-items-center">
                <div>
                    <i class="bi ${icon} me-2"></i>
                    <span class="item-name">${highlightMatches(item.name, searchTerm)}</span>
                    <small class="text-muted ms-2">${item.path}</small>
                </div>
                <div class="btn-group">
                    ${item.is_dir ? 
                        `<button class="btn btn-sm btn-outline-secondary" onclick="loadDirectoryContent('${item.path}')">
                            <i class="bi bi-folder2-open"></i> Abrir
                        </button>` : 
                        `<button class="btn btn-sm btn-outline-primary" onclick="previewFile('${item.path}')">
                            <i class="bi bi-eye"></i> Ver
                        </button>`
                    }
                    <button class="btn btn-sm btn-outline-secondary" onclick="setModalPath('renameModal', '${item.path}', '${item.name}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="setModalPath('deleteModal', '${item.path}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </li>
        `;
    });

    html += `</ul>`;
    browserContent.innerHTML = html;
}

// Función para resaltar coincidencias en los resultados
function highlightMatches(text, searchTerm) {
    if (!searchTerm) return text;
    
    const regex = new RegExp(`(${escapeRegExp(searchTerm)})`, 'gi');
    return text.replace(regex, '<span class="bg-warning">$1</span>');
}

// Función para escapar caracteres especiales en regex
function escapeRegExp(string) {
    return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
}

// Manejadores de eventos para los formularios
document.getElementById('createDirForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('createDirPath').value || '';
    const formattedPath = path ? path.replace(/^\/|\/$/g, '') : '';
    const name = document.getElementById('createDirName').value;
    
    try {
        const response = await fetch('/api/create_directory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, name }),
        });
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('createDirModal'));
            modal.hide();
            loadDirectoryContent(formattedPath);
            showAlert('success', 'Directorio creado correctamente');
        } else {
            showAlert('danger', data.message || 'Error al crear el directorio');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al crear el directorio');
    }
});

document.getElementById('createFileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('createFilePath').value || '';
    const formattedPath = path ? path.replace(/^\/|\/$/g, '') : '';
    const name = document.getElementById('createFileName').value;
    const content = document.getElementById('createFileContent').value;
    
    try {
        const response = await fetch('/api/create_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, name, content }),
        });
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('createFileModal'));
            modal.hide();
            loadDirectoryContent(formattedPath);
            showAlert('success', 'Archivo creado correctamente');
        } else {
            showAlert('danger', data.message || 'Error al crear el archivo');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al crear el archivo');
    }
});

document.getElementById('appendFileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('appendFilePath').value || '';
    const formattedPath = path ? path.replace(/^\/|\/$/g, '') : '';
    const content = document.getElementById('appendFileContent').value;
    
    try {
        const response = await fetch('/api/append_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath, content }),
        });
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('appendModal'));
            modal.hide();
            loadDirectoryContent(formattedPath.split('/').slice(0, -1).join('/'));
            showAlert('success', 'Contenido agregado correctamente');
        } else {
            showAlert('danger', data.message || 'Error al agregar contenido');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al agregar contenido');
    }
});

document.getElementById('deleteItemForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('deleteItemPath').value || '';
    const formattedPath = path ? path.replace(/^\/|\/$/g, '') : '';
    const itemName = path.split('/').pop();
    
    try {
        const response = await fetch('/api/delete_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path: formattedPath }),
        });
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('deleteModal'));
            modal.hide();
            const parentPath = formattedPath.split('/').slice(0, -1).join('/');
            loadDirectoryContent(parentPath);
            showAlert('success', `"${itemName}" eliminado correctamente`);
        } else {
            showAlert('danger', data.message || 'Error al eliminar el item');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al eliminar el item');
    }
});

document.getElementById('renameItemForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const oldPath = document.getElementById('renameItemPath').value || '';
    const formattedOldPath = oldPath ? oldPath.replace(/^\/|\/$/g, '') : '';
    const newName = document.getElementById('renameItemName').value;
    const oldName = oldPath.split('/').pop();
    
    try {
        const response = await fetch('/api/rename_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ oldPath: formattedOldPath, newName }),
        });
        const data = await response.json();
        
        if (data.success) {
            const modal = bootstrap.Modal.getInstance(document.getElementById('renameModal'));
            modal.hide();
            const parentPath = formattedOldPath.split('/').slice(0, -1).join('/');
            loadDirectoryContent(parentPath);
            showAlert('success', `"${oldName}" renombrado a "${newName}" correctamente`);
        } else {
            showAlert('danger', data.message || 'Error al renombrar el item');
        }
    } catch (error) {
        console.error('Error:', error);
        showAlert('danger', 'Error al renombrar el item');
    }
});

// Inicializar el explorador cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    // Configurar el buscador
    document.getElementById('searchInput').addEventListener('input', function() {
        clearTimeout(window.searchTimeout);
        window.searchTimeout = setTimeout(searchFiles, 300);
    });
    
    // Cargar el directorio raíz
    loadDirectoryContent();
    
    // Configurar los modales para que limpien los formularios al cerrarse
    ['createDirModal', 'createFileModal', 'appendModal', 'deleteModal', 'renameModal'].forEach(modalId => {
        document.getElementById(modalId).addEventListener('hidden.bs.modal', function() {
            const form = this.querySelector('form');
            if (form) {
                form.reset();
            }
        });
    });
});