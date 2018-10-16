from django.db import models
from jsonfield import JSONField

#ajout pour les Token
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
#from django.contrib.auth.models import User

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import ugettext_lazy as _


#ajout pour creer un token a chaque user créé
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_auth_token(sender, instance=None, created=False, **kwargs):
    if created:
        Token.objects.create(user=instance)

""" pour avoir juste l'email """
class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(self, email, password, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError('The given email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular User with the given email and password."""
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self._create_user(email, password, **extra_fields)

""" pour avoir juste l'email """
class UserCustom(AbstractUser):
    """User model."""

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    objects = UserManager()

# Create your models here.
class Departement(models.Model):
    numero=models.IntegerField()
    nom_departement=models.CharField(max_length=50)
    dep_ip=models.AutoField(primary_key=True)
    mon_utilisateur=models.ForeignKey(UserCustom, on_delete=models.CASCADE)

    def __str__(self):
        return  self.nom_departement

class Banque(models.Model):
    id_banque=models.AutoField(primary_key=True)
    nom_banque=models.CharField(max_length=50)
    wb_banque=models.CharField(max_length=500)
    wb_website=models.CharField(max_length=500)
    #en fait non, il faudra retirer les URL et mettre seulement, un identifiant txt et un nom complet

    def __str__(self):
        return  self.nom_banque

class CompteBancaire(models.Model):
    id_compteBancaire=models.AutoField(primary_key=True)
    login_compteBancaire=models.CharField(max_length=50)
    password_compteBancaire=models.CharField(max_length=50)
    banque=models.ForeignKey(Banque, on_delete=models.CASCADE)
    utilisateur=models.ForeignKey(UserCustom, on_delete=models.CASCADE)
    def __str__(self):
        return  str(self.id_compteBancaire)+' '+self.banque.nom_banque+' Usr: '+self.utilisateur.email

class Situation(models.Model):
    id_situation=models.AutoField(primary_key=True)
    date_situation=models.DateTimeField()
    utilisateur=models.ForeignKey(UserCustom, on_delete=models.CASCADE)
    solde_banque=models.IntegerField()
    solde_espece=models.IntegerField()
    isImposable_or=models.BooleanField()
    isImposable_argent=models.BooleanField()

    def __str__(self):
        return  str(self.date_situation)+' '+self.utilisateur.email+' '+str(self.solde_banque)+' €'


"""
"dates":[
    {
      "date_historique":"2018-08-13 22:07:20.585419",
      "comptes_bancaires":[
        {
          "nom_banque":"LCL",
          "id_compteBancaire":4,
          "solde":4591.86,
          "details":[
            {
              "libelle":"Compte de d\u00e9p\u00f4ts",
              "solde":313.23
            },
            {
              "libelle":"Compte sur livret",
              "solde":15.22
            },
          ]
        }
      ]
    }
]
"""

class Historique(models.Model):
    id_historique=models.AutoField(primary_key=True)
    utilisateur=models.ForeignKey(UserCustom, on_delete=models.CASCADE)
    #historique_espece=JSONField(default='{"dates":[]}')
    #historique_immo=JSONField(default='{"dates":[]}')
    #historique_banque=JSONField(default='{"dates":[]}')
    blocs=JSONField(default='{"blocs":[{"ID":0,"nature":"init","date":"","solde_banque":0,"solde_espece":0,"solde_immo":0,"etat":"disabled"}]}')

    def __str__(self):
        return  self.utilisateur.email
