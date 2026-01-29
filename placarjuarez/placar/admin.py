from django.contrib import admin
from .models import Modalidade, Equipe
from .forms import ModalidadeForm, EquipeForm


@admin.register(Modalidade)
class ModalidadeAdmin(admin.ModelAdmin):
    form = ModalidadeForm

    list_display = ('nome', 'categoria', 'numero_jogadores', 'ativo')
    list_filter = ('categoria', 'ativo')
    search_fields = ('nome',)
    ordering = ('nome',)

    fieldsets = (
        ('Informações Básicas', {
            'fields': ('nome', 'descricao')
        }),
        ('Configuração', {
            'fields': ('numero_jogadores', 'categoria', 'ativo')
        }),
    )

@admin.register(Equipe)
class EquipeAdmin(admin.ModelAdmin):
    form = EquipeForm

    list_display = ('nome', 'serie', 'ano')
    list_filter = ('ano', 'serie')
    search_fields = ('nome', 'serie')
    ordering = ('ano', 'serie', 'nome')

    fieldsets = (
        ('Dados da Equipe', {
            'fields': ('nome', 'serie')
        }),
        ('Ano Letivo', {
            'fields': ('ano',)
        }),
    )
