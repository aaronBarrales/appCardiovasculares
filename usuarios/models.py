from django.db import models
from django.contrib.auth.hashers import make_password, check_password
from django.utils import timezone

class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True, db_column='ID_Genero')
    genero = models.CharField(max_length=20, db_column='Genero')

    class Meta:
        managed = False
        db_table = '"Genero"'

    def __str__(self):
        return self.genero


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True, db_column='ID_Rol')
    rol = models.CharField(max_length=20, db_column='Rol')

    class Meta:
        managed = False
        db_table = '"Roles"'

    def __str__(self):
        return self.rol


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, db_column='ID_Usuario')

    genero = models.ForeignKey(
        Genero,
        on_delete=models.RESTRICT,
        db_column='ID_Genero',
        related_name='usuarios'
    )

    nombre = models.CharField(max_length=20, db_column='Nombre')
    apellido1 = models.CharField(max_length=50, db_column='Apellido1')
    apellido2 = models.CharField(max_length=50, db_column='Apellido2', null=True, blank=True)

    fecha_nacimiento = models.DateField(db_column='Fecha_Nacimiento')
    correo = models.EmailField(max_length=50, db_column='Correo', unique=True)

    password = models.CharField(max_length=200, db_column='Password')
    estado = models.CharField(max_length=20, db_column='Estado', default='ACTIVO')

    fecha_creacion = models.DateTimeField(db_column='FechaCreacion', default=timezone.now)
    fecha_actualizacion = models.DateTimeField(db_column='FechaActualizacion', default=timezone.now)
    fecha_eliminacion = models.DateTimeField(db_column='FechaEliminacion', null=True, blank=True)

    # Campo “de compatibilidad” si lo usas para auth manual
    last_login = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed = False
        db_table = '"Usuario"'

    def __str__(self):
        return f"{self.nombre} {self.apellido1}"

    # ===== Password helpers =====
    def set_password(self, raw_password: str):
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        return check_password(raw_password, self.password)

    # ===== Roles helpers =====
    def tiene_rol(self, nombre_rol: str) -> bool:
        return self.roles.filter(rol__rol__iexact=nombre_rol).exists()

    @property
    def es_medico(self) -> bool:
        return self.tiene_rol('medico')

    @property
    def es_paciente(self) -> bool:
        return self.tiene_rol('paciente')

    @property
    def es_admin(self) -> bool:
        return self.tiene_rol('administrador')

    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return (self.estado or '').upper() == 'ACTIVO' or self.estado in (None, '')

    @property
    def is_anonymous(self):
        return False

    @property
    def is_staff(self):
        return self.es_admin

    @property
    def is_superuser(self):
        return self.es_admin

    def has_perm(self, perm, obj=None):
        return self.es_admin

    def has_module_perms(self, app_label):
        return self.es_admin

    @classmethod
    def get_email_field_name(cls):
        return 'correo'


class UserRol(models.Model):
    id_userrol = models.AutoField(primary_key=True, db_column='ID_UserRol')

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='ID_Usuario',
        related_name='roles'
    )

    rol = models.ForeignKey(
        Rol,
        on_delete=models.RESTRICT,
        db_column='ID_Rol',
        related_name='usuarios'
    )

    class Meta:
        managed = False
        db_table = '"UserRol"'
        unique_together = (('usuario', 'rol'),)

    def __str__(self):
        return f"{self.usuario} - {self.rol}"
