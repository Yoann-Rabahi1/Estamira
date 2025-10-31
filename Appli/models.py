import os
from django.db import models
from django.contrib.auth import get_user_model
from django.db.models import Sum, Avg

# Récupère le modèle d'utilisateur personnalisé (User)
User = get_user_model()


# ----------------------------------------------------
# 1. CHOIX STATIQUES
# ----------------------------------------------------

STATUT = [
    ('demande','Demande effectuée'),
    ('en cours', 'En cours de traitement'),
    ('annulé', 'Demande Annulée'),
    ('traitée', 'Demande traitée'),
    ('validée', 'Transaction effectuée')
]

MONNAIE_CHOICES = [
    ("EUR", "€ (Euros)"),
    ("MAD", "DH (Dirhams Marocains)"),
    ("DOLLAR", "$ (Dollars)")
]

# Les durées fixes proposées par Estamira
DUREE_CHOICES = [
    (1, '1 jour'),
    (3, '3 jours'),
    (5, '5 jours'),
    (8, '8 jours'),
    (10, '10 jours'),
]

# ----------------------------------------------------
# 2. MODÈLES DE STRUCTURE ET D'EXPÉRIENCE (Vos "Tabs" de contenu)
# ----------------------------------------------------

class Ville(models.Model):
    """TAB : VILLE (Destination principale)"""
    nom = models.CharField(max_length=60, unique=True)
    description_generale = models.TextField(blank=True, null=True)
    image_banniere = models.ImageField(upload_to='img_villes/', null=True, blank=True)

    def __str__(self):
        return self.nom
    
    class Meta:
        verbose_name_plural = "Villes (Destinations)"


class Restaurant(models.Model):
    """TAB : RESTAURANT (Expérience recommandée/incluse)"""
    nom = models.CharField(max_length=100)
    # FK vers la Ville
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='restaurants')
    type_cuisine = models.CharField(max_length=50)
    prix_moyen_eur = models.FloatField(default=0.0, help_text="Coût moyen estimé par personne (à titre indicatif).")

    def __str__(self):
        return self.nom


class Activite(models.Model):
    """TAB : ACTIVITÉ (Les briques de base incluses dans les Packs)"""
    nom_activite = models.CharField(max_length=60)
    # FK vers la Ville
    ville = models.ForeignKey(Ville, on_delete=models.SET_NULL, null=True, blank=True, related_name='activites') 
    description = models.TextField(blank=True, null=True)
    duree_texte = models.CharField(max_length=50, blank=True, null=True, help_text="Ex: 2 heures, demi-journée...")

    def __str__(self):
        return self.nom_activite


class Pack(models.Model):
    """TAB : PACK (Le produit final assemblé et STANDARD)"""
    titre = models.CharField(max_length=150)
    resume_inspirant = models.TextField(max_length=500, blank=True, null=True)
    
    # Liens
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, related_name='packs') 
    activites = models.ManyToManyField(Activite, related_name='packs', help_text="Liste des activités incluses dans ce pack.") 
    restaurants = models.ManyToManyField(Restaurant, related_name='packs', blank=True, help_text="Liste des restaurants visités ou recommandés.")
    
    # Attributs pour le pack
    duree_standard_jours = models.PositiveSmallIntegerField(choices=DUREE_CHOICES, default=3)
    prix_par_personne_euros = models.FloatField(default=0.0, help_text="Prix par personne pour la durée standard du pack.")
    
    date_creation = models.DateField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.titre} ({self.ville.nom}, {self.duree_standard_jours}J)"
    
    class Meta:
        ordering = ['ville', 'titre']


class DescriptionJournaliere(models.Model):
    """Détail "Jour par Jour" du contenu du Pack (Contenu imbriqué sous le Pack)"""
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, related_name='jours')
    numero_jour = models.PositiveSmallIntegerField()
    titre = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return f"{self.pack.titre} - Jour {self.numero_jour}"
    
    class Meta:
        unique_together = ('pack', 'numero_jour')
        ordering = ['numero_jour']


class Image(models.Model):
    """Gestion des images pour les entités du site (Packs, Activités, Villes)"""
    pack = models.ForeignKey(Pack, on_delete=models.CASCADE, null=True, blank=True, related_name="images") 
    activite = models.ForeignKey(Activite, on_delete=models.CASCADE, null=True, blank=True, related_name="images_activite") 
    ville = models.ForeignKey(Ville, on_delete=models.CASCADE, null=True, blank=True, related_name="images_ville")
    fichier = models.ImageField(upload_to="img/", null=True, blank=True)
    caption = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.caption or f"Image {self.id}"


# ----------------------------------------------------
# 3. MODÈLES DE RÉSERVATION
# ----------------------------------------------------

class ReservationBase(models.Model):
    """Classe abstraite pour toutes les réservations"""
    date_demande = models.DateTimeField(auto_now_add=True)
    statut = models.CharField(choices=STATUT, max_length=60, default='demande')
    date_traitement = models.DateTimeField(null=True, blank=True) # Date du dernier changement de statut
    nb_personne = models.SmallIntegerField()
    montant_total = models.FloatField(default=0.0)
    devise_paiement = models.CharField(max_length=20, choices=MONNAIE_CHOICES, null=True, blank=True)
    type_virement = models.CharField(max_length=60, blank=True, null=True)
    
    # Liens utilisateurs
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="%(class)s_reservations")
    traiter_par = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name="%(class)s_traites")
    
    lien_de_paiement = models.URLField(max_length=300, blank=True, null=True)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        """Filtre les utilisateurs pour 'traiter_par' afin de n'afficher que le personnel."""
        if db_field.name == "traiter_par":
            # N'affiche que les utilisateurs avec des droits d'administration (is_staff)
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    @property
    def paiement_autorise(self):
        """Vrai si le statut est 'traitée', indiquant que l'admin a envoyé le devis/lien."""
        return self.statut == "traitée"

    class Meta:
        abstract = True
        ordering = ['-date_demande']


class ReservationPack(ReservationBase):
    """Réservation finale d'un Pack Estamira STANDARD"""
    # FK vers le Pack standard
    pack = models.ForeignKey(Pack, null=True, on_delete=models.SET_NULL) 
    
    # Les dates spécifiques de la réservation par le client
    date_debut = models.DateField(null=True, blank=True) 
    date_fin = models.DateField(null=True, blank=True)
    
    @property
    def duree_reservee(self):
        """Calcule la durée de la réservation en jours."""
        if self.date_debut and self.date_fin:
            return max((self.date_fin - self.date_debut).days, 1)
        return self.pack.duree_standard_jours if self.pack else 0

    def save(self, *args, **kwargs):
        # Logique de calcul simple du prix (peut être affinée plus tard)
        if self.pack:
            prix_base = self.pack.prix_par_personne_euros 
            # Le prix peut être ajusté en fonction de la durée ou des dates, 
            # mais pour l'instant, nous utilisons le prix standard.
            self.montant_total = round(prix_base * self.nb_personne, 2)
        
        super().save(*args, **kwargs)

    def __str__(self):
        nom_pack = self.pack.titre if self.pack else "Pack Supprimé"
        return f"Réservation {nom_pack} par {getattr(self.user, 'email', 'Inconnu')}"