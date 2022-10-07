from django import forms

from party.models import Party, Users, Devices


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.Textarea(attrs={"rows":1, "cols":34,"style": "resize: none"}),label = 'Email Address or Username', required=True)

class NamePartyForm(forms.Form):
    party_name = forms.CharField(
        label='Sesh Name',
        required=True,
        widget=forms.TextInput(attrs={'class':'form-control','placeholder': 'ENTER A SESH NAME',}),
        max_length=Party._meta.get_field('name').max_length
        )
    user_name = forms.CharField(
        label = 'Name',
        required = True,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER YOUR NAME',}),
        max_length=Users._meta.get_field('name').max_length
    
    )

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

class BlankForm(forms.Form):
    blank = forms.CharField(label='text', required=False)