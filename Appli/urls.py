from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='accueil'),
    path('contact', views.contact, name='contact'),
    path('services', views.services, name='services'),
    path('mon_activite', views.mon_activite, name='mon_activite'),
    path('about', views.about, name='about'),
    
    # --- CORRECTION DES CHEMINS DE RÉSERVATION ---
    
    # Réservation Pack 1 Jour (sans ID ou avec ID)
    path('reservation/jour/', 
         views.reservation_pack_jour, 
         name='reservation_jour_base'),

    path('reservation/jour/<int:pack_id>/', 
         views.reservation_pack_jour, 
         name='reservation_jour_detail'),
    
    # Réservation Pack Complet (sans ID ou avec ID)
    path('reservation/complet/', 
         views.reservation_pack_complet, 
         name='reservation_complet_base'),

    path('reservation/complet/<int:pack_id>/', 
         views.reservation_pack_complet, 
         name='reservation_complet_detail'),

    # Suppression de l'ancienne entrée :
    # path('reservation', views.reservation_pack, name='reservation') 
]