#!/bin/bash

# Esperar a que la base de datos esté lista
echo "Esperando a que la base de datos esté disponible..."

# Intentar conectarse al host 'db' en el puerto 3306 hasta que tenga éxito
until nc -z -v -w30 db 3306
do
  echo "Esperando a que la base de datos esté disponible..."
  sleep 5
done

echo "La base de datos está lista. Ejecutando migraciones y colectando archivos estáticos."

# Ejecutar migraciones y colectar archivos estáticos
python manage.py collectstatic --noinput
python manage.py migrate

# Iniciar Apache en primer plano
exec "$@"
