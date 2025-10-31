from django.shortcuts import render, HttpResponse, redirect
from django.views import View

def home_page(request):
    return render(request, 'accueil.html')

def services(request):
    return render(request, 'services.html')

def mon_activite(request):
    return render(request, 'mon_activite.html')

def contact(request):
    return render(request, 'contact.html')

def about(request):
    return render(request, 'about.html')
# Create your views here.
