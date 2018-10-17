from django.contrib.auth.models import Group #,User
from rest_framework import serializers
from appMyZak.models import Departement, Banque, CompteBancaire, Situation, Historique, UserCustom

"""
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserCustom
        fields = ('id', 'url', 'username', 'email', 'groups','password')
"""

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserCustom
        fields = ( 'email', 'password')

    def create(self, validated_data):
        user = super(UserSerializer, self).create(validated_data)
        user.set_password(validated_data['password'])
        user.save()
        return user

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
