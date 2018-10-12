from django.contrib.auth.models import User, Group
from django.http import HttpResponse, JsonResponse
from datetime import datetime

from rest_framework import viewsets
from api.serializers import UserSerializer, GroupSerializer, DepartementSerializer, BanqueSerializer, CompteBancaireSerializer, SituationSerializer, HistoriqueSerializer
from api.models import Departement, Banque, CompteBancaire, Situation, Historique

from rest_framework import status,generics
from rest_framework.decorators import api_view,permission_classes
from rest_framework.permissions import IsAuthenticated,AllowAny

from rest_framework.response import Response


from rest_framework.authtoken.models import Token

from Scraper import getDatas
import json, time


import logging, logging.config
import sys

LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'stream': sys.stdout,
        }
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO'
    }
}

logging.config.dictConfig(LOGGING)
logging.info('Hello')


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer


class GroupViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Group.objects.all()
    serializer_class = GroupSerializer

class DepartementViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Departement.objects.all()
    serializer_class = DepartementSerializer

class BanqueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """
    queryset = Banque.objects.all()
    serializer_class = BanqueSerializer

class CompteBancaireViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = CompteBancaire.objects.all()
    serializer_class = CompteBancaireSerializer

class SituationViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Situation.objects.all()
    serializer_class = SituationSerializer

class HistoriqueViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows groups to be viewed or edited.
    """

    queryset = Historique.objects.all()
    serializer_class = HistoriqueSerializer



#OLD
class oldGetSituation(generics.ListAPIView):

    serializer_class = SituationSerializer

    def get_queryset(self):

        requestToken = self.request.META['HTTP_AUTHORIZATION'].replace('Token ','')

        """ On va récupérer le User pour pouvoir filtrer les situation """
        user_id = Token.objects.get(key=requestToken).user_id
        user = User.objects.get(id=user_id)

        return Situation.objects.filter(utilisateur=user)


#Renvoie tout
@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def getSituation(request):

    if request.method == 'GET':

        requestToken = request.META['HTTP_AUTHORIZATION'].replace('Token ','')
        user_id = Token.objects.get(key=requestToken).user_id
        user = User.objects.get(id=user_id)

        #On recupere les comptes bancaire du user
        cpts = CompteBancaire.objects.filter(utilisateur=user)
        comptesBancaires=[]
        for compte in cpts:
            item = {'nom_banque': compte.banque.nom_banque ,
                    'login_compteBancaire': compte.login_compteBancaire,
                    'id_compteBancaire': compte.id_compteBancaire}
            #comptesBancaires.append(CompteBancaireSerializer(compte).cpts)
            comptesBancaires.append(item)

        #On recupere l'historique du user (comprend les blocs)
        historique = Historique.objects.filter(utilisateur=user)

        datas = {'situation':HistoriqueSerializer(historique[0]).data,
         'infoUser':{'email':user.email}, 'comptes':comptesBancaires}

        return Response(datas, status=status.HTTP_200_OK)



@api_view(['GET', 'POST'])
@permission_classes((IsAuthenticated,))
def compteBancaire(request):

    if request.method == 'GET':
        logging.info(request)

        token_recu = request.META['HTTP_AUTHORIZATION'].replace('Token ','')

        user_id = Token.objects.get(key=token_recu).user_id
        user = User.objects.get(id=user_id)

        data = CompteBancaire.objects.filter(utilisateur=user)
        serializer=[]
        for compte in data:
            serializer.append(CompteBancaireSerializer(compte).data)
        #serializer = CompteBancaireSerializer(data[0])
        logging.info(serializer)
        return Response(serializer, status=status.HTTP_200_OK)



    if request.method == 'POST':
        logging.info(request.data)

        token_recu = request.META['HTTP_AUTHORIZATION'].replace('Token ','')

        user_id = Token.objects.get(key=token_recu).user_id
        #user = User.objects.get(id=user_id)

        bank = Banque.objects.filter(id_banque=request.data['banque'])[0]
        datasVerif = getDatas(bank.wb_banque,request.data['login_compteBancaire'],request.data['password_compteBancaire'],bank.wb_website)
        datasVerif = json.loads(datasVerif)

        logging.info(datasVerif)
        #On verifie que la connexion s'est bien passé, si tel est le cas
        #On enregistre le compte en base et on return ses infos
        #Sinon on renvoit KO
        if (datasVerif['status']=='OK'):
            data = {
                'login_compteBancaire': request.data['login_compteBancaire'],
                'password_compteBancaire': request.data['password_compteBancaire'],
                'banque': request.data['banque'],
                'utilisateur': user_id
            }

            serializer = CompteBancaireSerializer(data=data)

            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response("KO", status=status.HTTP_400_BAD_REQUEST)



@api_view(['PUT', 'GET'])
@permission_classes((IsAuthenticated,))
def historiqueEspece(request):

    if request.method == 'PUT':
        logging.info(request.data)
        token_recu = request.META['HTTP_AUTHORIZATION'].replace('Token ','')
        user_id = Token.objects.get(key=token_recu).user_id
        user = User.objects.get(id=user_id)
        historique = Historique.objects.filter(utilisateur=user)[0]

        #On recupere le dernier blocs, on maj le solde espece et on append avec un nouvel ID et une nouvelle date
        lastBloc = historique.blocs['blocs'][-1]
        bloc = {
            "ID" : lastBloc["ID"]+1,
            "nature":"maj_espece",
            "date":str(datetime.now()),
            "solde_banque" : lastBloc["solde_banque"],
            "solde_espece" : request.data['montant'],
            "solde_immo" : lastBloc["solde_immo"],
            "etat" : "actif"
        }
        historique.blocs['blocs'].append(bloc)
        historique.save()
        return Response(historique.blocs['blocs'], status=status.HTTP_200_OK)



@api_view(['PUT', 'GET'])
@permission_classes((IsAuthenticated,))
def historiqueImmo(request):

    if request.method == 'PUT':
        logging.info(request.data)
        token_recu = request.META['HTTP_AUTHORIZATION'].replace('Token ','')
        user_id = Token.objects.get(key=token_recu).user_id
        user = User.objects.get(id=user_id)
        historique = Historique.objects.filter(utilisateur=user)[0]

        #On recupere le dernier blocs, on maj le solde espece et on append avec un nouvel ID et une nouvelle date
        lastBloc = historique.blocs['blocs'][-1]
        bloc = {
            "ID" : lastBloc["ID"]+1,
            "nature":"maj_immo",
            "date":str(datetime.now()),
            "solde_banque" : lastBloc["solde_banque"],
            "solde_espece" : lastBloc["solde_espece"],
            "solde_immo" : request.data['montant'],
            "etat" : "actif"
        }
        historique.blocs['blocs'].append(bloc)
        historique.save()
        return Response(historique.blocs['blocs'], status=status.HTTP_200_OK)


@api_view(['PUT', 'GET'])
@permission_classes((IsAuthenticated,))
def majEtatBloc(request):

    if request.method == 'PUT':
        logging.info(request.data)
        token_recu = request.META['HTTP_AUTHORIZATION'].replace('Token ','')
        user_id = Token.objects.get(key=token_recu).user_id
        user = User.objects.get(id=user_id)
        historique = Historique.objects.filter(utilisateur=user)[0]

        for bloc in historique.blocs['blocs']:
            if bloc['ID'] == request.data['ID']:
                bloc['etat'] = request.data['etat']
                break;

        historique.save()
        return Response(historique.blocs['blocs'], status=status.HTTP_200_OK)

@api_view(['GET'])
@permission_classes((IsAuthenticated,))
def majSolde(request):

    startTime = time.time()
    if request.method == 'GET':
            token_recu = request.META['HTTP_AUTHORIZATION'].replace('Token ','')
            user_id = Token.objects.get(key=token_recu).user_id
            user = User.objects.get(id=user_id)

            comptesBancaires = CompteBancaire.objects.filter(utilisateur=user)
            nouvelItem=[]
            #Pour chaque compte de l'utilisateur n va recuperer son solde via Weboob
            for cpt in comptesBancaires:
                print("\tRecuperation des datas de " + cpt.utilisateur.username + " chez " + cpt.banque.nom_banque + " ID:"+ str(cpt.id_compteBancaire) )
                datas = getDatas(cpt.banque.wb_banque,cpt.login_compteBancaire,cpt.password_compteBancaire,cpt.banque.wb_website)
                datas = json.loads(datas)

                nouvelItem.append({
                    "id_compteBancaire":cpt.id_compteBancaire,
                    "date":str(datetime.now()),
                    "nom_banque":cpt.banque.nom_banque,
                    "status":datas["status"],
                    "solde":datas["solde"],
                    "details":datas["details"]
                })

            if len(comptesBancaires) > 0 :
                historique = Historique.objects.filter(utilisateur=user)[0]
                #On recupere le dernier blocs, on maj le solde espece et on append avec un nouvel ID et une nouvelle date
                lastBloc = historique.blocs['blocs'][-1]
                bloc = {
                    "ID" : lastBloc["ID"]+1,
                    "nature":"maj_banque_manu",
                    "date":str(datetime.now()),
                    "solde_banque" : nouvelItem,
                    "solde_espece" : lastBloc["solde_espece"],
                    "solde_immo" : lastBloc["solde_immo"],
                    "etat" : "actif"
                }
                historique.blocs['blocs'].append(bloc)
                historique.save()

            endTime = time.time()
            tempsTotal = round(endTime - startTime,2)
            print ("temps total: "+ str(tempsTotal)+' sec')
            return Response(historique.blocs['blocs'], status=status.HTTP_200_OK)



#OLD
class weshCompteBancaire(generics.RetrieveUpdateDestroyAPIView):
            queryset = CompteBancaire.objects.all()
            serializer_class = CompteBancaireSerializer


#OLD
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes((IsAuthenticated, ))
def bonjour_appel(request):
    """
    Retrieve, update or delete a code snippet.
    """

    if request.method == 'GET':

        try:
            request.META['HTTP_AUTHORIZATION']
        except:
            reqToken = "pas de token"
            username = ""
        else:
            reqToken = request.META['HTTP_AUTHORIZATION'].replace('Token ','')
            username = ""

            try:
                Token.objects.get(key=reqToken)
            except:
                username = "Ce token existe pas"
            else:
                id = Token.objects.get(key=reqToken).user_id
                username = User.objects.get(id=id).username

        content={
         "phrase": "bonjour",
         "request token": reqToken,
         "username" : username
         }

        return Response(content)
