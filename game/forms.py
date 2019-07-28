from django import forms
from django.utils.safestring import mark_safe
from party.models import Library
from party.models import Searches

CHOICES = [('1', 'Track'), ('2', 'Artist')]

class blankForm(forms.Form):
    blank = forms.CharField(label='text', required=False)
    
class chooseCategoryForm(forms.Form):
    cat_choice = forms.ModelChoiceField(label = 'choose category', queryset=Library.objects.all()) 
    custom = forms.CharField(label = 'create your own', required = False)

class searchForm(forms.Form):
    search = forms.CharField(label = 'search', required = False)
    
    choice_field = forms.ChoiceField(widget=forms.RadioSelect, choices=CHOICES)

class searchResultsForm(forms.Form):
    results = forms.ModelChoiceField(queryset=Searches.objects.all())
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        super(ChooseDeviceForm,self).__init__(*args,**kwargs)
        self.fields['device'].queryset = Searches.objects.filter(party=self.partyObject)
