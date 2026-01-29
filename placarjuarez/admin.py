from django.contrib import admin
from .models import Time, Partida


@admin.register(Time)
class TimeAdmin(admin.ModelAdmin):
    list_display = (
        'nome',
        'pontos',
        'vitorias',
        'empates',
        'derrotas',
        'gols_pro',
        'gols_contra'
    )


@admin.register(Partida)
class PartidaAdmin(admin.ModelAdmin):
    list_display = (
        'time_casa',
        'gols_casa',
        'gols_fora',
        'time_fora',
        'data'
    )
