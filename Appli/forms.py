from django import forms
from django.utils import timezone
from .models import (
    PackJour,
    PackComplet,
    ReservationPackJour,
    ReservationPackComplet,
    MONNAIE_CHOICES
)

# ----------------------------------------------------
# WIDGETS ET LABELS COMMUNS
# ----------------------------------------------------

COMMON_WIDGETS = {
    'pack': forms.Select(attrs={"class": "form-select rounded-3 shadow-sm"}),
    'nb_personne': forms.NumberInput(attrs={
        "class": "form-control rounded-3 shadow-sm",
        "min": 1
    }),
    'devise_paiement': forms.Select(attrs={"class": "form-select rounded-3 shadow-sm"}),
    'date_debut': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control rounded-3 shadow-sm',
        'required': 'required',
    }),
    'date_fin': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control rounded-3 shadow-sm',
    }),
    'option_ryad': forms.CheckboxInput(attrs={"class": "form-check-input"}),
    'option_restaurant': forms.CheckboxInput(attrs={"class": "form-check-input"}),
}

COMMON_LABELS = {
    'pack': 'Choisissez votre Pack Voyage',
    'nb_personne': 'Nombre de personnes',
    'devise_paiement': 'Devise de paiement souhaitée',
    'option_ryad': 'Ajouter l’option Ryad (Hébergement)',
    'option_restaurant': 'Ajouter l’option Restaurant',
}

# =========================================================================
# FORMULAIRE POUR LES PACKS D’UNE JOURNÉE
# =========================================================================

class ReservationPackJourForm(forms.ModelForm):
    """Formulaire pour la réservation de packs d'une journée."""
    
    class Meta:
        model = ReservationPackJour
        fields = [
            'pack',
            'nb_personne',
            'devise_paiement',
            'date_debut',
            'option_ryad',
        ]
        
        widgets = {
            'pack': COMMON_WIDGETS['pack'],
            'nb_personne': COMMON_WIDGETS['nb_personne'],
            'devise_paiement': COMMON_WIDGETS['devise_paiement'],
            'date_debut': COMMON_WIDGETS['date_debut'],
            'option_ryad': COMMON_WIDGETS['option_ryad'],
        }
        
        labels = {
            'pack': COMMON_LABELS['pack'],
            'nb_personne': COMMON_LABELS['nb_personne'],
            'devise_paiement': COMMON_LABELS['devise_paiement'],
            'date_debut': 'Date de l’activité (jour unique)',
            'option_ryad': COMMON_LABELS['option_ryad'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pack'].queryset = PackJour.objects.all()
        self.fields['devise_paiement'].choices = MONNAIE_CHOICES
        self.fields['option_ryad'].required = False

    def clean_date_debut(self):
        date_debut = self.cleaned_data.get("date_debut")
        today = timezone.now().date()
        if date_debut and date_debut < today:
            raise forms.ValidationError("La date de l’activité ne peut pas être antérieure à aujourd’hui.")
        return date_debut


# =========================================================================
# FORMULAIRE POUR LES PACKS COMPLETS (3 jours et +)
# =========================================================================

class ReservationPackCompletForm(forms.ModelForm):
    """Formulaire pour la réservation de packs complets (plusieurs jours)."""
    
    class Meta:
        model = ReservationPackComplet
        fields = [
            'pack',
            'nb_personne',
            'devise_paiement',
            'date_debut',
            'date_fin',
            'option_ryad',
            'option_restaurant',
        ]
        
        widgets = {
            'pack': COMMON_WIDGETS['pack'],
            'nb_personne': COMMON_WIDGETS['nb_personne'],
            'devise_paiement': COMMON_WIDGETS['devise_paiement'],
            'date_debut': COMMON_WIDGETS['date_debut'],
            'date_fin': COMMON_WIDGETS['date_fin'],
            'option_ryad': COMMON_WIDGETS['option_ryad'],
            'option_restaurant': COMMON_WIDGETS['option_restaurant'],
        }
        
        labels = {
            'pack': COMMON_LABELS['pack'],
            'nb_personne': COMMON_LABELS['nb_personne'],
            'devise_paiement': COMMON_LABELS['devise_paiement'],
            'date_debut': 'Date de début du séjour',
            'date_fin': 'Date de fin du séjour',
            'option_ryad': COMMON_LABELS['option_ryad'],
            'option_restaurant': COMMON_LABELS['option_restaurant'],
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pack'].queryset = PackComplet.objects.all()
        self.fields['devise_paiement'].choices = MONNAIE_CHOICES
        self.fields['option_ryad'].required = False
        self.fields['option_restaurant'].required = False

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")
        today = timezone.now().date()

        # Validation chronologique
        if date_debut and date_debut < today:
            self.add_error("date_debut", "La date de début ne peut pas être antérieure à aujourd’hui.")
        if date_fin and date_fin < today:
            self.add_error("date_fin", "La date de fin ne peut pas être antérieure à aujourd’hui.")
        if date_debut and date_fin and date_fin <= date_debut:
            self.add_error("date_fin", "La date de fin doit être strictement postérieure à la date de début.")

        return cleaned_data
