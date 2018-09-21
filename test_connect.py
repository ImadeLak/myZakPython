import os, sys, json, time
from datetime import datetime
proj_path = "./"
# This is so Django knows where to find stuff.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "myApi.settings")
sys.path.append(proj_path)
# This is so my local_settings.py gets loaded.
os.chdir(proj_path)
# This is so models get loaded.
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

""" C'est la que tout commence !!!! """

from django.contrib.auth.models import User, Group
from api.models import Departement, Banque, CompteBancaire, Situation, Historique
from Scraper import getSolde, getGrilleDecodee, getDatas

startTime = time.time()


#Les settings des banques
with open('bankSettings.json') as json_data:
    bankSettings = json.load(json_data)

""" L'idee, pour chaque user, on recupere les compteBancaires associes,
    et apres on maj la historiques. Donc un fil de situation par user.
"""

""" Bon now, on va recuperer les comptes bancaire de chaque user, et a chaque fois
    on mettra a jour leur historique, voila tout
"""

users = User.objects.all()
for user in users:
    #On commence par parcourir tous les compte bancaire a mettre a jour
    print ("Recuperation compte bancaire de", user.username)
    compteBancaires = CompteBancaire.objects.filter(utilisateur=user)
    #soldeBanque = 0

    nouvelItem={
            "date_historique":str(datetime.now()),
            "cron":True,
            "comptes_bancaires":[]
    }
    for cpt in compteBancaires:
        print("\tRecuperation des datas de " + cpt.utilisateur.username + " chez " + cpt.banque.nom_banque + " ID:"+ str(cpt.id_compteBancaire) )

        #datas = getSolde(bankSettings[cpt.banque.nom_banque], cpt.login_compteBancaire, cpt.password_compteBancaire)
        datas = getDatas(cpt.banque.wb_banque,cpt.login_compteBancaire,cpt.password_compteBancaire,cpt.banque.wb_website)
        datas = json.loads(datas)
        #historique_user = Historique.objects.filter(utilisateur=user)[0]

        nouvelItem["comptes_bancaires"].append({
            "id_compteBancaire":cpt.id_compteBancaire,
            "nom_banque":cpt.banque.nom_banque,
            "status":datas["status"],
            "solde":datas["solde"],
            "details":datas["details"]
        })
        #nouvelItem={str(datetime.now()) : nouvelItem}
        #print(historique_user.historique_banque)

        #print(historique_user.historique_banque['dates'])
    if len(compteBancaires) > 0 :
        historique_user = Historique.objects.filter(utilisateur=user)[0]
        historique_user.historique_banque['dates'].append(nouvelItem)
        historique_user.save()
        #print ("JSON",json.dumps(historique_user.historique_banque))
        print(json.dumps(nouvelItem))



endTime = time.time()

tempsTotal = round(endTime - startTime,2)
print (tempsTotal, " sec")
