from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from itertools import chain
from django.db.models import Q
from django.utils import timezone

from .notification.email import (
    notifier_admins_reservation,
    notifier_utilisateur_reservation
)

from .models import (
    Ville,
    ActiviteJour,
    ActiviteComplet,
    PackJour,
    PackComplet,
    ReservationPackJour,
    ReservationPackComplet,
    OptionReservation,
)

from .forms import ReservationPackJourForm, ReservationPackCompletForm


# -----------------------------------------------------------------
# VUE : PAGE D’ACCUEIL
# -----------------------------------------------------------------
def home_page(request):
    packs_jour = PackJour.objects.prefetch_related('activites').all()
    packs_complet = PackComplet.objects.prefetch_related('activites').all()

    packs = sorted(
        chain(packs_jour, packs_complet),
        key=lambda p: p.nom
    )

    villes = Ville.objects.all()

    context = {
        "packs": packs,
        "villes": villes,
    }
    return render(request, "accueil.html", context)


# -----------------------------------------------------------------
# PAGES STATIQUES
# -----------------------------------------------------------------
def services(request):
    return render(request, 'services.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')


# -----------------------------------------------------------------
# VUE : RÉSERVATION PACK JOUR
# -----------------------------------------------------------------
@login_required
def reservation_pack_jour(request, pack_id=None):
    user = request.user
    montant_total = None
    initial_data = {}

    if pack_id:
        pack_a_reserver = get_object_or_404(PackJour, pk=pack_id)
        initial_data['pack'] = pack_a_reserver
        montant_total = pack_a_reserver.get_prix_par_devise("MAD")

    if request.method == "POST":
        form = ReservationPackJourForm(request.POST, initial=initial_data)
    else:
        form = ReservationPackJourForm(initial=initial_data)

    form.fields['pack'].queryset = PackJour.objects.all()

    if request.method == "POST" and form.is_valid():
        reservation = form.save(commit=False)
        reservation.user = user
        reservation.date_reservation = timezone.now()
        reservation.save()

        montant_total = reservation.pack.get_prix_par_devise(reservation.devise) * reservation.nb_personne

        # Ajout du total des options liées
        for option in reservation.options.all():
            montant_total += option.get_prix_par_devise(reservation.devise) * option.quantite

        try:
            notifier_admins_reservation(reservation)
            notifier_utilisateur_reservation(reservation)
        except Exception:
            messages.warning(request, "Réservation enregistrée, mais l'envoi d'e-mail a échoué.")

        messages.success(request, "Réservation Pack 1 Jour enregistrée avec succès !")
        return render(request, "reservation/success_pack_jour.html", {
            "reservation": reservation,
            "montant_total": montant_total,
        })

    packs_standards = PackJour.objects.all()
    return render(request, 'reservation/jour.html', {
        "form": form,
        "montant_total": montant_total,
        "packs_standards": packs_standards,
        "is_pack_jour": True,
    })


# -----------------------------------------------------------------
# VUE : RÉSERVATION PACK COMPLET
# -----------------------------------------------------------------
@login_required
def reservation_pack_complet(request, pack_id=None):
    user = request.user
    montant_total = None
    initial_data = {}

    if pack_id:
        pack_a_reserver = get_object_or_404(PackComplet, pk=pack_id)
        initial_data['pack'] = pack_a_reserver
        montant_total = pack_a_reserver.get_prix_par_devise("MAD")

    if request.method == "POST":
        form = ReservationPackCompletForm(request.POST, initial=initial_data)
    else:
        form = ReservationPackCompletForm(initial=initial_data)

    form.fields['pack'].queryset = PackComplet.objects.all()

    if request.method == "POST" and form.is_valid():
        reservation = form.save(commit=False)
        reservation.user = user
        reservation.date_reservation = timezone.now()
        reservation.save()

        montant_total = reservation.pack.get_prix_par_devise(reservation.devise) * reservation.nb_personne

        # Ajout du total des options liées
        for option in reservation.options.all():
            montant_total += option.get_prix_par_devise(reservation.devise) * option.quantite

        try:
            notifier_admins_reservation(reservation)
            notifier_utilisateur_reservation(reservation)
        except Exception:
            messages.warning(request, "Réservation enregistrée, mais l'envoi d'e-mail a échoué.")

        messages.success(request, "Réservation Pack Complet enregistrée avec succès !")
        return render(request, "reservation/success_pack_complet.html", {
            "reservation": reservation,
            "montant_total": montant_total,
        })

    packs_standards = PackComplet.objects.all()
    return render(request, 'reservation/complet.html', {
        "form": form,
        "montant_total": montant_total,
        "packs_standards": packs_standards,
        "is_pack_jour": False,
    })

# -----------------------------------------------------------------
# VUE : MES ACTIVITÉS
# -----------------------------------------------------------------
@login_required
def mon_activite(request):
    reservations_jour = ReservationPackJour.objects.filter(user=request.user)
    reservations_complet = ReservationPackComplet.objects.filter(user=request.user)

    for r in reservations_jour:
        r.type_reservation = "Pack 1 Jour"
    for r in reservations_complet:
        r.type_reservation = "Pack Complet"

    all_reservations = sorted(
        chain(reservations_jour, reservations_complet),
        key=lambda r: r.date_reservation,
        reverse=True
    )

    return render(request, "mon_activite.html", {"reservations": all_reservations})
