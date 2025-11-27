from django.contrib import admin
from .models import Genero, Rol, Usuario, UserRol

admin.site.register(Genero)
admin.site.register(Rol)
admin.site.register(Usuario)
admin.site.register(UserRol)
