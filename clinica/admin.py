from django.contrib import admin
from .models import (
    RangoColesterol,
    RangoGlucosa,
    RangoIMC,
    RangoPresionSanguinea,
    CitaMedica,
)

admin.site.register(RangoColesterol)
admin.site.register(RangoGlucosa)
admin.site.register(RangoIMC)
admin.site.register(RangoPresionSanguinea)
admin.site.register(CitaMedica)
