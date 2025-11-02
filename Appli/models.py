import os
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from datetime import date, timedelta, datetime


User = get_user_model()


# ----------------------------------------------------
# 1. CHOIX STATIQUES
# ----------------------------------------------------

STATUT = [
    ('demande', 'Demande effectuée'),
    ('en cours', 'En cours de traitement'),
    ('annulé', 'Demande annulée'),
    ('traitée', 'Demande traitée'),
    ('validée', 'Transaction effectuée'),
]

MONNAIE_CHOICES = [
    ("EUR", "€ (Euros)"),
    ("MAD", "DH (Dirhams Marocains)"),
    ("DOLLAR", "$ (Dollars)"),
]

DUREE_CHOICES_COMPLET = [
    (3, '3 jours'),
    (5, '5 jours'),
    (8, '8 jours'),
    (10, '10 jours'),
]

TYPE_PACK_CHOICES = [
    ('AVENTURE', 'Aventure & Exploration'),
    ('LUXE', 'Séjour Luxe & Exclusif'),
    ('IMMERSION', 'Immersion Culturelle & Tradition'),
    ('DETENTE', 'Détente & Bien-être'),
    ('SUR_MESURE', 'Pack Sur Mesure (Générique)'),
]

TYPE_RESTAURANT_CHOICES = [
    ('GASTRONOMIQUE', 'Gastronomique / Haute Cuisine'),
    ('TRADITIONNEL', 'Cuisine Marocaine Traditionnelle'),
    ('FUSION', 'Fusion / Moderne'),
    ('VEGETARIEN', 'Végétarien / Santé'),
]


# ----------------------------------------------------
# 2. MODÈLES DE STRUCTURE ET D’EXPÉRIENCE
# ----------------------------------------------------

class Ville(models.Model):
    nom = models.CharField(max_length=60, unique=True)
    description_generale = models.TextField(blank=True, null=True)
    image_banniere = models.ImageField(upload_to='img_villes/', null=True, blank=True)

    def __str__(self):
        return self.nom

    class Meta:
        verbose_name_plural = "Villes (Destinations)"


class ActiviteJour(models.Model):
    """
    Activité d'une seule journée, rattachée à une ville.
    Exemple : visite guidée, excursion d’une journée, etc.
    """
    nom_activite = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name="activites_jour")
    duree_texte = models.CharField(max_length=100, blank=True, null=True)
    image_principale = models.ImageField(upload_to='img_activites_jour/', null=True, blank=True)

    def __str__(self):
        return f"{self.nom_activite} ({self.ville.nom})"

    class Meta:
        verbose_name = "Activité 1 Jour"
        verbose_name_plural = "Activités 1 Jour"
        ordering = ['ville', 'nom_activite']


class ActiviteComplet(models.Model):
    """
    Activité de séjour complet (3 à 10 jours),
    pouvant inclure plusieurs villes ou excursions.
    """
    nom_activite = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    duree_estimee_heures = models.PositiveIntegerField(default=4)
    villes = models.ManyToManyField(Ville, related_name='activites_complets', blank=True)
    image_principale = models.ImageField(upload_to='img_activites_complets/', null=True, blank=True)

    def __str__(self):
        return self.nom_activite

    class Meta:
        verbose_name = "Activité Pack Complet"
        verbose_name_plural = "Activités Pack Complet"
        ordering = ['nom_activite']


# ============================================================
# MODELES DE PACKS
# ============================================================

class PackJour(models.Model):
    """
    Pack d'une journée (activité courte).
    """
    nom_pack = models.CharField(max_length=200, blank=True, null=True)
    prix = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    activites = models.ManyToManyField(ActiviteJour, related_name="packs_jour", blank=True)
    description = models.TextField(blank=True, null=True)
    image_pack = models.ImageField(upload_to='img_packs_jour/', null=True, blank=True)

    def __str__(self):
        return self.nom_pack

    class Meta:
        verbose_name = "Pack 1 Jour"
        verbose_name_plural = "Packs 1 Jour"
        ordering = ['nom_pack']


class PackComplet(models.Model):
    """
    Pack de plusieurs jours, regroupant plusieurs activités longues.
    """
    nom_pack = models.CharField(max_length=200, null=True, blank=True)
    prix = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    activites = models.ManyToManyField(ActiviteComplet, related_name="packs_complets", blank=True)
    description = models.TextField(blank=True, null=True)
    image_pack = models.ImageField(upload_to='img_packs_complets/', null=True, blank=True)

    def __str__(self):
        return self.nom_pack

    class Meta:
        verbose_name = "Pack Complet"
        verbose_name_plural = "Packs Complets"
        ordering = ['nom_pack']


# ============================================================
# MODELES DE RÉSERVATION
# ============================================================

def default_end_date():
    return date.today() + timedelta(days=3)

class ReservationPackJour(models.Model):
    """
    Réservation d’un pack d’une journée.
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservations_pack_jour")
    pack = models.ForeignKey(PackJour, on_delete=models.CASCADE)
    nb_personne = models.PositiveIntegerField(default=1)
    devise_paiement = models.CharField(max_length=10, choices=MONNAIE_CHOICES, default="MAD")
    date_debut = models.DateField(default=datetime.now)
    option_ryad = models.BooleanField(default=False)
    date_reservation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Réservation {self.pack.nom_pack} ({self.date_debut})"

    class Meta:
        verbose_name = "Réservation Pack 1 Jour"
        verbose_name_plural = "Réservations Pack 1 Jour"
        ordering = ['-date_reservation']


class ReservationPackComplet(models.Model):
    """
    Réservation d’un pack complet (plusieurs jours).
    """
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="reservations_pack_complet")
    pack = models.ForeignKey(PackComplet, on_delete=models.CASCADE, )
    nb_personne = models.PositiveIntegerField(default=1)
    devise_paiement = models.CharField(max_length=10, choices=MONNAIE_CHOICES, default="MAD")
    date_debut = models.DateField(default=datetime.now)
    date_fin = models.DateField(default=default_end_date)
    option_ryad = models.BooleanField(default=False)
    option_restaurant = models.BooleanField(default=False)
    date_reservation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Réservation {self.pack.nom_pack} ({self.date_debut} → {self.date_fin})"

    class Meta:
        verbose_name = "Réservation Pack Complet"
        verbose_name_plural = "Réservations Pack Complet"
        ordering = ['-date_reservation']
