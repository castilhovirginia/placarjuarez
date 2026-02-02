from django.shortcuts import render
from django.views.generic import ListView
from django.db.models import Q, Sum, F, IntegerField
from django.db.models.functions import Coalesce

from .models import Equipe, Modalidade

def get_classificacao_geral():
    return (
        Equipe.objects
        .annotate(
            pontos_a=Coalesce(
                Sum(
                    "partidas_equipe_a__pontuacao_a",
                    filter=Q(partidas_equipe_a__encerrada=True)
                ),
                0,
                output_field=IntegerField()
            ),
            pontos_b=Coalesce(
                Sum(
                    "partidas_equipe_b__pontuacao_b",
                    filter=Q(partidas_equipe_b__encerrada=True)
                ),
                0,
                output_field=IntegerField()
            ),
        )
        .annotate(total_pontos=F("pontos_a") + F("pontos_b"))
        .order_by("-total_pontos", "nome")
    )

def home(request):
    slides = [
        "creditos.html",
        "classificacao/geral.html",
    ]

    return render(request, "home.html", {
        "slides": slides,
        "classificacao": get_classificacao_geral(),
    })


def creditos(request):
    return render(request, 'creditos.html')


class ClassificacaoModalidadeView(ListView):
    template_name = "classificacao/modalidade.html"
    context_object_name = "classificacao"

    def get_queryset(self):
        modalidade_id = self.kwargs["modalidade_id"]

        return (
            Equipe.objects
            .annotate(
                pontos_a=Coalesce(
                    Sum(
                        "partidas_equipe_a__pontuacao_a",
                        filter=Q(
                            partidas_equipe_a__modalidade_id=modalidade_id,
                            partidas_equipe_a__encerrada=True
                        )
                    ),
                    0,
                    output_field=IntegerField()
                ),
                pontos_b=Coalesce(
                    Sum(
                        "partidas_equipe_b__pontuacao_b",
                        filter=Q(
                            partidas_equipe_b__modalidade_id=modalidade_id,
                            partidas_equipe_b__encerrada=True
                        )
                    ),
                    0,
                    output_field=IntegerField()
                ),
            )
            .annotate(total_pontos=F("pontos_a") + F("pontos_b"))
            .order_by("-total_pontos", "nome")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["modalidade"] = Modalidade.objects.get(
            pk=self.kwargs["modalidade_id"]
        )
        return context

class ClassificacaoGeralView(ListView):
    template_name = "classificacao/geral.html"
    context_object_name = "classificacao"

    def get_queryset(self):
        return get_classificacao_geral()
