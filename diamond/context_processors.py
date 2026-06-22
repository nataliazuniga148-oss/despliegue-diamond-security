from .models import Perfil
from .models import ConfiguracionSistema

def configuracion_global(request):
    configuracion, _ = ConfiguracionSistema.objects.get_or_create(id=1)

    return {
        "configuracion": configuracion
    }

def perfil_usuario(request):
    if request.user.is_authenticated:
        perfil, _ = Perfil.objects.get_or_create(usuario=request.user)
        return {'perfil': perfil}
    return {}
from PIL import Image

def save(self, *args, **kwargs):
    super().save(*args, **kwargs)

    if self.foto:
        img = Image.open(self.foto.path)

        # 🔥 mejorar calidad
        img = img.convert("RGB")

        # tamaño óptimo
        img.thumbnail((300, 300))

        img.save(self.foto.path, quality=95)