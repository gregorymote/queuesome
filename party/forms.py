from django import forms

from party.models import Party
from party.models import Devices


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "cols":34,"style": "resize: none"}),label = 'Email Address or Username', required=True)

class NamePartyForm(forms.Form):
    party_name = forms.CharField(label='Sesh Name', required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER A SESH NAME',}))
    user_name = forms.CharField(label = 'Name', required = True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER YOUR NAME',}))

class CreateUserForm(forms.Form):
    party_code = forms.CharField(label = 'Room Code', required=True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Enter Room Code','style' : 'text-transform:uppercase'})) 
    user_name = forms.CharField(label = 'Name', required = True, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER YOUR NAME',}))

class AuthForm(forms.Form):
    auth_code = forms.CharField(label = 'Enter code', required=True)

class ChooseDeviceForm(forms.Form):
    device = forms.ModelChoiceField(queryset=Devices.objects.all(), widget=forms.Select(attrs={'class':'form-control'}))    
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        super(ChooseDeviceForm,self).__init__(*args,**kwargs)
        self.fields['device'].queryset = Devices.objects.filter(party=self.partyObject)
