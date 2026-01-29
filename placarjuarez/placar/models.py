from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver


class Modalidade(models.Model):
    nome = models.CharField(max_length=100)
    descricao = models.TextField(blank=True, null=True)
    numero_jogadores = models.PositiveIntegerField(
        help_text="Número de jogadores por equipe"
    )
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('MASCULINO', 'Masculino'),
            ('FEMININO', 'Feminino'),
            ('MISTO', 'Misto'),
        ]
    )
    ativo = models.BooleanField(default=True)
    data_criacao = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.nome} - {self.categoria}"

from django.db import models

from django.db import models

class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.PositiveIntegerField(help_text="Ano letivo (ex: 2025)")
    serie = models.CharField(max_length=20, help_text="Ex: 1º Ano, 2º Ano, 9º Ano")

    class Meta:
        unique_together = ('nome', 'ano')

    def __str__(self):
        return f"{self.nome} - {self.serie} ({self.ano})"

class Time(models.Model):
    nome = models.CharField(max_length=100)
    pontos = models.IntegerField(default=0)
    vitorias = models.IntegerField(default=0)
    empates = models.IntegerField(default=0)
    derrotas = models.IntegerField(default=0)
    gols_pro = models.IntegerField(default=0)
    gols_contra = models.IntegerField(default=0)

    def saldo_gols(self):
        return self.gols_pro - self.gols_contra

    def __str__(self):
        return self.nome


class Partida(models.Model):
    time_casa = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='partidas_casa')
    time_fora = models.ForeignKey(Time, on_delete=models.CASCADE, related_name='partidas_fora')
    gols_casa = models.IntegerField()
    gols_fora = models.IntegerField()
    data = models.DateField()

    def __str__(self):
        return f"{self.time_casa} x {self.time_fora}"


@receiver(post_save, sender=Partida)
def atualizar_classificacao(sender, instance, created, **kwargs):
    # Evita recalcular se a partida for editada
    if not created:
        return

    casa = instance.time_casa
    fora = instance.time_fora

    casa.gols_pro += instance.gols_casa
    casa.gols_contra += instance.gols_fora

    fora.gols_pro += instance.gols_fora
    fora.gols_contra += instance.gols_casa

    if instance.gols_casa > instance.gols_fora:
        casa.pontos += 3
        casa.vitorias += 1
        fora.derrotas += 1
    elif instance.gols_casa < instance.gols_fora:
        fora.pontos += 3
        fora.vitorias += 1
        casa.derrotas += 1
    else:
        casa.pontos += 1
        fora.pontos += 1
        casa.empates += 1
        fora.empates += 1

    casa.save()
    fora.save()
