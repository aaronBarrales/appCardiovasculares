from django.contrib import admin
from .models import (
    RangoColesterol,
    RangoGlucosa,
    Prediccion,
    CitaMedica,
)


admin.site.register(RangoColesterol)
admin.site.register(RangoGlucosa)
admin.site.register(CitaMedica)
