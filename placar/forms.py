from django import forms
from .models import Modalidade, Equipe, Partida, Danca, Extra


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


class PartidaAdminForm(forms.ModelForm):
    HOUVE_WO_CHOICES = (
        ("", "---------"),
        ("sim", "Sim"),
        ("nao", "Não"),
    )

    houve_wo = forms.ChoiceField(
        label="Houve WO?",
        choices=HOUVE_WO_CHOICES,
        required=False,
    )

    class Meta:
        model = Partida
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)#

        campeonato = None

        # 🔹 edição
        if self.instance.pk:
            campeonato = self.instance.campeonato

        # 🔹 criação (quando o usuário já escolheu o campeonato)
        elif 'campeonato' in self.data:
            try:
                campeonato_id = int(self.data.get('campeonato'))
                campeonato = Campeonato.objects.get(pk=campeonato_id)
            except (ValueError, Campeonato.DoesNotExist):
                campeonato = None

        # 🔹 filtrar equipes pelo ano do campeonato
        if campeonato:
            self.fields['equipe_a'].queryset = Equipe.objects.filter(
                ano=campeonato.ano
            )
            self.fields['equipe_b'].queryset = Equipe.objects.filter(
                ano=campeonato.ano
            )
        else:
            # enquanto não houver campeonato definido, não mostra ninguém
            self.fields['equipe_a'].queryset = Equipe.objects.none()
            self.fields['equipe_b'].queryset = Equipe.objects.none()

        #🧹 Sempre limpar vencedora no formulário (edição)
        if 'vencedora' in self.fields:
            self.initial['vencedora'] = None

        # 🔁 Mapear BooleanField → ChoiceField ao editar
        if self.instance.pk:
            if self.instance.houve_wo is True:
                self.initial["houve_wo"] = "sim"
            elif self.instance.houve_wo is False:
                self.initial["houve_wo"] = "nao"

        # 🔒 Remover botões FK (como você já tinha)
        fk_fields = [
            'campeonato',
            'modalidade',
            'equipe_a',
            'equipe_b',
            'equipe_wo',
            'vencedora',
        ]

        for field_name in fk_fields:
            field = self.fields.get(field_name)
            if isinstance(field, forms.ModelChoiceField):
                field.widget.can_add_related = False
                field.widget.can_change_related = False
                field.widget.can_delete_related = False
                field.widget.can_view_related = False

        # 🔢 Placar não aceita valores negativos
        for field_name in ('placar_a', 'placar_b'):
            field = self.fields.get(field_name)
            if field:
                field.min_value = 0
                field.widget.attrs['min'] = 0

    def clean_houve_wo(self):
        value = self.cleaned_data.get("houve_wo")
        if value == "sim":
            return True
        if value == "nao":
            return False
        return None

    def clean(self):
        cleaned_data = super().clean()

        if cleaned_data.get("iniciada") and cleaned_data.get("houve_wo") is None:
            self.add_error(
                "houve_wo",
                "Informe se houve ou não WO. Ou desmarque a partida como iniciada."
            )

        return cleaned_data


class DancaForm(forms.ModelForm):
    class Meta:
        model = Danca
        fields = '__all__'
        widgets = {
            'data_apresentacao': forms.DateInput(
                attrs={'type': 'date'}
            ),
            'horario_apresentacao': forms.TimeInput(
                attrs={'type': 'time'}
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  #

        campeonato = None

        # 🔹 edição
        if self.instance.pk:
            campeonato = self.instance.campeonato

        # 🔹 criação (quando o usuário já escolheu o campeonato)
        elif 'campeonato' in self.data:
            try:
                campeonato_id = int(self.data.get('campeonato'))
                campeonato = Campeonato.objects.get(pk=campeonato_id)
            except (ValueError, Campeonato.DoesNotExist):
                campeonato = None

        # 🔹 filtrar equipes pelo ano do campeonato
        if campeonato:
            self.fields['equipe'].queryset = Equipe.objects.filter(
                ano=campeonato.ano
            )
        else:
            # enquanto não houver campeonato definido, não mostra ninguém
            self.fields['equipe'].queryset = Equipe.objects.none()

        # 🔒 Remover botões FK (como você já tinha)
        fk_fields = [
            'equipe',
            'campeonato',
        ]

        for field_name in fk_fields:
            field = self.fields.get(field_name)
            if isinstance(field, forms.ModelChoiceField):
                field.widget.can_add_related = False
                field.widget.can_change_related = False
                field.widget.can_delete_related = False
                field.widget.can_view_related = False


class ExtraForm(forms.ModelForm):

    class Meta:
        model = Extra
        fields = ['campeonato', 'equipe', 'ocorrencia', 'pontos', 'observacoes']
        widgets = {
            'observacoes': forms.Textarea(attrs={
                'rows': 4,
                'cols': 40
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)  #

        campeonato = None

        # 🔹 edição
        if self.instance.pk:
            campeonato = self.instance.campeonato

        # 🔹 criação (quando o usuário já escolheu o campeonato)
        elif 'campeonato' in self.data:
            try:
                campeonato_id = int(self.data.get('campeonato'))
                campeonato = Campeonato.objects.get(pk=campeonato_id)
            except (ValueError, Campeonato.DoesNotExist):
                campeonato = None

        # 🔹 filtrar equipes pelo ano do campeonato
        if campeonato:
            self.fields['equipe'].queryset = Equipe.objects.filter(
                ano=campeonato.ano
            )
        else:
            # enquanto não houver campeonato definido, não mostra ninguém
            self.fields['equipe'].queryset = Equipe.objects.none()

        # 🔒 Remover botões FK (como você já tinha)
        fk_fields = [
            'equipe',
            'campeonato',
        ]

        for field_name in fk_fields:
            field = self.fields.get(field_name)
            if isinstance(field, forms.ModelChoiceField):
                field.widget.can_add_related = False
                field.widget.can_change_related = False
                field.widget.can_delete_related = False
                field.widget.can_view_related = False