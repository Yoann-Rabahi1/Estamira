from django.contrib import admin
from .models import (
    Ville,
    ActiviteJour,
    PackJour,
    ReservationPackJour,
    ActiviteComplet,
    PackComplet,
    ReservationPackComplet,
    OptionReservation,
)

# -----------------------------
# VILLE
# -----------------------------
@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ['nom']
    search_fields = ['nom']
    ordering = ['nom']


# -----------------------------
# ACTIVITÉ JOUR
# -----------------------------
@admin.register(ActiviteJour)
class ActiviteJourAdmin(admin.ModelAdmin):
    list_display = ['nom', 'ville', 'duree']
    list_filter = ['ville']
    search_fields = ['nom', 'description']
    ordering = ['ville', 'nom']


# -----------------------------
# PACK JOUR
# -----------------------------
@admin.register(PackJour)
class PackJourAdmin(admin.ModelAdmin):
    list_display = ['nom', 'prix_mad', 'prix_eur', 'prix_usd']
    list_filter = ['activites']
    search_fields = ['nom', 'description']
    filter_horizontal = ['activites']
    ordering = ['nom']


# -----------------------------
# RÉSERVATION PACK JOUR
# -----------------------------
@admin.register(ReservationPackJour)
class ReservationPackJourAdmin(admin.ModelAdmin):
    list_display = ['pack', 'user', 'date', 'nb_personne', 'devise', 'date_reservation']
    list_filter = ['devise']
    search_fields = ['pack__nom', 'user__username']
    ordering = ['-date_reservation']


# -----------------------------
# ACTIVITÉ COMPLÈTE (segmentée par jour)
# -----------------------------
@admin.register(ActiviteComplet)
class ActiviteCompletAdmin(admin.ModelAdmin):
    list_display = ['nom', 'pack', 'jour_numero']
    list_filter = ['pack', 'jour_numero']
    search_fields = ['nom', 'description']
    ordering = ['pack', 'jour_numero', 'nom']


# -----------------------------
# PACK COMPLET
# -----------------------------
@admin.register(PackComplet)
class PackCompletAdmin(admin.ModelAdmin):
    list_display = ['nom', 'type_pack', 'duree_jours', 'prix_mad', 'prix_eur', 'prix_usd']
    list_filter = ['type_pack']
    search_fields = ['nom', 'description']
    ordering = ['nom']


# -----------------------------
# RÉSERVATION PACK COMPLET
# -----------------------------
@admin.register(ReservationPackComplet)
class ReservationPackCompletAdmin(admin.ModelAdmin):
    list_display = ['pack', 'user', 'date_debut', 'date_fin', 'nb_personne', 'devise', 'statut', 'date_reservation']
    list_filter = ['devise', 'statut']
    search_fields = ['pack__nom', 'user__username']
    ordering = ['-date_reservation']


# -----------------------------
# OPTIONS DE RÉSERVATION
# -----------------------------
@admin.register(OptionReservation)
class OptionReservationAdmin(admin.ModelAdmin):
    list_display = [
        'nom_option', 'type_option', 'quantite',
        'prix_mad', 'prix_eur', 'prix_usd',
        'reservation_complet', 'reservation_jour'
    ]
    list_filter = ['type_option']
    search_fields = ['nom_option']
    ordering = ['nom_option']
