# Aplicación de Gestión de Archivos y Directorios

Esta es una sencilla aplicación web construida con Python y Flask para gestionar archivos y directorios dentro de una carpeta designada llamada `data`. Proporciona una interfaz gráfica básica accesible a través de un navegador web para realizar operaciones comunes del sistema de archivos.

## Características

La aplicación soporta las siguientes operaciones dentro del directorio `data`:

* **Ver Contenido:** explora el contenido del directorio `data` y sus subdirectorios.

* **Crear Directorio:** crea nuevos directorios en una ruta especificada dentro de `data`.

* **Crear Archivo:** crea nuevos archivos en una ruta especificada dentro de `data` con contenido inicial.

* **Añadir a Archivo:** Agrega nuevo contenido al final de un archivo existente dentro de `data`.

* **Eliminar Archivo:** Elimina un archivo específico dentro de `data`.

* **Eliminar Directorio:** Elimina recursivamente un directorio y todo su contenido dentro de `data`.

## Estructura del Proyecto

El proyecto sigue una estructura sencilla:

```
/project_root
├── app.py              # El archivo principal de la aplicación Flask
├── data/               # Directorio para el almacenamiento de archivos y directorios
└── templates/          # Directorio para las plantillas HTML
    ├── index.html      # Página del menú principal
    ├── create_dir.html # Formulario para crear directorios
    ├── create_file.html # Formulario para crear archivos
    ├── append_file.html # Formulario para añadir a archivos
    ├── delete_item.html # Formulario para eliminar archivos/directorios
    └── view_data.html  # Página para ver el contenido del directorio data


```

El directorio `data/` se crea automáticamente cuando la aplicación se ejecuta si no existe.

## Configuración

Para ejecutar este proyecto, necesitas tener Python instalado en tu sistema. Es altamente recomendable usar un entorno virtual para gestionar las dependencias.

1. **Clona o descarga los archivos del proyecto:**
   Guarda el archivo `app.py` y crea el directorio `templates` con los archivos HTML dentro. Asegúrate de que el directorio `data` esté creado al mismo nivel que `app.py`.

2. **Navega al directorio del proyecto:**
   Abre tu terminal o línea de comandos y cambia tu directorio actual a la raíz del proyecto (`project_root`).

   ```
   cd /ruta/a/tu/project_root
   
   
   
   ```

3. **Crea un entorno virtual:**

   ```
   python3 -m venv .venv
   
   
   
   ```

   Esto crea un entorno virtual llamado `.venv` en el directorio de tu proyecto.

4. **Activa el entorno virtual:**

   * En Linux/macOS:

     ```
     source .venv/bin/activate
     
     
     
     ```

   * En Windows:

     ```
     .venv\Scripts\activate
     
     
     
     ```

   Deberías ver `(.venv)` al principio de tu prompt de terminal, indicando que el entorno virtual está activo.

5. **Instala las dependencias:**
   Con el entorno virtual activo, instala Flask:

   ```
   pip install Flask
   
   
   
   ```

## Cómo Ejecutar

1. **Activa tu entorno virtual** (si no está ya activo):

   ```
   source .venv/bin/activate # Linux/macOS
   # O
   .venv\Scripts\activate # Windows
   
   
   
   ```

2. **Ejecuta la aplicación Flask:**

   ```
   python app.py
   
   
   
   ```

3. **Accede a la aplicación:**
   Abre tu navegador web y ve a `http://127.0.0.1:5000/`.

La terminal que ejecuta `app.py` mostrará los registros del servidor. Presiona `CTRL+C` en la terminal para detener el servidor.

## Uso

Una vez que la aplicación esté en funcionamiento y accedas a `http://127.0.0.1:5000/` en tu navegador, verás el menú principal.

* Haz clic en los enlaces para navegar a los diferentes formularios para crear, añadir o eliminar elementos.

* Utiliza el enlace "View Data Directory Contents" para explorar la carpeta `data` y ver los resultados de tus operaciones.

* Cuando se te pida una ruta, proporciona la ruta *relativa* al directorio `data/` (por ejemplo, `mi_carpeta/mi_archivo.txt` o `nuevo_directorio`). No uses barras iniciales (`/`) ni `..` al principio de las rutas.
