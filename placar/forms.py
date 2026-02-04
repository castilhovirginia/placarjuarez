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
            'nome': forms.TextInput(),
            'ano': forms.NumberInput(attrs={
                'placeholder': 'Ano letivo (ex: 2026)'
            }),
            'serie': forms.TextInput(attrs={
                'placeholder': 'Ex: 1º Ano'
            }),
        }

    def clean_logo(self):
        logo = self.cleaned_data.get('logo')

        if logo:
            max_size = 2 * 1024 * 1024  # 2MB

            if logo.size > max_size:
                raise forms.ValidationError(
                    'A logo deve ter no máximo 2MB.'
                )

        return logo