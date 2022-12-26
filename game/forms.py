from django import forms
from django.utils.safestring import mark_safe
from party.models import Library, Searches, Devices
from game.fields import ListTextWidget
from django.core.validators import MinValueValidator


class blankForm(forms.Form):
    blank = forms.CharField(label='text', required=False)
    

class chooseCategoryForm(forms.Form):
    cat_choice = forms.ModelChoiceField(
        label = 'Curate the Vibe',
        queryset=Library.objects.all(),
        required=False,
        widget=forms.Select(attrs={'class':'form-control'})
    ) 
    custom = forms.CharField(
        label = 'Create Your Own',
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'NAME',}),
        max_length=Library._meta.get_field('name').max_length
    )
    custom_desc = forms.CharField(
        label = 'Create Your Own',
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'DESCRIPTION',}),
        max_length=Library._meta.get_field('description').max_length
    )
    artist = forms.CharField(
        label = 'Artist Name',
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER THE NAME OF AN ARTIST',}),
        max_length=Library._meta.get_field('name').max_length
    )
    CHOICES=[('Artist','Artist'),( 'Song','Song')]
    scatt_radio = forms.ChoiceField(
        choices=CHOICES,
        widget=forms.RadioSelect(attrs={'class':'form-check-inline'}),
        initial='Song'
    )

    search = forms.CharField(required = False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Search for Vibes',}))
    result = forms.CharField(label = 'result pk', initial='-1', required = False,widget=forms.TextInput(attrs={'class':'form-control',}))

    def __init__(self,*args,**kwargs):
        self.repo = kwargs.pop('repo')
        super(chooseCategoryForm,self).__init__(*args,**kwargs)
        combined_query = Library.objects.filter(pk__in=self.repo, visible=True) | Library.objects.filter(special=True, visible=True)
        self.fields['cat_choice'].queryset = combined_query.order_by('order','name')


class pickCategoryForm(forms.Form):
    custom = forms.CharField(
        label = 'Create Your Own',
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER SOME WORDS HERE...',}),
        max_length=Library._meta.get_field('name').max_length
    )
    custom_desc = forms.CharField(
        label = 'Create Your Own',
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'DESCRIPTION',}),
        max_length=Library._meta.get_field('description').max_length
    )
    search = forms.CharField(
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Search for Vibes',})
    )
    result = forms.CharField(
        label = 'result pk',
        initial='-1',
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control',})
    )
    artist = forms.CharField(
        label = 'Artist Name',
        required = False,
        widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'ENTER THE NAME OF AN ARTIST',}),
        max_length=Library._meta.get_field('name').max_length - 15
    )


class searchForm(forms.Form):
    result = forms.CharField(label = 'result pk', initial='-1', required = False,widget=forms.TextInput(attrs={'class':'form-control',}))
    search = forms.CharField(required = False, widget=forms.TextInput(attrs={'class':'form-control', 'placeholder': 'Search Songs or Artists',}))
    #search = forms.CharField(required=False,widget=forms.TextInput)

    #def __init__(self, *args, **kwargs):
    #    _song_list = kwargs.pop('data_list', None)
    #    super(searchForm, self).__init__(*args, **kwargs)

    # the "name" parameter will allow you to use the same widget more than once in the same
    # form, not setting this parameter differently will cuse all inputs display the
    # same list.
    #    self.fields['search'].widget = ListTextWidget(data_list=_song_list, name='song-list')

class searchResultsForm(forms.Form):
    results = forms.ModelChoiceField(widget=forms.Select(attrs={'class':'form-control'}),queryset=Searches.objects.all(), required=False)
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        self.userObject = kwargs.pop('userObject')
        super(searchResultsForm,self).__init__(*args,**kwargs)
        self.fields['results'].queryset = Searches.objects.filter(party=self.partyObject, user=self.userObject).order_by('pk')


class settingsForm(forms.Form):

    time = forms.IntegerField(validators=[MinValueValidator(30)])
    device = forms.ModelChoiceField(queryset=Devices.objects.all(), required = False, widget=forms.Select(attrs={'class':'form-control'}))
        
    def __init__(self,*args,**kwargs):
        
        self.partyObject = kwargs.pop('partyObject')
        super(settingsForm,self).__init__(*args,**kwargs)
        self.fields['device'].queryset = Devices.objects.filter(party=self.partyObject)