from django.urls import path, include
from django.contrib.auth import views as auth_views
from . import views

# authUser/urls.py
urlpatterns = [
    path('', include('django.contrib.auth.urls')),
    path('signup/', views.signup_view, name='signup'),
    path('logout/', views.custom_logout, name='logout'),
    #path("password-reset/", views.custom_password_reset, name="password_reset"),

]
