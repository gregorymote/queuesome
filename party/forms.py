from django import forms

from party.models import Party


class NamePartyForm(forms.Form):
    party_name = forms.CharField(label='Party Name', required=True)
    user_name = forms.CharField(label = 'Your Name', required = True)


class CreateUserForm(forms.Form):
    party_choice = forms.ModelChoiceField(queryset=Party.objects.all()) 
    user_name = forms.CharField(label = 'Your Name', required = True)
