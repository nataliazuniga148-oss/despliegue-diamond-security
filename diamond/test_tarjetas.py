from django.test import TestCase
from .models import Tarjeta
from django.db.utils import IntegrityError

class TarjetaTest(TestCase):

    def test_tarjeta_activa(self):
        tarjeta = Tarjeta.objects.create(
            numero="2034",
            activa=True
        )
        self.assertTrue(tarjeta.activa)
        
    def test_cambiar_estado_tarjeta(self):
        tarjeta = Tarjeta.objects.create(
            numero="1002",
            activa=True
        )

        tarjeta.activa = False
        tarjeta.save()

        tarjeta.refresh_from_db()

        self.assertFalse(tarjeta.activa)
        #probamos si se puede duplicar un número de tarjeta
class TarjetaTest(TestCase):
    
    def test_no_permitir_tarjeta_duplicada(self):
        Tarjeta.objects.create(
            numero="2001",
            activa=True
        )

        
        with self.assertRaises(Exception):
            Tarjeta.objects.create(
                numero="2001",
                activa=True
            )