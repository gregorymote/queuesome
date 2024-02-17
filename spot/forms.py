from django import forms
from spot.models import Fly


class FlyForm(forms.Form):

    artwork_url = forms.CharField(
        label = 'Album Image URL',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder': 'ENTER ALBUM IMAGE URL'
            }
        ),
        max_length=Fly._meta.get_field('album_url').max_length
    )

    album_name = forms.CharField(
        label = 'Album Name',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder': 'ENTER ALBUM NAME'
            }
        ),
        max_length=Fly._meta.get_field('album_name').max_length
    )

    artist_name = forms.CharField(
        label = 'Artist Name',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder': 'ENTER ARTIST NAME'
            }
        ),
        max_length=Fly._meta.get_field('artist_name').max_length
    )

    album_url = forms.CharField(
        label = 'Album URL',
        widget=forms.TextInput(
            attrs={
                'class':'form-control',
                'placeholder': 'ENTER ALBUM URL'
            }
        ),
        max_length=Fly._meta.get_field('album_url').max_length
    )

    x_coord = forms.FloatField(
        label = 'X Coord'
    )
    y_coord = forms.FloatField(
        label = 'Y Coord'
    )

    width = forms.FloatField(
        label = 'width'
    )
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Search Albums',
            }))
    result = forms.CharField(label = 'result pk', initial='-1', required = False,widget=forms.TextInput(attrs={'class':'form-control',}))
    color = forms.CharField(label = 'Color', required = False,widget=forms.TextInput(attrs={'class':'form-control',}))


class DayForm(forms.Form):
    search = forms.CharField(
        required=False,
        widget=forms.TextInput(
            attrs={
                'class': 'form-control',
                'placeholder': 'Search Flys',
    }))
    result = forms.CharField(label = 'result pk', initial='-1', required = False,widget=forms.TextInput(attrs={'class':'form-control',}))