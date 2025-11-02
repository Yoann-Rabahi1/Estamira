from django.contrib import admin
from .models import (
    Ville,
    ActiviteJour,
    ActiviteComplet,
    PackJour,
    PackComplet,
    ReservationPackJour,
    ReservationPackComplet,
)

# ----------------------------------------------------
# 1. ADMIN DES COMPOSANTS DE BASE
# ----------------------------------------------------

@admin.register(Ville)
class VilleAdmin(admin.ModelAdmin):
    list_display = ('nom', 'description_generale')
    search_fields = ('nom',)
    ordering = ('nom',)
    list_per_page = 20


@admin.register(ActiviteJour)
class ActiviteJourAdmin(admin.ModelAdmin):
    list_display = ('nom_activite', 'ville', 'duree_texte')
    list_filter = ('ville',)
    search_fields = ('nom_activite', 'ville__nom')
    autocomplete_fields = ('ville',)
    list_per_page = 20
    ordering = ('ville', 'nom_activite')


@admin.register(ActiviteComplet)
class ActiviteCompletAdmin(admin.ModelAdmin):
    list_display = ('nom_activite', 'duree_estimee_heures')
    search_fields = ('nom_activite',)
    filter_horizontal = ('villes',)
    ordering = ('nom_activite',)
    list_per_page = 20


# ----------------------------------------------------
# 2. ADMIN DES PACKS
# ----------------------------------------------------

class ActiviteJourInline(admin.TabularInline):
    model = PackJour.activites.through
    extra = 1
    verbose_name = "Activité (1 jour)"
    verbose_name_plural = "Activités incluses (1 jour)"


class ActiviteCompletInline(admin.TabularInline):
    model = PackComplet.activites.through
    extra = 1
    verbose_name = "Activité complète"
    verbose_name_plural = "Activités incluses (séjour complet)"


@admin.register(PackJour)
class PackJourAdmin(admin.ModelAdmin):
    list_display = ('nom_pack', 'prix')
    list_filter = ('prix',)
    search_fields = ('nom_pack',)
    inlines = [ActiviteJourInline]
    exclude = ('activites',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom_pack', 'description', 'image_pack')
        }),
        ('Tarification', {
            'fields': ('prix',)
        }),
    )
    ordering = ('nom_pack',)
    list_per_page = 20


@admin.register(PackComplet)
class PackCompletAdmin(admin.ModelAdmin):
    list_display = ('nom_pack', 'prix')
    list_filter = ('prix',)
    search_fields = ('nom_pack',)
    inlines = [ActiviteCompletInline]
    exclude = ('activites',)
    fieldsets = (
        ('Informations générales', {
            'fields': ('nom_pack', 'description', 'image_pack')
        }),
        ('Tarification', {
            'fields': ('prix',)
        }),
    )
    ordering = ('nom_pack',)
    list_per_page = 20


# ----------------------------------------------------
# 3. ADMIN DES RÉSERVATIONS
# ----------------------------------------------------

@admin.register(ReservationPackJour)
class ReservationPackJourAdmin(admin.ModelAdmin):
    list_display = ('user', 'pack', 'date_debut', 'nb_personne', 'option_ryad', 'devise_paiement', 'date_reservation')
    list_filter = ('devise_paiement', 'option_ryad', 'pack')
    search_fields = ('user__email', 'pack__nom_pack')
    autocomplete_fields = ('user', 'pack')
    readonly_fields = ('date_reservation',)
    ordering = ('-date_reservation',)
    date_hierarchy = 'date_debut'
    list_per_page = 25


@admin.register(ReservationPackComplet)
class ReservationPackCompletAdmin(admin.ModelAdmin):
    list_display = (
        'user', 'pack', 'date_debut', 'date_fin',
        'nb_personne', 'option_ryad', 'option_restaurant',
        'devise_paiement', 'date_reservation'
    )
    list_filter = ('devise_paiement', 'option_ryad', 'option_restaurant', 'pack')
    search_fields = ('user__email', 'pack__nom_pack')
    autocomplete_fields = ('user', 'pack')
    readonly_fields = ('date_reservation',)
    ordering = ('-date_reservation',)
    date_hierarchy = 'date_debut'
    list_per_page = 25
