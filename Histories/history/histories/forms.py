from django import forms
from .models import History, Comment, Guest

from django.contrib.auth import get_user_model

User = get_user_model()


class HistoryForm(forms.ModelForm):
    class Meta:
        model = History
        fields = ('title', 'description', 'place')

    widgets = {
        'title': forms.Textarea(attrs={'class': 'form-control'}),
        'description': forms.Textarea(attrs={'class': 'form-control'}),
        'place': forms.Select(attrs={'class': 'form-control'})
    }

    def __init__(self, *args, **kwargs):
        super(HistoryForm, self).__init__(*args, **kwargs)
        self.fields['description'].label = ""
        self.fields['title'].label = "Titulo"
        self.fields['place'].label = "Lugar"


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('title', 'image', 'description')

    widgets = {
        'title': forms.Textarea(attrs={'class': 'form-control'}),
        'image': forms.FileInput(attrs={'class': 'form-control'}),
        'description': forms.Textarea(attrs={'class': 'form-control'})
    }

    def __init__(self, *args, **kwargs):
        super(CommentForm, self).__init__(*args, **kwargs)
        self.fields['description'].label = ""
        self.fields['title'].label = "Titulo"
        self.fields['image'].label = "Imagen"


class GuestForm(forms.ModelForm):
    CHOICES = [
        ('R', 'Visitar historia.'),
        ('C', ' Comentar Fotos.'),
        ('I', 'Comentar y agregar fotos.')
    ]

    class Meta:
        model = Guest
        fields = ['user', 'permit_level']

    permit_level = forms.CharField( widget=forms.RadioSelect(choices=CHOICES))
    print("GuestForm-->History")


    widgets = {
        'user' : forms.Select(choices=User.objects.all()),
    }

    def __init__(self, *args, **kwargs):
        super(GuestForm, self).__init__(*args, **kwargs)
        self.fields['permit_level'].label = "Permitir"
        self.fields['user'].label = "Usuario"
        self.fields['user'].widget.attrs['style'] = 'max-width: 300px;overflow: auto;'
