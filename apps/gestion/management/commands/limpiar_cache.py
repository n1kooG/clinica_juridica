from django.core.management.base import BaseCommand
from django.core.cache import cache


class Command(BaseCommand):
    help = 'Limpia todo el caché del sistema'

    def handle(self, *args, **kwargs):
        cache.clear()
        self.stdout.write(
            self.style.SUCCESS('Caché limpiado exitosamente')
        )