from django import forms
from .models import Diagnose

class DiagnoseForm(forms.ModelForm):
    class Meta:
        model = Diagnose
        fields = ['date_time', 'note', 'diagnose', 'photo_before', 'photo_after']
