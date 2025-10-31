from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

USERNAME_FIELD = 'email'

class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("L'adresse email est requise")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError("Le superutilisateur doit avoir is_staff=True.")
        if extra_fields.get('is_superuser') is not True:
            raise ValueError("Le superutilisateur doit avoir is_superuser=True.")

        return self.create_user(email, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True, null=True)
    last_name = models.CharField(max_length=150, blank=True, null=True)
    prenom = models.CharField(max_length=60, blank=True, null=True)
    nom = models.CharField(max_length=60, blank=True, null=True)
    tel = models.CharField(max_length=20, blank=True, null=True)
    date_de_creation = models.DateField(default=timezone.now)  

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['prenom', 'nom', 'tel']

    def __str__(self):
        return f"{self.prenom} {self.nom} ({self.email})"
    
    @property
    def first_name(self):
        return self.prenom
    
    @first_name.setter
    def first_name(self, value):
        self.prenom = value

    @property
    def last_name(self):
        return self.nom
    
    @last_name.setter
    def last_name(self, value):
        self.nom = value

