from django import forms

from party.models import Party
from party.models import Devices


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

class ChooseDeviceForm(forms.Form):

    device = forms.ModelChoiceField(queryset=Devices.objects.all())
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        super(ChooseDeviceForm,self).__init__(*args,**kwargs)
        self.fields['device'].queryset = Devices.objects.filter(party=self.partyObject)
    


