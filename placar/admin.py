from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Modalidade, Equipe, Partida, Campeonato, Danca
from .forms import ModalidadeForm, EquipeForm
from django.http import JsonResponse
from django.urls import path
import json


@admin.register(Campeonato)
class CampeonatoAdmin(admin.ModelAdmin):
    list_display = ('nome', 'ano')
    list_filter = ('ano',)
    search_fields = ('nome',)
    ordering = ('-ano', 'nome')

@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    form = ModalidadeForm

    list_display = (
        'nome',
        'categoria',
    )

    list_filter = ('categoria',)
    search_fields = ('nome',)
    ordering = ('nome',)

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    form = EquipeForm

    list_display = (
        'nome',
        'serie',
        'ano',
        'logo_preview',
    )

    list_filter = ('ano', 'serie')
    search_fields = ('nome', 'serie')
    ordering = ('ano', 'serie', 'nome')

    readonly_fields = ('logo_preview',)

    fieldsets = (
        ('Dados da Equipe', {
            'fields': ('nome', 'serie', 'logo', 'logo_preview')
        }),
        ('Ano Letivo', {
            'fields': ('ano',)
        }),
    )

    def logo_preview(self, obj):
        if not obj.logo:
            return "Sem logo"
        return format_html(
            '<img src="{}" style="height: 80px; border-radius: 6px;" />',
            obj.logo.url
        )

    logo_preview.short_description = "Logo"


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


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    form = PartidaAdminForm

    class Media:
        js = ("admin/js/partida.js",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "modalidade":
            mapa = {
                str(m.id): m.possui_placar
                for m in Modalidade.objects.all()
            }

            # Garante que o JSON esteja bem escapado para uso no HTML
            json_mapa = json.dumps(mapa, ensure_ascii=True)

            # Atribui o JSON ao atributo 'data-possui-placar-map' de forma segura
            field.widget.attrs["data-possui-placar-map"] = json_mapa

        return field

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "equipes-por-campeonato/",
                self.admin_site.admin_view(self.equipes_por_campeonato),
                name="partida_equipes_por_campeonato",
            ),
        ]
        return custom_urls + urls

    def equipes_por_campeonato(self, request):
        campeonato_id = request.GET.get("campeonato_id")
        equipes = []

        if campeonato_id:
            try:
                campeonato = Campeonato.objects.get(pk=campeonato_id)
                equipes = Equipe.objects.filter(ano=campeonato.ano)
            except Campeonato.DoesNotExist:
                pass

        data = [
            {"id": equipe.id, "text": str(equipe)}
            for equipe in equipes
        ]

        return JsonResponse(data, safe=False)

    list_display = (
        'data',
        'modalidade',
        'fase',
        'vencedora',
        'equipe_wo',
        'equipe_a',
        'placar_a',
        'equipe_b',
        'placar_b',
    )

    list_filter = ('modalidade', 'fase', 'encerrada')

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

@admin.register(Danca)
class DancaAdmin(admin.ModelAdmin):
    form = DancaForm

    class Media:
        js = ("admin/js/danca.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "equipes-por-campeonato/",
                self.admin_site.admin_view(self.equipes_por_campeonato),
                name="partida_equipes_por_campeonato",
            ),
        ]
        return custom_urls + urls

    def equipes_por_campeonato(self, request):
        campeonato_id = request.GET.get("campeonato_id")
        equipes = []

        if campeonato_id:
            try:
                campeonato = Campeonato.objects.get(pk=campeonato_id)
                equipes = Equipe.objects.filter(ano=campeonato.ano)
            except Campeonato.DoesNotExist:
                pass

        data = [
            {"id": equipe.id, "text": str(equipe)}
            for equipe in equipes
        ]

        return JsonResponse(data, safe=False)

    list_display = (
        'equipe',
        'data_apresentacao',
        'horario_apresentacao',
        'colocacao',
    )

    list_filter = (
        'data_apresentacao',
        'colocacao',
    )

    search_fields = (
        'equipe__nome',
    )

    ordering = (
        'data_apresentacao',
        'horario_apresentacao',
    )

