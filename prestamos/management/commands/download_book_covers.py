import os
import requests
from django.core.management.base import BaseCommand
from prestamos.models import Item, Category
from django.core.files import File
from urllib.parse import urlparse
from django.conf import settings


class Command(BaseCommand):
    help = 'Descarga libros desde la API de Google Books y los guarda en el modelo Item'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str, help='La categoría de los libros')
        parser.add_argument('--limit', type=int, default=10, help='Número de libros a descargar')

    def handle(self, *args, **kwargs):
        category_name = kwargs['category']
        limit = kwargs['limit']

        # URL base de la API de Google Books
        api_url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{category_name}&maxResults={limit}"

        # Realizamos la petición a la API
        response = requests.get(api_url)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Error en la solicitud a la API. Status Code: {response.status_code}'))
            return

        books = response.json().get('items', [])

        if not books:
            self.stdout.write(self.style.WARNING(f'No se encontraron libros para la categoría "{category_name}".'))
            return

        # Intentamos obtener o crear la categoría en el modelo Category
        category_obj, created = Category.objects.get_or_create(name=category_name)
        if created:
            self.stdout.write(self.style.SUCCESS(f'Se creó la categoría "{category_name}".'))

        for book in books:
            title = book.get('volumeInfo', {}).get('title', 'Título Desconocido')
            description = book.get('volumeInfo', {}).get('description', 'Sin descripción disponible.')
            categories = book.get('volumeInfo', {}).get('categories', [])
            image_links = book.get('volumeInfo', {}).get('imageLinks', {})

            # Obtener una única URL de portada (thumbnail o smallThumbnail)
            cover_url = image_links.get('thumbnail') or image_links.get(
                'smallThumbnail')  # Asegurarse de que sea una cadena

            # Creación del objeto Item en la base de datos
            item_obj, created = Item.objects.get_or_create(
                name=title,
                defaults={'description': description}
            )

            if created:
                # Asignamos las categorías
                item_obj.category.add(category_obj)
                for cat_name in categories:
                    cat_obj, _ = Category.objects.get_or_create(name=cat_name)
                    item_obj.category.add(cat_obj)

                # Guardamos la imagen si existe una URL válida
                if cover_url and isinstance(cover_url, str):  # Verificar que cover_url sea una cadena válida
                    image_path = self.download_image(cover_url, title)
                    if image_path:
                        item_obj.image.save(os.path.basename(image_path), File(open(image_path, 'rb')))
                        self.stdout.write(self.style.SUCCESS(f'Portada guardada para el libro: {title}'))

                item_obj.save()
                self.stdout.write(self.style.SUCCESS(f'Se creó el libro: {title}'))
            else:
                self.stdout.write(self.style.WARNING(f'El libro "{title}" ya existe en la base de datos.'))

    def download_image(self, url, title):
        """
        Descarga una imagen desde la URL y la guarda en el sistema de archivos.
        :param url: URL de la imagen
        :param title: Título del libro (se usa para nombrar el archivo)
        :return: Ruta del archivo de la imagen descargada o None si falla
        """
        try:
            # Obtener el nombre del archivo desde la URL
            filename = f"{title.replace(' ', '_')}.jpg"
            path = os.path.join(settings.MEDIA_ROOT, 'book_covers', filename)

            # Crear el directorio si no existe
            os.makedirs(os.path.dirname(path), exist_ok=True)

            # Descargar la imagen
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                with open(path, 'wb') as img_file:
                    for chunk in response.iter_content(1024):
                        img_file.write(chunk)
                return path
            else:
                self.stdout.write(self.style.WARNING(f"No se pudo descargar la imagen para el libro: {title}"))
                return None
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error al descargar la imagen: {str(e)}'))
            return None
