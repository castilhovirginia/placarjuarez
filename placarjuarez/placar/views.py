from django.shortcuts import render
from django.db.models import F, IntegerField, ExpressionWrapper

from placar.models import Partida, Time


def creditos(request):
    return render(request, 'creditos.html')

def tabela_e_partidas(request):
    partidas = Partida.objects.select_related(
        'time_casa', 'time_fora'
    ).order_by('data')

    classificacao = Time.objects.annotate(
        saldo=ExpressionWrapper(
            F('gols_pro') - F('gols_contra'),
            output_field=IntegerField()
        )
    ).order_by(
        '-pontos', '-vitorias', '-saldo', '-gols_pro', 'nome'
    )

    return render(request, 'tabela.html', {
        'classificacao': classificacao,
        'partidas': partidas
    })

def ranking(request):
    ranking_geral = [
        {"posicao": 1, "nome": "Turma A", "pontos": 120},
        {"posicao": 2, "nome": "Turma B", "pontos": 110},
        {"posicao": 3, "nome": "Turma C", "pontos": 95},
        # ...
    ]

    return render(request, "ranking.html", {
        "ranking": ranking_geral,
        "ano": 2026
    })


def home(request):
    ranking = [
        {"posicao": 1, "nome": "Equipe A", "pontos": 120},
        {"posicao": 2, "nome": "Equipe B", "pontos": 95},
    ]

    slides = [
        "partials/creditos_content.html",
        "partials/ranking_content.html",
    ]

    return render(request, "home.html", {
        "slides": slides,
        "ranking": ranking,
    })
