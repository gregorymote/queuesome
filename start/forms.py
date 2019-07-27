from django import forms


class blankForm(forms.Form):
    blank = forms.CharField(label='text', required=False)
