from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import user_passes_test
from .forms import CustomUserCreationForm
from .notifications.email import notifier_creation_nouvel_utilisateur

# ---------------------------
# Inscription publique
# ---------------------------
def signup_view(request):
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
           # notifier_creation_nouvel_utilisateur(user)
            messages.success(request, "Inscription réussie ! Bienvenue chez Maison Elba.")
            return render(request, "registration/signup_success.html", {"user": user})
        else:
            messages.error(request, "Merci de corriger les erreurs ci-dessous.")
    else:
        form = CustomUserCreationForm()
    return render(request, "registration/signup.html", {"form": form})


# ---------------------------
# Déconnexion
# ---------------------------
def custom_logout(request):
    logout(request)
    return redirect('login')


# ---------------------------
# Vérification que l'utilisateur est admin
# ---------------------------
def is_admin(user):
    return user.is_superuser