from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = User

    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Informations personnelles', {'fields': ('prenom', 'nom', 'tel', 'date_de_creation')}),
        ('Permissions', {'fields': ('is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Statut', {'fields': ('is_active',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'prenom', 'nom', 'tel', 'password1', 'password2', 'is_staff', 'is_superuser', 'is_active'),
        }),
    )

    list_display = ('email', 'prenom', 'nom', 'tel','date_de_creation', 'is_staff')
    search_fields = ('email', 'prenom', 'nom')
    ordering = ('email',)

admin.site.register(User, CustomUserAdmin)
