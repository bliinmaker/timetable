from django.forms import CharField, EmailField
from django.contrib.auth import models, forms


class RegistrationForm(forms.UserCreationForm):
    first_name = CharField(max_length=100, required=True)
    last_name = CharField(max_length=100, required=True)
    email = EmailField(max_length=200, required=True)

    class Meta:
        model = models.User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
