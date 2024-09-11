import os
import requests
from django.core.management.base import BaseCommand
from django.conf import settings

class Command(BaseCommand):
    help = 'Descarga las portadas de los libros por categoría y las guarda en un directorio'

    def add_arguments(self, parser):
        parser.add_argument('category', type=str, help='La categoría de los libros para buscar en Google Books')
        parser.add_argument('--limit', type=int, default=10, help='Número de libros cuyas portadas se descargarán')

    def handle(self, *args, **kwargs):
        category_name = kwargs['category']
        limit = kwargs['limit']

        # URL base de la API de Google Books
        api_url = f"https://www.googleapis.com/books/v1/volumes?q=subject:{category_name}&maxResults={limit}"

        # Realizamos la solicitud a la API
        response = requests.get(api_url)

        if response.status_code != 200:
            self.stdout.write(self.style.ERROR(f'Error en la solicitud a la API. Código de estado: {response.status_code}'))
            return

        books = response.json().get('items', [])

        if not books:
            self.stdout.write(self.style.WARNING(f'No se encontraron libros para la categoría "{category_name}".'))
            return

        # Creamos el directorio para almacenar las portadas si no existe
        folder_path = os.path.join(settings.MEDIA_ROOT, 'book_covers')
        os.makedirs(folder_path, exist_ok=True)

        for book in books:
            title = book.get('volumeInfo', {}).get('title', 'Título Desconocido')
            image_links = book.get('volumeInfo', {}).get('imageLinks', {})

            # Obtener la URL de la portada (preferimos 'thumbnail', si no existe, usamos 'smallThumbnail')
            cover_url = image_links.get('thumbnail') or image_links.get('smallThumbnail')

            if cover_url and isinstance(cover_url, str):  # Nos aseguramos de que la URL sea una cadena válida
                image_path = self.download_image(cover_url, title)
                if image_path:
                    self.stdout.write(self.style.SUCCESS(f'Portada descargada para el libro: {title}'))
            else:
                self.stdout.write(self.style.WARNING(f'No se encontró portada para el libro: {title}'))

    def download_image(self, url, title):
        """
        Descarga una imagen desde la URL y la guarda en el sistema de archivos.
        :param url: URL de la imagen
        :param title: Título del libro (se usa para nombrar el archivo)
        :return: Ruta del archivo de la imagen descargada o None si falla
        """
        try:
            # Crear el nombre del archivo basado en el título del libro
            filename = f"{title.replace(' ', '_')}.jpg"
            path = os.path.join(settings.MEDIA_ROOT, 'book_covers', filename)

            # Descargar la imagen
            response = requests.get(url, stream=True)
            if response.status_code == 200:
                # Guardamos la imagen en el sistema de archivos
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
