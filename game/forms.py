from django import forms
from django.utils.safestring import mark_safe
from party.models import Library
from party.models import Searches
from party.models import Devices


class blankForm(forms.Form):
    blank = forms.CharField(label='text', required=False)
    

class chooseCategoryForm(forms.Form):
    cat_choice = forms.ModelChoiceField(label = 'Choose a Category', queryset=Library.objects.all(), required=False, widget=forms.Select(attrs={'class':'form-control'})) 
    custom = forms.CharField(label = 'Create Your Own',  required = False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER YOUR OWN CATEGORY',}) )
    
    def __init__(self,*args,**kwargs):
        self.repo = kwargs.pop('repo')
        super(chooseCategoryForm,self).__init__(*args,**kwargs)
        combined_query = Library.objects.filter(pk__in=self.repo, visible=True) | Library.objects.filter(special=True, visible=True)
        self.fields['cat_choice'].queryset = combined_query.order_by('order','name')


class searchForm(forms.Form):
    search = forms.CharField(label = 'search', required = False,widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Search Songs or Artists',}))


class searchResultsForm(forms.Form):
    results = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}),queryset=Searches.objects.all(), required=False)
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        self.userObject = kwargs.pop('userObject')
        super(searchResultsForm,self).__init__(*args,**kwargs)
        self.fields['results'].queryset = Searches.objects.filter(party=self.partyObject).filter(user=self.userObject)


class settingsForm(forms.Form):

    time = forms.IntegerField()
    device = forms.ModelChoiceField(queryset=Devices.objects.all(), required = False, widget=forms.Select(attrs={'class':'form-control'}))
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        super(settingsForm,self).__init__(*args,**kwargs)
        self.fields['device'].queryset = Devices.objects.filter(party=self.partyObject)
