from django import forms

from party.models import Party


class LoginForm(forms.Form):
    username = forms.CharField(label = 'Enter your Spotify Username', required=True)

class NamePartyForm(forms.Form):
    party_name = forms.CharField(label='Party Name', required=True)
    user_name = forms.CharField(label = 'Your Name', required = True)


class CreateUserForm(forms.Form):
    party_choice = forms.ModelChoiceField(queryset=Party.objects.all()) 
    user_name = forms.CharField(label = 'Your Name', required = True)

class AuthForm(forms.Form):
    auth_code = forms.CharField(label = 'Enter code', required=True)


