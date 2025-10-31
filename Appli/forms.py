from django import forms
from django.utils import timezone
from .models import ReservationPack, Pack, MONNAIE_CHOICES

# =========================================================================
# FORMULAIRE DE RÉSERVATION DE PACK VOYAGE (STANDARD)
# =========================================================================

class ReservationPackForm(forms.ModelForm):
    """
    Formulaire simplifié pour la réservation d'un pack standard Estamira.
    Utilise ModelForm pour lier directement les champs à ReservationPack.
    """
    class Meta:
        model = ReservationPack
        # Les champs sont directement ceux de l'objet ReservationPack
        fields = [
            'pack',
            'nb_personne',
            'devise_paiement',
            'date_debut',
            'date_fin',
        ]
        
        widgets = {
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
                'required': 'required',
            }),
        }
        
        labels = {
            'pack': 'Choisissez votre Pack Voyage',
            'nb_personne': 'Nombre de personnes',
            'devise_paiement': 'Devise de paiement souhaitée',
            'date_debut': 'Date de début de séjour',
            'date_fin': 'Date de fin de séjour',
        }

    def __init__(self, *args, **kwargs):
        # Retrait de l'argument 'user' qui n'est plus nécessaire ici
        super().__init__(*args, **kwargs)
        
        # S'assure que le champ pack liste tous les packs disponibles
        self.fields['pack'].queryset = Pack.objects.all()
        self.fields['devise_paiement'].choices = MONNAIE_CHOICES

    def clean(self):
        cleaned_data = super().clean()
        date_debut = cleaned_data.get("date_debut")
        date_fin = cleaned_data.get("date_fin")
        
        # Validation des dates
        today = timezone.now().date()

        if date_debut and date_debut < today:
            self.add_error("date_debut", "La date de début ne peut pas être antérieure à aujourd’hui.")

        if date_fin and date_fin < today:
            self.add_error("date_fin", "La date de fin ne peut pas être antérieure à aujourd’hui.")

        # La date de fin doit être strictement après la date de début pour un séjour
        if date_debut and date_fin and date_fin <= date_debut:
            self.add_error("date_fin", "La date de fin doit être strictement postérieure à la date de début.")

        return cleaned_data