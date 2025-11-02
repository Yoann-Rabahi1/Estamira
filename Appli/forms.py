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
    'devise': forms.Select(attrs={"class": "form-select rounded-3 shadow-sm"}),
    'date': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control rounded-3 shadow-sm',
        'required': 'required',
    }),
    'date_debut': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control rounded-3 shadow-sm',
        'required': 'required',
    }),
    'date_fin': forms.DateInput(attrs={
        'type': 'date',
        'class': 'form-control rounded-3 shadow-sm',
    }),
}

COMMON_LABELS = {
    'pack': 'Choisissez votre Pack Voyage',
    'nb_personne': 'Nombre de personnes',
    'devise': 'Devise de paiement souhaitée',
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
            'devise',
            'date',
        ]

        widgets = {
            'pack': COMMON_WIDGETS['pack'],
            'nb_personne': COMMON_WIDGETS['nb_personne'],
            'devise': COMMON_WIDGETS['devise'],
            'date': COMMON_WIDGETS['date'],
        }

        labels = {
            'pack': COMMON_LABELS['pack'],
            'nb_personne': COMMON_LABELS['nb_personne'],
            'devise': COMMON_LABELS['devise'],
            'date': 'Date de l’activité (jour unique)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pack'].queryset = PackJour.objects.all()
        self.fields['devise'].choices = MONNAIE_CHOICES

    def clean_date(self):
        date = self.cleaned_data.get("date")
        today = timezone.now().date()
        if date and date < today:
            raise forms.ValidationError("La date de l’activité ne peut pas être antérieure à aujourd’hui.")
        return date


# =========================================================================
# FORMULAIRE POUR LES PACKS COMPLETS
# =========================================================================

class ReservationPackCompletForm(forms.ModelForm):
    """Formulaire pour la réservation de packs complets (plusieurs jours)."""

    class Meta:
        model = ReservationPackComplet
        fields = [
            'pack',
            'nb_personne',
            'devise',
            'date_debut',
            'date_fin',
        ]

        widgets = {
            'pack': COMMON_WIDGETS['pack'],
            'nb_personne': COMMON_WIDGETS['nb_personne'],
            'devise': COMMON_WIDGETS['devise'],
            'date_debut': COMMON_WIDGETS['date_debut'],
            'date_fin': COMMON_WIDGETS['date_fin'],
        }

        labels = {
            'pack': COMMON_LABELS['pack'],
            'nb_personne': COMMON_LABELS['nb_personne'],
            'devise': COMMON_LABELS['devise'],
            'date_debut': 'Date de début du séjour',
            'date_fin': 'Date de fin du séjour',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['pack'].queryset = PackComplet.objects.all()
        self.fields['devise'].choices = MONNAIE_CHOICES

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")
        today = timezone.now().date()

        if date_debut and date_debut < today:
            self.add_error("date_debut", "La date de début ne peut pas être antérieure à aujourd’hui.")
        if date_fin and date_fin < today:
            self.add_error("date_fin", "La date de fin ne peut pas être antérieure à aujourd’hui.")
        if date_debut and date_fin and date_fin <= date_debut:
            self.add_error("date_fin", "La date de fin doit être strictement postérieure à la date de début.")

        return cleaned_data
