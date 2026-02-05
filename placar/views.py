from collections import defaultdict

from django.db.models import Q
from django.shortcuts import get_object_or_404, render
from .models import Campeonato, Partida, Danca, Extra, Fase, Equipe

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
            ranking[extra.equipe] += extra.pontos  # Soma os pontos das doações
        elif extra.ocorrencia == 2:  # Penalidade
            ranking[extra.equipe] += extra.pontos  # Soma o valor negativo das penalidades (já é negativo)

    # 🔹 Ordenação: Primeiro por pontos, depois por nome (caso empate em 0 pontos)
    ranking_ordenado = sorted(
        ranking.items(),
        key=lambda item: (-item[1], item[0].nome)  # Ordena por pontos decrescentes e nome alfabético
    )

    context = {
        'campeonato': campeonato,
        'ranking': ranking_ordenado
    }

    return render(request, 'ranking_geral.html', context)

PONTOS_COLOCACAO = {
    1: 1000,
    2: 800,
    3: 600,
    4: 400,
}


def pontuacao_por_equipe(request, equipe_id):
    equipe = get_object_or_404(Equipe, id=equipe_id)

    # Filtra todas as partidas em que a equipe participou (como equipe_a ou equipe_b)
    partidas = Partida.objects.filter(
        (Q(equipe_a=equipe) | Q(equipe_b=equipe)),
        encerrada=True  # Apenas partidas que já foram encerradas
    ).select_related('campeonato', 'modalidade').order_by('modalidade', 'data')  # Ordenando por modalidade e data

    # Lista para armazenar os resultados de cada partida
    resultados = []
    total_pontos = 0  # Variável para somar os pontos da equipe

    for partida in partidas:
        # Define o resultado da partida
        if partida.equipe_a == equipe:
            adversario = partida.equipe_b
            placar = f"{partida.placar_a} x {partida.placar_b}"
            resultado = 'Vencedora' if partida.vencedora == partida.equipe_a else 'Perdedora'
        else:
            adversario = partida.equipe_a
            placar = f"{partida.placar_b} x {partida.placar_a}"
            resultado = 'Vencedora' if partida.vencedora == partida.equipe_b else 'Perdedora'

        # Inicializa a pontuação como 0
        pontuacao = 0

        # Se for uma partida de final ou terceiro lugar, define a pontuação
        if partida.fase == Fase.FINAL:
            pontuacao = PONTOS_COLOCACAO[1] if partida.vencedora == equipe else PONTOS_COLOCACAO[2]
        elif partida.fase == Fase.TERCEIRO:
            pontuacao = PONTOS_COLOCACAO[3] if partida.vencedora == equipe else PONTOS_COLOCACAO[4]

        # Adiciona o resultado da partida à lista de resultados
        resultados.append({
            'campeonato': partida.campeonato,
            'modalidade': partida.modalidade,
            'fase': partida.get_fase_display(),  # Nome da fase
            'adversario': adversario,
            'placar': placar,
            'resultado': resultado,
            'pontuacao': pontuacao,
            'data': partida.data  # Adicionando a data da partida
        })

        # Soma a pontuação das partidas ao total
        total_pontos += pontuacao

    # Pontuação extra (doações e penalidades)
    extras = Extra.objects.filter(equipe=equipe)
    doacoes = extras.filter(ocorrencia=1)  # Doações
    penalidades = extras.filter(ocorrencia=2)  # Penalidades

    doacoes_pontos = sum([doacao.pontos for doacao in doacoes])
    penalidades_pontos = sum([penalidade.pontos for penalidade in penalidades])

    # Somando as doações e penalidades ao total de pontos
    total_pontos += doacoes_pontos - penalidades_pontos

    # Contexto para renderizar a template
    context = {
        'equipe': equipe,
        'resultados': resultados,
        'doacoes_pontos': doacoes_pontos,
        'penalidades_pontos': penalidades_pontos,
        'total_pontos': total_pontos
    }

    return render(request, 'pontuacao_por_equipe.html', context)
