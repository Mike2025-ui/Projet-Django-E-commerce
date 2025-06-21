from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser  # Ton modèle utilisateur personnalisé
from shop.models import Product

class CustomUserCreationForm(UserCreationForm):
    username = forms.CharField(
        required=True,
        widget=forms.TextInput(attrs={'placeholder': "Nom d'utilisateur", 'class': 'form-control'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'placeholder': "Email", 'class': 'form-control'})
    )
    photo = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={'class': 'form-control-file'}),
        label="Photo de profil"
    )
    password1 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': "Mot de passe", 'class': 'form-control'})
    )
    password2 = forms.CharField(
        required=True,
        widget=forms.PasswordInput(attrs={'placeholder': "Confirmer le mot de passe", 'class': 'form-control'})
    )

    class Meta:
        model = CustomUser  # Change ceci si tu utilises `User`
        fields = ['username', 'email', 'photo', 'password1', 'password2']
        
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("Cet e-mail est déjà utilisé.")
        return email


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ['nom', 'description', 'prix', 'category', 'image', 'image_url']
        widgets = {
            'nom': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'prix': forms.NumberInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.ClearableFileInput(attrs={'class': 'form-control-file', 'onchange': 'previewImage(this)'}),
            'image_url': forms.URLInput(attrs={'class': 'form-control', 'oninput': 'previewUrlImage(this)'}),
        }