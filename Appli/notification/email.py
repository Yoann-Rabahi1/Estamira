from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from Appli.models import ReservationPackJour, ReservationPackComplet

User = get_user_model()



# ====================================================================
# NOTIFICATIONS ADMINISTRATEURS
# ====================================================================

def notifier_admins_reservation(reservation):
    """
    Notifie les admins d'une nouvelle réservation de Pack.
    La fonction accepte soit ReservationPackJour soit ReservationPackComplet.
    """
    subject = "Nouvelle réservation Estamira"
    
    # La réservation Pack Jour n'a pas de 'date_fin', mais elle n'est pas utilisée 
    # pour le calcul ici. Le template doit être conçu pour gérer un 'date_fin' vide.
    html_content = render_to_string("email/admin/reservation_notification_pack.html", {
        "user": reservation.user,
        "pack": reservation.pack,
        "date_debut": reservation.date_debut,
        # Si c'est un Pack Jour, date_fin sera None. Le template doit s'adapter.
        "date_fin": getattr(reservation, 'date_fin', None), 
        "nb_personne": reservation.nb_personne,
        "devise_paiement": reservation.devise_paiement,
        "montant_total": reservation.montant_total
    })

    # À modifier avec l'email d'Estamira si différent de contact@maisonelba.com
    admins = ["contact@estamira.com"] 
    email = EmailMessage(subject, html_content, to=list(admins))
    email.content_subtype = "html"
    email.send()


# ====================================================================
# NOTIFICATIONS UTILISATEURS
# ====================================================================

def notifier_utilisateur_reservation(reservation):
    """Envoie la confirmation de réservation de Pack à l'utilisateur."""
    subject = "Confirmation de votre réservation Estamira"
    html_content = render_to_string("email/utilisateur/reservation_notif_user_pack.html", {
        "user": reservation.user,
        "pack": reservation.pack,
        "date_debut": reservation.date_debut,
        "date_fin": getattr(reservation, 'date_fin', None), 
        "nb_personne": reservation.nb_personne,
        "devise_paiement": reservation.devise_paiement,
        "montant_total": reservation.montant_total
    })

    email = EmailMessage(
        subject,
        html_content,
        to=[reservation.user.email]
    )
    email.content_subtype = "html"
    email.send()


def notifier_utilisateur_changement_statut(reservation):
    """Notifie l'utilisateur quand le statut de sa réservation change (par l'Admin)."""
    subject = "Mise à jour de votre réservation Estamira"
    html_content = render_to_string("email/utilisateur/statut_update.html", {
        "user": reservation.user,
        "reservation": reservation,
        # get_statut_display est une méthode de modèle pour obtenir le label lisible (ex: 'Demande effectuée')
        "nouveau_statut": reservation.get_statut_display(), 
    })

    email = EmailMessage(subject, html_content, to=[reservation.user.email])
    email.content_subtype = "html"
    email.send()


# ====================================================================
# DÉTECTEUR DE CHANGEMENT DE STATUT (Signal Django)
# ====================================================================

# CORRECTION : Le signal doit écouter les deux modèles de réservation.

@receiver(pre_save, sender=ReservationPackJour)
@receiver(pre_save, sender=ReservationPackComplet)
def detecter_changement_statut(sender, instance, **kwargs):
    """
    Détecte un changement de statut AVANT que la réservation soit sauvegardée.
    Si le statut a changé, notifie l'utilisateur.
    """
    if instance.pk:
        try:
            # Récupère la version ancienne de l'objet
            ancien = sender.objects.get(pk=instance.pk)
        except sender.DoesNotExist:
            return # Sort si l'objet n'existe pas encore (création)

        # Vérifie la différence de statut
        if ancien.statut != instance.statut:
            notifier_utilisateur_changement_statut(instance)