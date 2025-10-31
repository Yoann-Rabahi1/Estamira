from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_page, name='accueil'),
    path('contact', views.contact, name='contact'),
    path('services', views.services, name='services'),
    path('mon_activite', views.mon_activite, name='mon_activite'),
    path('about', views.about, name='about'),
    path('reservation', views.reservation_pack, name='reservation')
]