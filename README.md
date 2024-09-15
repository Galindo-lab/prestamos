### Requisitos
* Python 3.x
* pip
* docker

### Instalación
Accede al panel de administración en `http://localhost:8000/admin/`.

```
# 1. Clona el repositorio
git clone https://github.com/usuario/proyecto-django.git
cd proyecto-django

# 2. Crea y activa un entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 3. Instala dependencias
pip install -r requirements.txt

# 4. Aplica migraciones
python manage.py migrate

# 5. Crea un superusuario
python manage.py createsuperuser

# 6. Inicia el servidor
python manage.py runserver
    
```

