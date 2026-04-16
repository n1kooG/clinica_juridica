"""
Tests — app gestion
Cobertura: validadores, permisos, IDOR consentimientos.
"""
from datetime import date

from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.urls import reverse

from apps.cuentas.models import Perfil
from .models import (
    Causa, CausaPersona, Consentimiento, EstadoCausa,
    Materia, Persona, Tribunal,
)
from .permissions import (
    obtener_rol_usuario,
    puede_editar_causa,
    tiene_permiso,
)
from .validators import (
    calcular_digito_verificador,
    validar_rut_chileno,
)
from .views import _puede_acceder_consentimiento


# =============================================================================
# Helpers
# =============================================================================

def crear_usuario(username, rol='ESTUDIANTE', password='Pass1234!'):
    user = User.objects.create_user(username=username, password=password)
    user.perfil.rol = rol
    user.perfil.save()
    return user


def rut_valido(numero_str):
    """Construye un RUT válido a partir del número (sin DV)."""
    dv = calcular_digito_verificador(numero_str)
    return f'{numero_str}-{dv}'


def rut_valido_con_k():
    """Retorna un número de RUT cuyo DV es K."""
    for n in range(1000000, 10000000):
        if calcular_digito_verificador(str(n)) == 'K':
            return str(n)
    raise RuntimeError('No se encontró RUT con DV=K')


# =============================================================================
# VALIDADORES — RUT chileno
# =============================================================================

class CalcularDigitoVerificadorTest(TestCase):

    def test_resultado_rut_conocido(self):
        """11111111 → DV=1 (suma=32, 32%11=10, 11-10=1)."""
        self.assertEqual(calcular_digito_verificador('11111111'), '1')

    def test_dv_k_encontrado_en_rango(self):
        """Debe existir al menos un RUT con DV=K en el primer millón."""
        numero = rut_valido_con_k()
        self.assertEqual(calcular_digito_verificador(numero), 'K')

    def test_entrada_no_numerica_retorna_none(self):
        self.assertIsNone(calcular_digito_verificador('abc'))


class ValidarRutChilenoTest(TestCase):

    def setUp(self):
        # Construir RUTs válidos en tiempo de ejecución para evitar hardcodear DV
        self.rut_numero = '11111111'
        self.dv = calcular_digito_verificador(self.rut_numero)      # '1'
        self.rut_sin_formato = f'{self.rut_numero}{self.dv}'        # '111111111'
        self.rut_con_guion = f'{self.rut_numero}-{self.dv}'         # '11111111-1'

        # RUT con DV=K
        self.rut_k_numero = rut_valido_con_k()

    def test_rut_valido_con_guion(self):
        validar_rut_chileno(self.rut_con_guion)

    def test_rut_valido_sin_formato(self):
        validar_rut_chileno(self.rut_sin_formato)

    def test_rut_vacio_es_valido(self):
        """Campo vacío pasa (required se maneja en el form)."""
        validar_rut_chileno('')

    def test_rut_dv_incorrecto_lanza_rut_dv_invalido(self):
        dv_malo = '0' if self.dv != '0' else '1'
        with self.assertRaises(ValidationError) as ctx:
            validar_rut_chileno(f'{self.rut_numero}-{dv_malo}')
        self.assertEqual(ctx.exception.code, 'rut_dv_invalido')

    def test_rut_fuera_de_rango_lanza_error(self):
        with self.assertRaises(ValidationError) as ctx:
            validar_rut_chileno('999-9')
        self.assertEqual(ctx.exception.code, 'rut_fuera_de_rango')

    def test_rut_con_k_mayuscula(self):
        validar_rut_chileno(f'{self.rut_k_numero}-K')

    def test_rut_con_k_minuscula(self):
        """limpiar_rut convierte a mayúsculas, k minúscula debe pasar."""
        validar_rut_chileno(f'{self.rut_k_numero}-k')

    def test_rut_con_puntos_y_guion(self):
        """Formato con puntos: 11.111.111-1"""
        numero = self.rut_numero
        formateado = f'{numero[:2]}.{numero[2:5]}.{numero[5:]}-{self.dv}'
        validar_rut_chileno(formateado)


# =============================================================================
# PERMISOS
# =============================================================================

class ObtenerRolUsuarioTest(TestCase):

    def test_rol_por_perfil(self):
        for rol in ['ADMIN', 'SUPERVISOR', 'ESTUDIANTE', 'SECRETARIA']:
            with self.subTest(rol=rol):
                user = crear_usuario(f'user_{rol}', rol=rol)
                self.assertEqual(obtener_rol_usuario(user), rol)

    def test_usuario_sin_perfil_retorna_none(self):
        user = User.objects.create_user('norol', password='pass')
        Perfil.objects.filter(user=user).delete()
        # Instancia fresca para que el ORM no use el perfil cacheado
        user = User.objects.get(pk=user.pk)
        self.assertIsNone(obtener_rol_usuario(user))

    def test_usuario_no_autenticado_retorna_none(self):
        from django.contrib.auth.models import AnonymousUser
        self.assertIsNone(obtener_rol_usuario(AnonymousUser()))


class TienePermisoTest(TestCase):

    def test_admin_tiene_permisos_clave(self):
        admin = crear_usuario('admin1', rol='ADMIN')
        for permiso in ['puede_crear_causa', 'puede_editar_persona', 'puede_ver_auditoria']:
            with self.subTest(permiso=permiso):
                self.assertTrue(tiene_permiso(admin, permiso))

    def test_estudiante_no_puede_ver_auditoria(self):
        est = crear_usuario('est1', rol='ESTUDIANTE')
        self.assertFalse(tiene_permiso(est, 'puede_ver_auditoria'))

    def test_estudiante_puede_subir_documento(self):
        est = crear_usuario('est2', rol='ESTUDIANTE')
        self.assertTrue(tiene_permiso(est, 'puede_subir_documento'))

    def test_permiso_inexistente_retorna_false(self):
        admin = crear_usuario('admin2', rol='ADMIN')
        self.assertFalse(tiene_permiso(admin, 'permiso_que_no_existe'))


class PuedeEditarCausaTest(TestCase):

    def setUp(self):
        self.estado = EstadoCausa.objects.create(nombre='En curso', color='#00f', orden=1)
        self.tribunal = Tribunal.objects.create(nombre='Juzgado Civil', activo=True)
        self.materia = Materia.objects.create(nombre='Civil', activo=True)

    def _causa(self, responsable):
        return Causa.objects.create(
            rit='C-001-2026',
            materia=self.materia,
            tribunal=self.tribunal,
            estado=self.estado,
            responsable=responsable,
        )

    def test_admin_puede_editar(self):
        admin = crear_usuario('adm_e', rol='ADMIN')
        self.assertTrue(puede_editar_causa(admin, self._causa(admin)))

    def test_supervisor_puede_editar(self):
        sup = crear_usuario('sup_e', rol='SUPERVISOR')
        self.assertTrue(puede_editar_causa(sup, self._causa(sup)))

    def test_estudiante_no_puede_editar(self):
        """La función objeto puede_editar_causa restringe a ESTUDIANTE."""
        est = crear_usuario('est_e', rol='ESTUDIANTE')
        self.assertFalse(puede_editar_causa(est, self._causa(est)))


# =============================================================================
# IDOR — Consentimientos
# =============================================================================

class IDORConsentimientoTest(TestCase):
    """
    Verifica que _puede_acceder_consentimiento bloquea ESTUDIANTES ajenos
    y permite a ADMIN/SUPERVISOR cualquier consentimiento.
    """

    def setUp(self):
        self.estado = EstadoCausa.objects.create(nombre='En curso', color='#0f0', orden=1)
        self.tribunal = Tribunal.objects.create(nombre='Juzgado', activo=True)
        self.materia = Materia.objects.create(nombre='Penal', activo=True)

        self.admin = crear_usuario('adm_c', rol='ADMIN')
        self.supervisor = crear_usuario('sup_c', rol='SUPERVISOR')
        self.estudiante_dueño = crear_usuario('est_dueno', rol='ESTUDIANTE')
        self.estudiante_ajeno = crear_usuario('est_ajeno', rol='ESTUDIANTE')

        self.persona = Persona.objects.create(
            run=rut_valido('18000000'),
            nombres='Ana', apellidos='López',
            email='ana@test.cl', tipo_persona='NATURAL',
        )
        self.causa = Causa.objects.create(
            rit='C-002-2026',
            materia=self.materia,
            tribunal=self.tribunal,
            estado=self.estado,
            responsable=self.estudiante_dueño,
        )
        CausaPersona.objects.create(
            causa=self.causa,
            persona=self.persona,
            rol_en_causa='IMPUTADO',
        )
        self.consentimiento = Consentimiento.objects.create(
            persona=self.persona,
            tipo='DATOS_PERSONALES',
            otorgado=True,
            fecha_otorgamiento=date.today(),
            registrado_por=self.estudiante_dueño,
        )

    def test_admin_puede_acceder(self):
        self.assertTrue(_puede_acceder_consentimiento(self.admin, self.consentimiento))

    def test_supervisor_puede_acceder(self):
        self.assertTrue(_puede_acceder_consentimiento(self.supervisor, self.consentimiento))

    def test_estudiante_dueño_puede_acceder(self):
        self.assertTrue(_puede_acceder_consentimiento(self.estudiante_dueño, self.consentimiento))

    def test_estudiante_ajeno_no_puede_acceder(self):
        self.assertFalse(_puede_acceder_consentimiento(self.estudiante_ajeno, self.consentimiento))

    def test_vista_detalle_devuelve_403_a_ajeno(self):
        c = Client()
        c.login(username='est_ajeno', password='Pass1234!')
        url = reverse('gestion:consentimiento_detalle', kwargs={'pk': self.consentimiento.pk})
        response = c.get(url)
        self.assertEqual(response.status_code, 403)

    def test_vista_revocar_devuelve_403_a_ajeno(self):
        c = Client()
        c.login(username='est_ajeno', password='Pass1234!')
        url = reverse('gestion:consentimiento_revocar', kwargs={'pk': self.consentimiento.pk})
        response = c.post(url)
        self.assertEqual(response.status_code, 403)


class DobleRevocacionTest(TestCase):
    """BUG-15: consentimiento ya revocado no puede revocarse otra vez."""

    def setUp(self):
        self.admin = crear_usuario('adm_rev', rol='ADMIN')
        self.persona = Persona.objects.create(
            run=rut_valido('18000001'),
            nombres='Pedro', apellidos='Soto',
            email='pedro@test.cl', tipo_persona='NATURAL',
        )
        self.consentimiento = Consentimiento.objects.create(
            persona=self.persona,
            tipo='NOTIFICACIONES',
            otorgado=True,
            fecha_otorgamiento=date.today(),
            fecha_revocacion=date.today(),   # ya revocado
            registrado_por=self.admin,
        )

    def test_revocar_ya_revocado_redirige_con_warning(self):
        c = Client()
        c.login(username='adm_rev', password='Pass1234!')
        url = reverse('gestion:consentimiento_revocar', kwargs={'pk': self.consentimiento.pk})
        response = c.post(url)
        self.assertRedirects(
            response,
            reverse('gestion:consentimiento_detalle', kwargs={'pk': self.consentimiento.pk}),
        )
        # La fecha de revocación no cambió (sigue siendo today)
        self.consentimiento.refresh_from_db()
        self.assertEqual(self.consentimiento.fecha_revocacion, date.today())
