from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Modalidade, Equipe, Partida
from .forms import ModalidadeForm, EquipeForm


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
    class Meta:
        model = Partida
        fields = "__all__"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Lista dos campos ForeignKey que queremos desabilitar os botões
        fk_fields = [
            'modalidade',
            'equipe_a',
            'equipe_b',
            'equipe_wo',
            'vencedora',
        ]

        for field_name in fk_fields:
            field = self.fields.get(field_name)
            if isinstance(field, forms.ModelChoiceField):
                # Remove os botões de adicionar, alterar e excluir
                field.widget.can_add_related = False
                field.widget.can_change_related = False
                field.widget.can_delete_related = False
                field.widget.can_view_related = False


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    form = PartidaAdminForm

    readonly_fields = ("vencedora", 'pontuacao_a', 'pontuacao_b')

    list_display = (
        'data',
        'modalidade',
        'fase',
        'equipe_a',
        'placar_a',
        'gols_contra_a',
        'gols_contra_b',
        'pontuacao_a',
        'equipe_b',
        'placar_b',
        'pontuacao_b',
    )

    list_filter = ('modalidade', 'fase', 'encerrada')
