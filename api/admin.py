from django.contrib import admin
from api.models import Departement, Banque, CompteBancaire, Situation,Historique
# Register your models here.

admin.site.register(Departement)
admin.site.register(Banque)
admin.site.register(CompteBancaire)
admin.site.register(Situation)
admin.site.register(Historique)
