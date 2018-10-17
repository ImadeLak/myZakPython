"""myApi URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework import routers
from appMyZak import views


from rest_framework.authtoken import views as rest_framework_views

admin.autodiscover()

router = routers.DefaultRouter()
router.register(r'users', views.UserViewSet)
router.register(r'groups', views.GroupViewSet)
router.register(r'departements', views.DepartementViewSet)
router.register(r'banques', views.BanqueViewSet)
router.register(r'comptebancaires', views.CompteBancaireViewSet)
router.register(r'situations', views.SituationViewSet)
router.register(r'historiques', views.HistoriqueViewSet)


# Wire up our API using automatic URL routing.
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    url(r'^', include(router.urls)),
    url(r'^admin/', admin.site.urls ),
    url(r'^compte_bancaire/', views.compteBancaire),
    url(r'^historique_espece/', views.historiqueEspece),
    url(r'^historique_immo/', views.historiqueImmo),
    url(r'^maj_solde/', views.majSolde),
    url(r'^maj_etat_bloc/', views.majEtatBloc),
    url(r'^edit_compte_bancaire/(?P<pk>[0-9]+)/$', views.weshCompteBancaire.as_view() ),
    #url(r'^get_situation/', views.getSituation.as_view() ),
    url(r'^get_historique/', views.getSituation),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
    url(r'^bonjour/$', views.bonjour_appel),

    url(r'^create_user/$', views.createUser),
]
