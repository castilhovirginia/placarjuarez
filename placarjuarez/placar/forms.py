from django import forms
from .models import Modalidade, Equipe


class ModalidadeForm(forms.ModelForm):
    class Meta:
        model = Modalidade
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={'placeholder': 'Ex: Futsal'}),
            'descricao': forms.Textarea(attrs={'rows': 3}),
        }

class EquipeForm(forms.ModelForm):
    class Meta:
        model = Equipe
        fields = '__all__'
        widgets = {
            'nome': forms.TextInput(attrs={
                'placeholder': 'Ex: Equipe Azul'
            }),
            'ano': forms.NumberInput(attrs={
                'placeholder': 'Ex: 2025'
            }),
            'serie': forms.TextInput(attrs={
                'placeholder': 'Ex: 1º Ano'
            }),
        }
