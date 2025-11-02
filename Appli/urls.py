from django.urls import path
from . import views

urlpatterns = [
    # Page d’accueil et pages statiques
    path('', views.home_page, name='accueil'),
    path('contact/', views.contact, name='contact'),
    path('services/', views.services, name='services'),
    path('about/', views.about, name='about'),
    path('mon_activite/', views.mon_activite, name='mon_activite'),

    # Réservation Pack 1 Jour
    path('reservation/jour/', views.reservation_pack_jour, name='reservation_jour_base'),
    path('reservation/jour/<int:pack_id>/', views.reservation_pack_jour, name='reservation_jour_detail'),

    # Réservation Pack Complet
    path('reservation/complet/', views.reservation_pack_complet, name='reservation_complet_base'),
    path('reservation/complet/<int:pack_id>/', views.reservation_pack_complet, name='reservation_complet_detail'),
]
