from django import forms
from django.utils.safestring import mark_safe
from party.models import Library
from party.models import Searches
from party.models import Devices


class blankForm(forms.Form):
    blank = forms.CharField(label='text', required=False)
    
class chooseCategoryForm(forms.Form):
    cat_choice = forms.ModelChoiceField(label = 'Choose a Category', queryset=Library.objects.filter(visible=True)) 
    custom = forms.CharField(label = 'Create Your Own', required = False)

class searchForm(forms.Form):
    search = forms.CharField(label = 'search', required = False)


class searchResultsForm(forms.Form):
    results = forms.ModelChoiceField(widget=forms.Select(attrs={'style':'max-width:100%'}),queryset=Searches.objects.all(), required=False)
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        self.userObject = kwargs.pop('userObject')
        super(searchResultsForm,self).__init__(*args,**kwargs)
        self.fields['results'].queryset = Searches.objects.filter(party=self.partyObject).filter(user=self.userObject)

class settingsForm(forms.Form):

    time = forms.IntegerField()

    device = forms.ModelChoiceField(queryset=Devices.objects.all(), required = False)
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        super(settingsForm,self).__init__(*args,**kwargs)
        self.fields['device'].queryset = Devices.objects.filter(party=self.partyObject)
