from django import forms
from party.models import Library

class blankForm(forms.Form):
    blank = forms.CharField(label='text', required=False)
    
class chooseCategoryForm(forms.Form):
    cat_choice = forms.ModelChoiceField(label = 'choose category', queryset=Library.objects.all()) 
    custom = forms.CharField(label = 'create your own', required = False)
