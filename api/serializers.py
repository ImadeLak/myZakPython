from django.contrib.auth.models import User, Group
from rest_framework import serializers
from api.models import Departement, Banque, CompteBancaire, Situation, Historique


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'url', 'username', 'email', 'groups','password')


class GroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = Group
        fields = ('url', 'name')

class BanqueSerializer(serializers.ModelSerializer):

    class Meta:
        model = Banque
        fields = ('id_banque', 'nom_banque', 'wb_banque', 'wb_website')

class CompteBancaireSerializer(serializers.ModelSerializer):

    class Meta:
        model = CompteBancaire
        fields = ('id_compteBancaire', 'login_compteBancaire', 'password_compteBancaire', 'banque', 'utilisateur')

class DepartementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Departement
        fields = ('numero', 'nom_departement', 'mon_utilisateur')

class SituationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Situation
        fields = ('id_situation', 'date_situation', 'solde_banque', 'solde_espece', 'isImposable_or', 'isImposable_argent')

class JSONSerializerField(serializers.Field):
    """ Serializer for JSONField -- required to make field writable"""
    def to_internal_value(self, data):
        return data
    def to_representation(self, value):
        return value

class HistoriqueSerializer(serializers.ModelSerializer):
    #historique_immo = JSONSerializerField()
    #historique_banque = JSONSerializerField()
    #historique_espece = JSONSerializerField()
    blocs = JSONSerializerField()

    class Meta:
        model = Historique
        fields = ('id_historique','utilisateur','blocs')
