from django.db import models


class RangoColesterol(models.Model):
    id_rango_colesterol = models.AutoField(primary_key=True, db_column='id_rangocolesterol')
    codigo_rango_colesterol = models.IntegerField(db_column='codigorangocolesterol', null=True, blank=True)
    min = models.FloatField(db_column='min', null=True, blank=True)
    max = models.FloatField(db_column='max', null=True, blank=True)
    version_modelo = models.CharField(max_length=10, db_column='versionmodelo', null=True, blank=True)
    descripcion = models.CharField(max_length=20, null=True, blank=True)


    class Meta:
        db_table = 'rangocolesterol'
        managed = False

    def __str__(self):
        return f"{self.min} - {self.max}"


class RangoGlucosa(models.Model):
    id_rango_glucosa = models.AutoField(primary_key=True, db_column='id_rangoglucosa')
    codigo_rango_glucosa = models.IntegerField(db_column='codigorangoglucosa', null=True, blank=True)
    min = models.FloatField(db_column='min', null=True, blank=True)
    max = models.FloatField(db_column='max', null=True, blank=True)
    version_modelo = models.CharField(max_length=10, db_column='versionmodelo', null=True, blank=True)
    descripcion = models.CharField(max_length=20, null=True, blank=True)


    class Meta:
        db_table = 'rangoglucosa'
        managed = False

    def __str__(self):
        return f"{self.min} - {self.max}"


class RangoIMC(models.Model):
    id_rango_imc = models.AutoField(primary_key=True, db_column='id_rangoimc')
    codigo_rango_imc = models.IntegerField(db_column='codigorangoimc', null=True, blank=True)
    min = models.FloatField(db_column='min', null=True, blank=True)
    max = models.FloatField(db_column='max', null=True, blank=True)
    version_modelo = models.CharField(max_length=10, db_column='versionmodelo', null=True, blank=True)
    descripcion = models.CharField(max_length=20, null=True, blank=True)


    class Meta:
        db_table = 'rangoimc'
        managed = False

    def __str__(self):
        return f"{self.min} - {self.max}"


class RangoPresionSanguinea(models.Model):
    id_rango_presion_sanguinea = models.AutoField(primary_key=True, db_column='id_rangopresionsanguinea')
    codigo_rango_colesterol = models.IntegerField(db_column='codigorangocolesterol', null=True, blank=True)
    min = models.FloatField(db_column='min', null=True, blank=True)
    max = models.FloatField(db_column='max', null=True, blank=True)
    version_modelo = models.CharField(max_length=10, db_column='versionmodelo', null=True, blank=True)
    descripcion = models.CharField(max_length=20, null=True, blank=True)


    class Meta:
        db_table = 'rangopresionsanguinea'
        managed = False

    def __str__(self):
        return f"{self.min} - {self.max}"


class CitaMedica(models.Model):
    id_cita = models.AutoField(primary_key=True, db_column='id_cita')

    paciente = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        db_column='id_paciente',
        related_name='citas_como_paciente'
    )

    doctor = models.ForeignKey(
        'usuarios.Usuario',
        on_delete=models.CASCADE,
        db_column='id_doctor',
        related_name='citas_como_doctor'
    )

    rango_colesterol = models.ForeignKey(
        RangoColesterol,
        on_delete=models.SET_NULL,
        db_column='id_rangocolesterol',
        null=True,
        blank=True
    )
    rango_glucosa = models.ForeignKey(
        RangoGlucosa,
        on_delete=models.SET_NULL,
        db_column='id_rangoglucosa',
        null=True,
        blank=True
    )
    rango_presion_sanguinea = models.ForeignKey(
        RangoPresionSanguinea,
        on_delete=models.SET_NULL,
        db_column='id_rangopresionsanguinea',
        null=True,
        blank=True
    )
    rango_imc = models.ForeignKey(
        RangoIMC,
        on_delete=models.SET_NULL,
        db_column='id_rangoimc',
        null=True,
        blank=True
    )

    peso = models.FloatField(db_column='peso', null=True, blank=True)
    estatura = models.FloatField(db_column='estatura', null=True, blank=True)
    fecha_cita = models.DateField(db_column='fecha_cita', null=True, blank=True)
    notas = models.CharField(max_length=255, db_column='notas', null=True, blank=True)

    alcohol = models.BooleanField(db_column='alcohol', default=False)
    drogas = models.BooleanField(db_column='drogas', default=False)
    actividad_fisica = models.BooleanField(db_column='actividad_fisica', default=False)
    fumador = models.BooleanField(db_column='fumador', default=False)

    enfermedad_cardiovascular = models.FloatField(db_column='enfermedadcardiovascular', null=True, blank=True)

    fecha_creacion = models.DateField(db_column='fechacreacion', null=True, blank=True)
    fecha_actualizacion = models.DateField(db_column='fechaactualizacion', null=True, blank=True)
    fecha_eliminacion = models.DateField(db_column='fechaeliminacion', null=True, blank=True)
    estado = models.CharField(max_length=20, db_column='estado', null=True, blank=True)

    class Meta:
        db_table = 'cita_medica'
        managed = False
        indexes = [
            models.Index(fields=['paciente'], name='idx_cita_paciente'),
            models.Index(fields=['doctor'], name='idx_cita_doctor'),
        ]

    def __str__(self):
        return f"Cita {self.id_cita}"
