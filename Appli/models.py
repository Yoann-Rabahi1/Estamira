from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import datetime, timedelta

User = get_user_model()

# -----------------------------
# CHOIX
# -----------------------------

MONNAIE_CHOICES = [
    ("MAD", "Dirham marocain"),
    ("EUR", "Euro"),
    ("USD", "Dollar américain"),
]

TYPE_PACK_CHOICES = [
    ('AVENTURE', 'Aventure & Exploration'),
    ('LUXE', 'Séjour Luxe & Exclusif'),
    ('IMMERSION', 'Immersion Culturelle & Tradition'),
    ('DETENTE', 'Détente & Bien-être'),
    ('SUR_MESURE', 'Pack Sur Mesure'),
]

TYPE_RESTAURANT_CHOICES = [
    ('GASTRONOMIQUE', 'Gastronomique'),
    ('TRADITIONNEL', 'Cuisine Marocaine'),
    ('FUSION', 'Fusion / Moderne'),
    ('VEGETARIEN', 'Végétarien'),
]

STATUT = [
    ('demande', 'Demande effectuée'),
    ('en cours', 'En cours de traitement'),
    ('annulé', 'Annulée'),
    ('traitée', 'Traitée'),
    ('validée', 'Validée'),
]

def default_end_date():
    return datetime.now().date() + timedelta(days=3)

# -----------------------------
# VILLE
# -----------------------------

class Ville(models.Model):
    nom = models.CharField(max_length=60, unique=True)
    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='img_villes/', blank=True, null=True)

    def __str__(self):
        return self.nom

# -----------------------------
# ACTIVITÉS JOUR
# -----------------------------

class ActiviteJour(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name="activites_jour")
    duree = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='img_activites_jour/', blank=True, null=True)

    def __str__(self):
        return f"{self.nom} ({self.ville.nom})"

# -----------------------------
# PACK JOUR
# -----------------------------

class PackJour(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)

    prix_mad = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    prix_eur = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    prix_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    activites = models.ManyToManyField(ActiviteJour, related_name="packs_jour")
    image = models.ImageField(upload_to='img_packs_jour/', blank=True, null=True)

    def get_prix_par_devise(self, devise):
        return {
            "MAD": self.prix_mad,
            "EUR": self.prix_eur,
            "USD": self.prix_usd,
        }.get(devise, self.prix_mad)

    def __str__(self):
        return self.nom


# -----------------------------
# RÉSERVATION JOUR
# -----------------------------

def default_pack_jour():
    pack = PackJour.objects.first()
    if pack:
        return pack.id
    return None  # ou lève une exception personnalisée si tu veux forcer la création


class ReservationPackJour(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pack = models.ForeignKey(PackJour, on_delete=models.CASCADE, default=default_pack_jour)
    nb_personne = models.PositiveIntegerField(default=1)
    devise = models.CharField(max_length=10, choices=MONNAIE_CHOICES, default="MAD")
    date = models.DateField(default=datetime.now)
    date_reservation = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.pack.nom} - {self.date}"

# -----------------------------
# ACTIVITÉS COMPLET
# -----------------------------

class ActiviteComplet(models.Model):
    nom = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    jour_numero = models.PositiveIntegerField(default=1)
    pack = models.ForeignKey('PackComplet', on_delete=models.CASCADE, related_name="activites")
    villes = models.ManyToManyField(Ville, related_name='activites_complet', blank=True)
    image = models.ImageField(upload_to='img_activites_complet/', blank=True, null=True)

    def __str__(self):
        return f"Jour {self.jour_numero} - {self.nom}"

# -----------------------------
# PACK COMPLET
# -----------------------------

def default_pack_complet():
    pack = PackComplet.objects.first()
    if pack:
        return pack.id
    return None

class PackComplet(models.Model):
    nom = models.CharField(max_length=200)
    type_pack = models.CharField(max_length=20, choices=TYPE_PACK_CHOICES, default='SUR_MESURE')
    duree_jours = models.PositiveIntegerField(default=3)
    duree_nuits = models.PositiveIntegerField(default=2)

    prix_mad = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    prix_eur = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)
    prix_usd = models.DecimalField(max_digits=10, decimal_places=2, default=0.0)

    description = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='img_packs_complet/', blank=True, null=True)

    def get_prix_par_devise(self, devise):
        return {
            "MAD": self.prix_mad,
            "EUR": self.prix_eur,
            "USD": self.prix_usd,
        }.get(devise, self.prix_mad)

    def __str__(self):
        return self.nom


# -----------------------------
# RÉSERVATION COMPLET
# -----------------------------

class ReservationPackComplet(models.Model):
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    pack = models.ForeignKey(PackComplet, on_delete=models.CASCADE,default=default_pack_complet)
    nb_personne = models.PositiveIntegerField(default=1)
    devise = models.CharField(max_length=10, choices=MONNAIE_CHOICES, default="MAD")
    date_debut = models.DateField(default=datetime.now)
    date_fin = models.DateField(default=default_end_date)
    date_reservation = models.DateTimeField(default=timezone.now)

    statut = models.CharField(max_length=20, choices=STATUT, default='demande')

    def __str__(self):
        return f"{self.pack.nom} - {self.date_debut} → {self.date_fin}"

# -----------------------------
# OPTIONS
# -----------------------------

class OptionReservation(models.Model):
    reservation_complet = models.ForeignKey(
        ReservationPackComplet,
        on_delete=models.CASCADE,
        related_name="options",
        null=True,
        blank=True
    )
    reservation_jour = models.ForeignKey(
        ReservationPackJour,
        on_delete=models.CASCADE,
        related_name="options",
        null=True,
        blank=True
    )

    nom_option = models.CharField(max_length=100)
    type_option = models.CharField(
        max_length=50,
        choices=TYPE_RESTAURANT_CHOICES,
        blank=True,
        null=True
    )

    prix_mad = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    prix_eur = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)
    prix_usd = models.DecimalField(max_digits=8, decimal_places=2, default=0.0)

    quantite = models.PositiveIntegerField(default=1)

    def get_prix_par_devise(self, devise):
        return {
            "MAD": self.prix_mad,
            "EUR": self.prix_eur,
            "USD": self.prix_usd,
        }.get(devise, self.prix_mad)

    def __str__(self):
        return f"{self.nom_option} x{self.quantite}"

