from django import forms
from .models import Feedback
from django.core.exceptions import ValidationError

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['username', 'telephone', 'title', 'description']

        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', "placeholder": "ФИО клиента"}),
            'telephone': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Номер телефона"}),
            'title': forms.TextInput(attrs={'class': 'form-control', "placeholder": "Заголовок"}),
            'description': forms.Textarea(attrs={'class': 'form-control', "placeholder": "Описание"}),
        }


class UploadFileForm(forms.ModelForm):
    file = forms.FileField()
