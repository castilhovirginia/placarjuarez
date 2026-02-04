from django.db.models import Q, Sum, F, IntegerField
from django.db.models.functions import Coalesce
from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from .models import (
    Campeonato, Partida, Danca, Extra, Fase, Equipe
)

def home(request):
    slides = [
        "creditos.html",
        "ranking_geral.html",
    ]

    return render(request, "home.html", {
        "slides": slides,
    })


def creditos(request):
    return render(request, 'creditos.html')


from collections import defaultdict
from django.shortcuts import get_object_or_404, render
from .models import Campeonato, Partida, Danca, Extra, Fase, Equipe

PONTOS_COLOCACAO = {
    1: 1000,
    2: 800,
    3: 600,
    4: 400,
}

def ranking_geral(request, campeonato_id):
    campeonato = get_object_or_404(Campeonato, id=campeonato_id)

    # Inicializa o ranking com todas as equipes do campeonato e ano
    equipes = Equipe.objects.filter(ano=campeonato.ano)
    ranking = defaultdict(int)

    # Adiciona todas as equipes ao ranking (mesmo que não tenham pontuado ainda)
    for equipe in equipes:
        ranking[equipe] = 0  # Inicializa as equipes com 0 pontos

    # 🔹 PARTIDAS (Final e Terceiro Lugar)
    partidas = Partida.objects.filter(
        campeonato=campeonato,
        encerrada=True,
        fase__in=[Fase.FINAL, Fase.TERCEIRO]
    ).select_related('equipe_a', 'equipe_b', 'vencedora')

    for partida in partidas:
        vencedora = partida.vencedora

        if not vencedora:
            continue

        perdedora = (
            partida.equipe_b if vencedora == partida.equipe_a
            else partida.equipe_a
        )

        if partida.fase == Fase.FINAL:
            ranking[vencedora] += PONTOS_COLOCACAO[1]
            ranking[perdedora] += PONTOS_COLOCACAO[2]

        elif partida.fase == Fase.TERCEIRO:
            ranking[vencedora] += PONTOS_COLOCACAO[3]
            ranking[perdedora] += PONTOS_COLOCACAO[4]

    # 🔹 DANÇA
    dancas = Danca.objects.filter(
        campeonato=campeonato,
        colocacao__in=[1, 2, 3, 4]
    ).select_related('equipe')

    for danca in dancas:
        ranking[danca.equipe] += PONTOS_COLOCACAO[danca.colocacao]

    # 🔹 EXTRAS (doações + / penalidades -)
    extras = Extra.objects.filter(
        campeonato=campeonato
    ).select_related('equipe')

    for extra in extras:
        if extra.ocorrencia == 1:  # Doação
            ranking[extra.equipe] += extra.pontos
        elif extra.ocorrencia == 2:  # Penalidade
            ranking[extra.equipe] -= extra.pontos

    # 🔹 Ordenação
    ranking_ordenado = sorted(
        ranking.items(),
        key=lambda item: item[1],
        reverse=True
    )

    context = {
        'campeonato': campeonato,
        'ranking': ranking_ordenado
    }

    return render(request, 'ranking_geral.html', context)
