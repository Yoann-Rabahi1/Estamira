from django.template.loader import render_to_string
from django.core.mail import EmailMessage
from django.contrib.auth import get_user_model

User = get_user_model()

def notifier_creation_nouvel_utilisateur(user):
    """
    Envoie un email à l'utilisateur pour l'informer que son compte a été créé.
    """
    subject = "Votre compte Maison Elba a été créé"
    html_content = render_to_string("email/utilisateur/notif_creation_account_user.html", {
        "user": user,
        "site_url" : "https://maisonelba.com/auth/login/"
    })

    email = EmailMessage(subject, html_content, to=[user.email])
    email.content_subtype = "html"
    email.send()
