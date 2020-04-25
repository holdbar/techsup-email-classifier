from django import forms

class EmailForm(forms.Form):
    email = forms.CharField(widget=forms.Textarea,label="Email")
