from django.db import models
from django.contrib.auth.hashers import make_password, check_password



class Genero(models.Model):
    id_genero = models.AutoField(primary_key=True, db_column='id_genero')
    genero = models.CharField(max_length=20, db_column='genero')

    class Meta:
        db_table = 'genero'
        managed = False

    def __str__(self):
        return self.genero


class Rol(models.Model):
    id_rol = models.AutoField(primary_key=True, db_column='id_rol')
    rol = models.CharField(max_length=20, db_column='rol')

    class Meta:
        db_table = 'roles'
        managed = False

    def __str__(self):
        return self.rol


class Usuario(models.Model):
    id_usuario = models.AutoField(primary_key=True, db_column='id_usuario')

    genero = models.ForeignKey(
        Genero,
        on_delete=models.SET_NULL,
        db_column='id_genero',
        null=True,
        blank=True,
        related_name='usuarios'
    )

    nombre = models.CharField(max_length=20, db_column='nombre')
    apellido1 = models.CharField(max_length=50, db_column='apellido1')
    apellido2 = models.CharField(max_length=50, db_column='apellido2', null=True, blank=True)
    fecha_nacimiento = models.DateField(db_column='fecha_nacimiento', null=True, blank=True)
    correo = models.EmailField(max_length=50, db_column='correo', unique=True)
    password = models.CharField(max_length=200, db_column='password')
    estado = models.CharField(max_length=20, db_column='estado', null=True, blank=True)

    last_login = models.DateTimeField(db_column='last_login', null=True, blank=True)

    fecha_creacion = models.DateField(db_column='fechacreacion', null=True, blank=True)
    fecha_actualizacion = models.DateField(db_column='fechaactualizacion', null=True, blank=True)
    fecha_eliminacion = models.DateField(db_column='fechaeliminacion', null=True, blank=True)

    class Meta:
        db_table = 'usuario'
        managed = False

    def __str__(self):
        return f"{self.nombre} {self.apellido1}"
    
    def get_email_field_name(self):
        """
        Django lo usa en la generación del token para recuperación de contraseña.
        En nuestro modelo, el campo de correo se llama 'correo'.
        """
        return 'correo'

    @property
    def is_authenticated(self):
        """Compatibilidad con el sistema de autenticación de Django."""
        return True

    @property
    def is_active(self):
        """
        El usuario solo se considera activo si su estado es 'ACTIVO'
        (o si no tiene estado definido todavía).
        """
        if self.estado is None or self.estado == "":
            return True
        return self.estado.upper() == "ACTIVO"

    @property
    def is_anonymous(self):
        return False

    def set_password(self, raw_password: str):
        """Guarda la contraseña hasheada."""
        self.password = make_password(raw_password)

    def check_password(self, raw_password: str) -> bool:
        """Verifica la contraseña contra el hash almacenado."""
        return check_password(raw_password, self.password)


        # =========================
    #   Helpers de roles
    # =========================
    def tiene_rol(self, nombre_rol: str) -> bool:
        """
        Revisa si el usuario tiene un rol con ese nombre.
        Usa la relación UserRol -> Rol -> campo 'rol'.
        """
        return self.roles.filter(rol__rol__iexact=nombre_rol).exists()
        # rol__rol:
        #   primer 'rol' = FK de UserRol
        #   segundo 'rol' = campo de la tabla Roles

    @property
    def es_doctor(self) -> bool:
        return self.tiene_rol('Medico')  # AJUSTA AL TEXTO REAL QUE TENGAS EN BD

    @property
    def es_paciente(self) -> bool:
        return self.tiene_rol('Paciente')  # idem

    @property
    def es_admin(self) -> bool:
        return self.tiene_rol('Administrador')  # o 'Administrador', según tu tabla

    @property
    def lista_roles(self):
        return ", ".join(ur.rol.rol for ur in self.roles.all())

    @property
    def is_staff(self):
        """
        Requerido por el admin de Django y algunos decoradores.
        Lo ligamos a que el usuario tenga rol de Administrador.
        """
        return self.es_admin

    @property
    def is_superuser(self):
        """
        Para simplificar, tratamos al Administrador como superusuario.
        Si quisieras algo más fino, podrías usar otro rol.
        """
        return self.es_admin

    def has_perm(self, perm, obj=None):
        """
        Método que usa el sistema de permisos del admin.
        Por ahora, si es admin le damos todos los permisos.
        """
        return self.es_admin

    def has_module_perms(self, app_label):
        """
        Igual que has_perm, pero a nivel de aplicación.
        """
        return self.es_admin


class UserRol(models.Model):
    id_userrol = models.AutoField(primary_key=True, db_column='id_userrol')

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        db_column='id_usuario',
        related_name='roles'
    )
    rol = models.ForeignKey(
        Rol,
        on_delete=models.CASCADE,
        db_column='id_rol',
        related_name='usuarios'
    )

    class Meta:
        db_table = 'userrol'
        managed = False

    def __str__(self):
        return f"{self.usuario} - {self.rol}"
