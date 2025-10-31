import string
from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User

class CustomUserCreationForm(UserCreationForm):
    prenom = forms.CharField(
        max_length=60,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Prénom", "class": "form-control"})
    )
    nom = forms.CharField(
        max_length=60,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Nom", "class": "form-control"})
    )
    tel = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Téléphone", "class": "form-control"})
    )


    class Meta:
        model = User
        fields = ['email', 'prenom', 'nom', 'tel', 'password1', 'password2']
        error_messages = {
            'email': {
                'unique': "Cette adresse email est déjà utilisée. Essayez de vous connecter ou utilisez une autre.",
                'invalid': "Veuillez entrer une adresse email valide.",
                'required': "L'adresse email est obligatoire.",
            },
            'tel': {
                'unique': "Ce numéro de téléphone est déjà associé à un compte.",
            },
        }

    def clean_prenom(self):
        prenom = self.cleaned_data.get('prenom')
        if any(char.isdigit() for char in prenom):
            raise forms.ValidationError("Le prénom ne doit pas contenir de chiffres.")
        return prenom

    def clean_nom(self):
        nom = self.cleaned_data.get('nom')
        if any(char.isdigit() for char in nom):
            raise forms.ValidationError("Le nom ne doit pas contenir de chiffres.")
        return nom

    def clean_tel(self):
        tel = self.cleaned_data.get('tel')
        if not tel.isdigit():
            raise forms.ValidationError("Le numéro de téléphone ne doit contenir que des chiffres.")
        if User.objects.filter(tel=tel).exists():
            raise forms.ValidationError("Ce numéro est déjà associé à un compte.")
        return tel

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Cette adresse email est déjà utilisée.")
        return email

    def clean_password1(self):
        password = self.cleaned_data.get('password1')
        prenom = self.cleaned_data.get('prenom')

        if not password:
            return password
        if prenom and prenom.lower() in password.lower():
            raise forms.ValidationError("Le mot de passe ne doit pas contenir le prénom.")
        if len(password) < 8:
            raise forms.ValidationError("Le mot de passe doit contenir au minimum 8 caractères.")
        if not any(c.islower() for c in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une minuscule.")
        if not any(c.isupper() for c in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins une majuscule.")
        if not any(c.isdigit() for c in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un chiffre.")
        if not any(c in string.punctuation for c in password):
            raise forms.ValidationError("Le mot de passe doit contenir au moins un caractère spécial.")

        return password

    def save(self, commit=True):
        user = super().save(commit=False)
        user.prenom = self.cleaned_data['prenom']
        user.nom = self.cleaned_data['nom']
        user.tel = self.cleaned_data['tel']
        user.first_name = user.prenom
        user.last_name = user.nom

        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ['email', 'prenom', 'nom', 'tel', 'is_staff', 'is_superuser']