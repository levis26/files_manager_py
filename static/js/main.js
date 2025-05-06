// Función para realizar búsqueda de archivos
async function searchFiles() {
    const query = document.getElementById('searchInput').value.trim();
    if (!query) {
        alert('Por favor ingrese un término de búsqueda');
        return;
    }

    try {
        const response = await fetch(`/api/search?query=${encodeURIComponent(query)}`);
        const data = await response.json();
        
        if (data.success) {
            const content = document.getElementById('browser-content');
            content.innerHTML = '';
            
            if (data.results.length === 0) {
                content.innerHTML = '<p class="text-muted">No se encontraron resultados</p>';
                return;
            }
            
            data.results.forEach(item => {
                const itemDiv = document.createElement('div');
                itemDiv.className = 'd-flex align-items-center mb-2';
                
                if (item.type === 'directory') {
                    itemDiv.innerHTML = `
                        <i class="bi bi-folder me-2"></i>
                        <a href="#" class="text-decoration-none" onclick="updateBrowserContent('${encodeURIComponent(item.path)}')">
                            ${item.name}
                        </a>
                    `;
                } else {
                    itemDiv.innerHTML = `
                        <i class="bi bi-file-earmark me-2"></i>
                        <a href="#" class="text-decoration-none" onclick="updateBrowserContent('${encodeURIComponent(item.path)}')">
                            ${item.name}
                        </a>
                    `;
                }
                content.appendChild(itemDiv);
            });
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al realizar la búsqueda');
    }
}

// Función para actualizar el contenido del explorador
async function updateBrowserContent(path = '') {
    try {
        const response = await fetch(`/api/browse?path=${encodeURIComponent(path)}`);
        const data = await response.json();
        
        if (data.success) {
            // Update the current path display
            document.getElementById('currentPath').textContent = data.current_path_display;
            
            const content = document.getElementById('browser-content');
            content.innerHTML = '';
            
            // Show folders
            data.items.filter(item => item.is_dir).forEach(item => {
                const folderDiv = document.createElement('div');
                folderDiv.className = 'd-flex align-items-center mb-2';
                folderDiv.innerHTML = `
                    <i class="bi bi-folder me-2"></i>
                    <a href="#" class="text-decoration-none" onclick="updateBrowserContent('${encodeURIComponent(item.path)}')">
                        ${item.name}
                    </a>
                `;
                content.appendChild(folderDiv);
            });
            
            // Show files
            data.items.filter(item => item.is_file).forEach(item => {
                const fileDiv = document.createElement('div');
                fileDiv.className = 'd-flex align-items-center mb-2';
                fileDiv.innerHTML = `
                    <i class="bi bi-file-earmark me-2"></i>
                    <a href="#" class="text-decoration-none" onclick="updateBrowserContent('${encodeURIComponent(item.path)}')">
                        ${item.name}
                    </a>
                `;
                content.appendChild(fileDiv);
            });
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al cargar el contenido del directorio');
    }
}

// Función para crear directorio
document.getElementById('createDirForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('createDirPath').value;
    const name = document.getElementById('createDirName').value;
    
    try {
        const response = await fetch('/api/create_directory', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path, name }),
        });
        const data = await response.json();
        
        if (data.success) {
            updateBrowserContent(path);
            document.getElementById('createDirModal').style.display = 'none';
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al crear el directorio');
    }
});

// Función para crear archivo
document.getElementById('createFileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('createFilePath').value;
    const name = document.getElementById('createFileName').value;
    const content = document.getElementById('createFileContent').value;
    
    try {
        const response = await fetch('/api/create_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path, name, content }),
        });
        const data = await response.json();
        
        if (data.success) {
            updateBrowserContent(path);
            document.getElementById('createFileModal').style.display = 'none';
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al crear el archivo');
    }
});

// Función para agregar contenido
document.getElementById('appendFileForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('appendFilePath').value;
    const content = document.getElementById('appendFileContent').value;
    
    try {
        const response = await fetch('/api/append_file', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path, content }),
        });
        const data = await response.json();
        
        if (data.success) {
            updateBrowserContent(path);
            document.getElementById('appendModal').style.display = 'none';
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al agregar contenido');
    }
});

// Función para eliminar item
document.getElementById('deleteItemForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('deleteItemPath').value;
    
    try {
        const response = await fetch('/api/delete_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path }),
        });
        const data = await response.json();
        
        if (data.success) {
            const parentPath = path.split('/').slice(0, -1).join('/');
            updateBrowserContent(parentPath);
            document.getElementById('deleteModal').style.display = 'none';
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al eliminar el item');
    }
});

// Función para renombrar item
document.getElementById('renameItemForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    const path = document.getElementById('renameItemPath').value;
    const newName = document.getElementById('renameItemName').value;
    
    try {
        const response = await fetch('/api/rename_item', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ path, newName }),
        });
        const data = await response.json();
        
        if (data.success) {
            const parentPath = path.split('/').slice(0, -1).join('/');
            updateBrowserContent(parentPath);
            document.getElementById('renameModal').style.display = 'none';
        } else {
            alert(data.message);
        }
    } catch (error) {
        console.error('Error:', error);
        alert('Error al renombrar el item');
    }
});

// Inicializar el explorador cuando se carga la página
document.addEventListener('DOMContentLoaded', () => {
    updateBrowserContent();
});