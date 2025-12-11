from django.core.management.base import BaseCommand
from apps.gestion.cache_utils import (
    get_tribunales_activos,
    get_materias_activas,
    get_estados_activos,
    get_tipos_documento_activos,
    get_responsables_activos,
)


class Command(BaseCommand):
    help = 'Pre-carga todos los catálogos en caché'

    def handle(self, *args, **kwargs):
        self.stdout.write('Calentando caché...')
        
        tribunales = get_tribunales_activos()
        self.stdout.write(f'  ✓ Tribunales: {len(tribunales)}')
        
        materias = get_materias_activas()
        self.stdout.write(f'  ✓ Materias: {len(materias)}')
        
        estados = get_estados_activos()
        self.stdout.write(f'  ✓ Estados: {len(estados)}')
        
        tipos = get_tipos_documento_activos()
        self.stdout.write(f'  ✓ Tipos documento: {len(tipos)}')
        
        responsables = get_responsables_activos()
        self.stdout.write(f'  ✓ Responsables: {len(responsables)}')
        
        self.stdout.write(
            self.style.SUCCESS('\nCaché calentado exitosamente')
        )