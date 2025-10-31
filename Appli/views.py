from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.views import View
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from .forms import ReservationPackForm # Nous supposons que les autres formulaires sont supprimés de forms.py
from .models import ( 
    ReservationPack, 
    Pack,
    Ville, # Ajout de Ville pour la page d'accueil si vous voulez filtrer par ville
    Activite # Gardons Activite pour une potentielle vue de détail
)
from django.contrib import messages

# Importation des fonctions de notification nécessaires
from .notification.email import (
    notifier_admins_reservation_pack,
    notifier_utilisateur_reservation_pack
)


# -----------------------------------------------------------------
# VUES STATIQUES / GÉNÉRALES
# -----------------------------------------------------------------

def home_page(request):
    """
    Affiche la page d'accueil avec tous les packs standards.
    Affiche également la liste des Villes pour la sélection.
    """
    packs = Pack.objects.prefetch_related('activites', 'ville').all() 
    villes = Ville.objects.all()
    
    context = {
        "packs": packs,
        "villes": villes
    }
    return render(request, "accueil.html", context=context)

def services(request):
    """
    Page de présentation des services (qui sont désormais axés sur les Packs).
    """
    return render(request, 'services.html')

def mon_activite(request):
    """
    Page du compte utilisateur affichant uniquement les réservations de Packs.
    """
    return render(request, 'mon_activite.html')

def contact(request):
    """
    Page de contact statique.
    """
    return render(request, 'contact.html')

def about(request):
    """
    Page 'À propos' statique.
    """
    return render(request, 'about.html')


# -----------------------------------------------------------------
# VUES DE RÉSERVATION
# -----------------------------------------------------------------

@login_required
def reservation_pack(request, pack_id=None):
    """
    Gère l'affichage et la soumission du formulaire de réservation de Pack.
    Peut être appelée avec un pack_id pour pré-sélectionner un pack.
    """
    user = request.user
    montant_total = None
    
    # Si un ID de pack est fourni dans l'URL, pré-sélectionnez-le
    initial_data = {}
    if pack_id:
        pack_a_reserver = get_object_or_404(Pack, pk=pack_id)
        initial_data['pack'] = pack_a_reserver
        # Si le pack existe, pré-calculer le montant_total pour l'affichage initial
        montant_total = round(pack_a_reserver.prix_par_personne_euros * 1, 2) # Montant pour 1 personne

    if request.method == "POST":
        form = ReservationPackForm(request.POST, initial=initial_data)
    else:
        form = ReservationPackForm(initial=initial_data)

    # Assurez-vous que le queryset du champ 'pack' contient tous les packs standard
    form.fields['pack'].queryset = Pack.objects.all()

    if request.method == "POST" and form.is_valid():
        
        # 1. Création de l'objet ReservationPack
        reservation = form.save(commit=False)
        reservation.user = user
        reservation.statut = "demande"
        
        # 2. Le montant est calculé et enregistré automatiquement dans la méthode save() du modèle
        reservation.save() 
        
        montant_total = reservation.montant_total
        
        # 3. Notification
        try:
            notifier_admins_reservation_pack(reservation)
            notifier_utilisateur_reservation_pack(reservation)
        except NameError as e:
            # Gestion d'erreur si la notification n'est pas configurée
            messages.warning(request, "Réservation enregistrée, mais l'envoi d'e-mail a échoué (vérifiez la configuration).")

        messages.success(request, "Réservation enregistrée avec succès ! Votre demande est en cours de traitement.")

        return render(request, "reservation/success_pack.html", {
            "message": "Réservation enregistrée avec succès !",
            "reservation": reservation,
        })

    # Context pour la vue GET ou si le formulaire est invalide
    packs_standards = Pack.objects.prefetch_related('activites').all() 

    return render(request, 'reservation/pack.html', {
        "form": form,
        "montant_total": montant_total,
        "packs_standards": packs_standards,
    })

@login_required
def mon_activite(request):
    """
    Affiche toutes les réservations de l'utilisateur.
    """
    # Filtre uniquement sur ReservationPack
    reservations = ReservationPack.objects.filter(user=request.user).order_by('-date_demande')
    
    # Ajout du type pour l'affichage dans le template
    for r in reservations:
        r.type_reservation = "Pack Voyage Standard"

    return render(request, "mon_activite.html", {"reservations": reservations})