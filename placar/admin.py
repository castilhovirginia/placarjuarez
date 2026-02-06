from django.contrib import admin
from django.utils.html import format_html
from django import forms
from .models import Modalidade, Equipe, Partida, Campeonato, Danca, Extra
from .forms import ModalidadeForm, EquipeForm, PartidaAdminForm, DancaForm, ExtraForm
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

    class Media:
        js = ("admin/js/modalidade.js",)


    list_display = (
        'nome',
        'categoria',
        'possui_placar',
    )

    list_filter = ('categoria','possui_placar')
    search_fields = ('nome',)
    ordering = ('categoria','possui_placar')

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


    def logo_preview(self, obj):
        if not obj.logo:
            return "Logo não adicionado"
        return format_html(
            '<img src="{}" style="height: 80px; border-radius: 6px;" />',
            obj.logo.url
        )

    logo_preview.short_description = "Visualização do logo"


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    form = PartidaAdminForm


    class Media:
        js = ("admin/js/partida.js",)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        field = super().formfield_for_foreignkey(db_field, request, **kwargs)

        if db_field.name == "modalidade":
            # Mapa de possui_placar
            mapa_placar = {
                str(m.id): m.possui_placar
                for m in Modalidade.objects.all()
            }
            field.widget.attrs["data-possui-placar-map"] = json.dumps(mapa_placar, ensure_ascii=True)

            # Mapa de possui_sets
            mapa_sets = {
                str(m.id): m.possui_sets  # <-- aqui
                for m in Modalidade.objects.all()
            }
            field.widget.attrs["data-possui-set-map"] = json.dumps(mapa_sets, ensure_ascii=True)

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
        'numero',
        'equipe_a',
        'placar_a',
        'equipe_b',
        'placar_b',
        'vencedora',
        'equipe_wo',
    )

    list_filter = ('modalidade', 'fase', 'encerrada')


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
                name="danca_equipes_por_campeonato",
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
        'observacoes',
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
        'colocacao',
    )


@admin.register(Extra)
class ExtraAdmin(admin.ModelAdmin):
    form = ExtraForm

    class Media:
        js = ("admin/js/extra.js",)

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                "equipes-por-campeonato/",
                self.admin_site.admin_view(self.equipes_por_campeonato),
                name="extra_equipes_por_campeonato",
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

    list_display = ('id', 'equipe', 'ocorrencia', 'pontos', 'data_registro', 'observacoes')
    list_filter = ('equipe', 'data_registro')
    search_fields = ('equipe__nome', 'observacoes')
    ordering = ('-data_registro',)

