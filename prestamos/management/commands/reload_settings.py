# my_app/management/commands/reload_settings.py

from django.core.management.base import BaseCommand
from django.core.cache import cache
from extra_settings.models import Setting  # Import the Setting model
from django.conf import settings

class Command(BaseCommand):
    help = 'Reloads all configurations, including django-extra-settings.'

    def handle(self, *args, **options):
        self.stdout.write('Starting the configuration reload process...')

        # 1. Clear specific cache keys related to django-extra-settings
        # Note: Ensure these are the actual cache keys used by django-extra-settings
        cache_keys = [
            'extra_settings_global_settings',
            'extra_settings_site_settings',
        ]
        for key in cache_keys:
            cache.delete(key)
            self.stdout.write(f'Cache key deleted: {key}')

        # 2. Optional: Clear the entire cache
        # Uncomment the following lines if you prefer to clear the entire cache
        # Be cautious as this will affect all cached data
        # cache.clear()
        # self.stdout.write('Entire cache cleared.')

        # 3. Force reload the configurations by accessing settings
        try:
            # Iterate through all settings to ensure they're loaded
            all_settings = Setting.objects.all()
            for setting in all_settings:
                value = setting.value  # Access the value to ensure it's loaded
            self.stdout.write('Configurations reloaded successfully.')
        except Exception as e:
            self.stderr.write(f'Error reloading configurations: {e}')
            return

        self.stdout.write(self.style.SUCCESS('Configuration reload process completed successfully.'))
