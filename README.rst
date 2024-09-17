Proyecto de Almacén
===================

Este proyecto permite gestionar un sistema de almacén. A continuación, se detallan las instrucciones para ejecutar el proyecto tanto con como sin Docker.

Requisitos
----------

Para ejecutar el proyecto sin Docker, necesitarás tener instalados los siguientes programas:

- Python 3.x
- pip
- Docker

Ejecución sin Docker
--------------------

Sigue estos pasos para ejecutar el proyecto sin usar Docker:

1. Crear y activar un entorno virtual::

   python -m venv venv
   source venv/bin/activate  # En Windows: venv\Scripts\activate

2. Instalar dependencias::

   pip install -r requirements.txt

3. Aplicar migraciones::

   python manage.py migrate --settings=almacen.settings.sqlite

4. Crear un superusuario::

   python manage.py createsuperuser --settings=almacen.settings.sqlite

5. Iniciar el servidor::

   python manage.py runserver --settings=almacen.settings.sqlite

   El servidor estará disponible en `http://localhost:8000/`.

Ejecución con Docker
--------------------

Si prefieres usar Docker, sigue estos pasos:

1. Iniciar Docker::

   sudo docker compose up --build

2. Revisar la aplicación en el navegador:

   Visita `http://localhost:8000/` en tu navegador para interactuar con la aplicación.
