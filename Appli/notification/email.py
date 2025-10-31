from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model
from django.db.models.signals import pre_save
from django.dispatch import receiver
from Appli.models import ReservationPack

User = get_user_model()


# ====================================================================
# NOTIFICATIONS ADMINISTRATEURS
# ====================================================================

def notifier_admins_reservation_pack(reservation):
    """Notifie les admins d'une nouvelle réservation de Pack."""
    subject = "Nouvelle réservation Estamira"
    
    # NOTE: L'objet 'reservation' n'a plus 'pack_personnalise'
    html_content = render_to_string("email/admin/reservation_notification_pack.html", {
        "user": reservation.user,
        "pack": reservation.pack,
        "date_debut": reservation.date_debut,
        "date_fin": reservation.date_fin,
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

def notifier_utilisateur_reservation_pack(reservation):
    """Envoie la confirmation de réservation de Pack à l'utilisateur."""
    subject = "Confirmation de votre réservation Estamira"
    html_content = render_to_string("email/utilisateur/reservation_notif_user_pack.html", {
        "user": reservation.user,
        "pack": reservation.pack,
        "date_debut": reservation.date_debut,
        "date_fin": reservation.date_fin,
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

@receiver(pre_save, sender=ReservationPack)
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
            # Utilise une fonction plutôt qu'un appel direct pour une meilleure organisation
            notifier_utilisateur_changement_statut(instance)