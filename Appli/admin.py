from django.contrib import admin
from django.contrib.auth import get_user_model
from django.utils.html import format_html
from django.utils import timezone

# Importez la fonction de notification
# Assurez-vous que ce chemin est correct : appli/notification/email.py
from .notification.email import notifier_admins_reservation_pack 

from .models import (
    Ville, Activite, Restaurant, 
    Pack, DescriptionJournaliere, Image,
    ReservationPack
)

User = get_user_model()


# -----------------------------------------------------------------
# 1. ADMINS INLINES (Modèles imbriqués)
# -----------------------------------------------------------------

class ImageInline(admin.TabularInline):
    """Permet de lier des images à une Ville/Activité/Pack directement."""
    model = Image
    extra = 1
    fields = ('fichier', 'caption', 'image_preview')
    readonly_fields = ('image_preview',)
    verbose_name_plural = "Galerie d'Images"

    def image_preview(self, obj):
        if obj.fichier:
            return format_html('<img src="{}" style="height: 100px;" />', obj.fichier.url)
        return ""
    image_preview.short_description = "Aperçu"


class DescriptionJournaliereInline(admin.TabularInline):
    """Permet de gérer les jours du pack directement dans la page du Pack."""
    model = DescriptionJournaliere
    extra = 1
    fields = ('numero_jour', 'titre', 'description')
    ordering = ('numero_jour',)
    verbose_name = "Jour"
    verbose_name_plural = "Itinéraire Jour par Jour"


# -----------------------------------------------------------------
# 2. ADMINS DES MODÈLES DE CONTENU (Vos "Tabs" de Produits)
# -----------------------------------------------------------------

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'compte_packs', 'compte_restaurants', 'afficher_image_banniere')
    search_fields = ('nom',)
    inlines = [ImageInline]

    def compte_packs(self, obj):
        return obj.packs.count()
    compte_packs.short_description = "Nb Packs"

    def compte_restaurants(self, obj):
        return obj.restaurants.count()
    compte_restaurants.short_description = "Nb Restaurants"

    def afficher_image_banniere(self, obj):
        if obj.image_banniere:
            return format_html('<img src="{}" width="50" height="auto" />', obj.image_banniere.url)
        return "Pas d'image"
    afficher_image_banniere.short_description = "Bannière"


@admin.register(Activite)
class ActiviteAdmin(admin.ModelAdmin):
    list_display = ('nom_activite', 'ville', 'duree_texte', 'compte_packs_lies')
    search_fields = ('nom_activite', 'description')
    list_filter = ('ville',)
    inlines = [ImageInline]

    def compte_packs_lies(self, obj):
        return obj.packs.count()
    compte_packs_lies.short_description = "Utilisé dans (Nb Packs)"


@admin.register(Restaurant)
class RestaurantAdmin(admin.ModelAdmin):
    list_display = ('nom', 'ville', 'type_cuisine', 'prix_moyen_eur', 'compte_packs_lies')
    search_fields = ('nom', 'ville__nom', 'type_cuisine')
    list_filter = ('ville', 'type_cuisine')

    def compte_packs_lies(self, obj):
        return obj.packs.count()
    compte_packs_lies.short_description = "Utilisé dans (Nb Packs)"


@admin.register(Pack)
class PackAdmin(admin.ModelAdmin):
    list_display = ('titre', 'ville', 'duree_standard_jours', 'prix_par_personne_euros', 'date_creation')
    search_fields = ('titre', 'resume_inspirant', 'ville__nom')
    list_filter = ('ville', 'duree_standard_jours')
    filter_horizontal = ('activites', 'restaurants')
    inlines = [DescriptionJournaliereInline, ImageInline]
    
    fieldsets = (
        ("Informations Générales", {
            'fields': ('titre', 'ville', 'duree_standard_jours')
        }),
        ("Tarification", {
            'fields': ('prix_par_personne_euros',)
        }),
        ("Contenu Descriptif", {
            'fields': ('resume_inspirant',)
        }),
        ("Contenu Inclus", {
            'fields': ('activites', 'restaurants'),
        }),
    )
    
    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "user":
            kwargs["queryset"] = User.objects.filter(is_staff=True)
        return super().formfield_for_foreignkey(db_field, request, **kwargs)


# -----------------------------------------------------------------
# 3. ADMIN DES RÉSERVATIONS (Gestion du Flux Client)
# -----------------------------------------------------------------

@admin.register(ReservationPack)
class ReservationPackAdmin(admin.ModelAdmin):
    list_display = ('id', 'pack', 'user_email', 'date_demande', 'nb_personne', 'montant_total', 'statut', 'traiter_par')
    list_filter = ('statut', 'date_demande', 'pack__ville')
    search_fields = ('user__email', 'pack__titre', 'id')
    date_hierarchy = 'date_demande'
    readonly_fields = ('montant_total', 'date_demande', 'user', 'duree_reservee')

    fieldsets = (
        ("Détails du Client et Pack", {
            'fields': ('user', 'pack', 'nb_personne', 'date_debut', 'date_fin', 'duree_reservee'),
        }),
        ("Tarification et Paiement", {
            'fields': ('montant_total', 'devise_paiement', 'type_virement', 'lien_de_paiement'),
        }),
        ("Suivi Administratif", {
            'fields': ('statut', 'traiter_par', 'date_traitement'),
        }),
    )

    def user_email(self, obj):
        return obj.user.email if obj.user else "N/A"
    user_email.short_description = "Client (Email)"

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name == "traiter_par":
            kwargs["queryset"] = User.objects.filter(is_staff=True) 
        return super().formfield_for_foreignkey(db_field, request, **kwargs)

    # Logique pour la traçabilité et la notification Admin
    def save_model(self, request, obj, form, change):
        is_new = not obj.pk

        if change:
            if 'statut' in form.changed_data or not obj.traiter_par:
                obj.date_traitement = timezone.now()
                obj.traiter_par = request.user 

        super().save_model(request, obj, form, change)

        # Notifie les admins uniquement lors de la création d'une nouvelle réservation
        if is_new:
            notifier_admins_reservation_pack(obj)