from django.db import models


class RangoColesterol(models.Model):
    id_rango_colesterol = models.AutoField(primary_key=True, db_column='ID_RangoColesterol')
    codigo_rango_colesterol = models.IntegerField(db_column='CodigoRangoColesterol')
    min = models.FloatField(db_column='Min')
    max = models.FloatField(db_column='Max')
    version_modelo = models.CharField(max_length=10, db_column='VersionModelo')
    descripcion = models.CharField(max_length=20, db_column='Descripcion')

    class Meta:
        managed = False
        db_table = '"RangoColesterol"'

    def __str__(self):
        return f"{self.codigo_rango_colesterol}: {self.min}-{self.max} ({self.version_modelo})"


class RangoGlucosa(models.Model):
    id_rango_glucosa = models.AutoField(primary_key=True, db_column='ID_RangoGlucosa')
    codigo_rango_glucosa = models.IntegerField(db_column='CodigoRangoGlucosa')
    min = models.FloatField(db_column='Min')
    max = models.FloatField(db_column='Max')
    version_modelo = models.CharField(max_length=10, db_column='VersionModelo')
    descripcion = models.CharField(max_length=20, db_column='Descripcion')

    class Meta:
        managed = False
        db_table = '"RangoGlucosa"'

    def __str__(self):
        return f"{self.codigo_rango_glucosa}: {self.min}-{self.max} ({self.version_modelo})"


class Prediccion(models.Model):
    id_prediccion = models.AutoField(primary_key=True, db_column='ID_Prediccion')
    probabilidad_riesgo = models.FloatField(db_column='ProbabilidadRiesgo')
    version_modelo = models.CharField(max_length=10, db_column='VersionModelo')
    # Si luego agregas FechaPrediccion en SQL, lo añades aquí:
    # fecha_prediccion = models.DateTimeField(db_column='FechaPrediccion')

    class Meta:
        managed = False
        db_table = '"Prediccion"'

    def __str__(self):
        return f"{self.probabilidad_riesgo:.2f}% ({self.version_modelo})"


class CitaMedica(models.Model):
    id_cita = models.AutoField(primary_key=True, db_column='ID_Cita')

    paciente = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.RESTRICT,
        db_column='ID_Patient',
        related_name='citas_como_paciente'
    )

    doctor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.RESTRICT,
        db_column='ID_Doctor',
        related_name='citas_como_doctor'
    )

    rango_colesterol = models.ForeignKey(
        RangoColesterol,
        on_delete=models.SET_NULL,
        db_column='ID_RangoColesterol',
        null=True,
        blank=True
    )

    rango_glucosa = models.ForeignKey(
        RangoGlucosa,
        on_delete=models.SET_NULL,
        db_column='ID_RangoGlucosa',
        null=True,
        blank=True
    )

    # Crudos
    peso = models.FloatField(db_column='Peso', null=True, blank=True)
    estatura = models.FloatField(db_column='Estatura', null=True, blank=True)
    colesterol_total = models.FloatField(db_column='ColesterolTotal', null=True, blank=True)
    presion_sistolica = models.FloatField(db_column='PresionSistolica', null=True, blank=True)
    presion_diastolica = models.FloatField(db_column='PresionDiastolica', null=True, blank=True)
    glucosa = models.FloatField(db_column='Glucosa', null=True, blank=True)
    imc_valor = models.FloatField(db_column='IMCValor', null=True, blank=True)

    fecha_cita = models.DateField(db_column='Fecha_Cita')
    notas = models.CharField(max_length=255, db_column='Notas', null=True, blank=True)

    alcohol = models.BooleanField(db_column='Alcohol', default=False)
    drogas = models.BooleanField(db_column='Drogas', default=False)
    actividad_fisica = models.BooleanField(db_column='Actividad_Fisica', default=False)
    fumador = models.BooleanField(db_column='Fumador', default=False)

    # Estado / auditoría
    estado = models.CharField(max_length=20, db_column='Estado', default='ACTIVO')
    fecha_creacion = models.DateTimeField(db_column='FechaCreacion')
    fecha_actualizacion = models.DateTimeField(db_column='FechaActualizacion')
    fecha_eliminacion = models.DateTimeField(db_column='FechaEliminacion', null=True, blank=True)

    # Predicción (1 a 1 opcional)
    prediccion = models.OneToOneField(
        Prediccion,
        on_delete=models.SET_NULL,
        db_column='ID_Prediccion',
        null=True,
        blank=True,
        related_name='cita'
    )

    class Meta:
        managed = False
        db_table = '"Cita_Medica"'
        indexes = [
            models.Index(fields=['paciente'], name='idx_cita_paciente'),
            models.Index(fields=['doctor'], name='idx_cita_doctor'),
        ]

    def __str__(self):
        return f"Cita {self.id_cita}"
