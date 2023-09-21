
# myApp/forms.py
from django import forms
from django.contrib.auth.forms import AuthenticationForm

# Reordering Form and View
class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, request=None, *args, **kwargs):
        super().__init__(request=None, *args, **kwargs)
        self.fields['username'].label = 'Usuario'
        self.fields['password'].label = 'Contraseña'

# myApp/forms.py
class PositionForm(forms.Form):
    position = forms.CharField()

    