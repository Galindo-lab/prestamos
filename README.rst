**Requisitos**
--------------
Para ejecutar el proyecto sin Docker, necesitarás tener instalados los siguientes programas:

- Python 3.x
- pip
- Docker

**Ejecución sin Docker**
------------------------
Sigue estos pasos para ejecutar el proyecto sin usar Docker:

1. **Crear y activar un entorno virtual**:

   .. code-block:: bash

      python -m venv venv
      source venv/bin/activate  # En Windows: venv\Scripts\activate

2. **Instalar dependencias**:

   .. code-block:: bash

      pip install -r requirements.txt

3. **Aplicar migraciones**:

   .. code-block:: bash

      python manage.py migrate --settings=almacen.settings.sqlite

4. **Crear un superusuario**:

   .. code-block:: bash

      python manage.py createsuperuser --settings=almacen.settings.sqlite

5. **Iniciar el servidor**:

   .. code-block:: bash

      python manage.py runserver --settings=almacen.settings.sqlite

   El servidor estará disponible en `http://localhost:8000/`.

**Ejecución con Docker**
------------------------
Si prefieres usar Docker, sigue estos pasos:

1. **Iniciar Docker**:

   .. code-block:: bash

      sudo docker compose up --build

2. **Revisar la aplicación en el navegador**:

   Visita `http://localhost:8000/` en tu navegador para interactuar con la aplicación.
