from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError


class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.PositiveIntegerField(help_text="Ano letivo (ex: 2025)")
    serie = models.CharField(max_length=20, help_text="Ex: 1º Ano")
    logo = models.ImageField(
        upload_to='equipes/logos/',
        null=True,
        blank=True,
        validators=[
            FileExtensionValidator(allowed_extensions=['jpg', 'jpeg'])
        ],
        help_text="Logo da equipe (JPG, opcional)"
    )

    class Meta:
        unique_together = ('nome', 'ano')

    def __str__(self):
        return f"{self.nome} - {self.serie} ({self.ano})"

class Modalidade(models.Model):
    nome = models.CharField(max_length=100)
    categoria = models.CharField(
        max_length=50,
        choices=[
            ('Masculino', 'Masculino'),
            ('Feminino', 'Feminino'),
            ('Misto', 'Misto'),
        ]
    )

    def __str__(self):
        return f"{self.nome} - {self.categoria}"

class Fase(models.TextChoices):
    OITAVAS = 'OIT', 'Oitavas de Final'
    QUARTAS = 'QUA', 'Quartas de Final'
    SEMI = 'SEM', 'Semifinal'
    FINAL = 'FIN', 'Final'


class Partida(models.Model):
    fase = models.CharField(max_length=3, choices=Fase.choices)
    modalidade = models.ForeignKey(Modalidade, related_name='modalidade', on_delete=models.CASCADE)
    data = models.DateTimeField(verbose_name="Data e horário")
    equipe_a = models.ForeignKey(
        Equipe, related_name='partidas_equipe_a', verbose_name="Equipe A", on_delete=models.CASCADE
    )
    equipe_b = models.ForeignKey(
        Equipe, related_name='partidas_equipe_b', verbose_name="Equipe B", on_delete=models.CASCADE
    )
    placar_a = models.IntegerField("Placar Equipe A", default=0, null=True, blank=True)
    placar_b = models.IntegerField("Placar Equipe B",default=0, null=True, blank=True)

    gols_contra_a = models.IntegerField("Gols contra Equipe A",default=0, null=True, blank=True)
    gols_contra_b = models.IntegerField("Gols contra Equipe B", default=0, null=True, blank=True)

    pontuacao_a = models.IntegerField("Pontuação Equipe A", default=0)
    pontuacao_b = models.IntegerField("Pontuação Equipe B", default=0)
    houve_wo = models.BooleanField("Houve WO?", default=False)
    equipe_wo = models.ForeignKey(Equipe,
                                  null=True,
                                  blank=True,
                                  related_name='wos',
                                  verbose_name="Equipe WO",
                                  on_delete=models.SET_NULL
    )
    vencedora = models.ForeignKey(
        Equipe,
        null=True,
        blank=True,
        related_name='vitorias',
        verbose_name="Equipe vencedora",
        on_delete=models.SET_NULL
    )
    encerrada = models.BooleanField("Partida encerrada", default=False)

    def definir_vencedora(self):
        # Caso tenha WO
        if self.houve_wo:
            if self.equipe_wo_id == self.equipe_a_id:
                return self.equipe_b
            elif self.equipe_wo_id == self.equipe_b_id:
                return self.equipe_a
            return None  # segurança extra

        # Sem WO → vence quem tiver maior placar
        if self.placar_a > self.placar_b:
            return self.equipe_a
        elif self.placar_b > self.placar_a:
            return self.equipe_b

        # Não deve acontecer (empate já é bloqueado no clean)
        return None

    def calcular_pontuacoes(self):
        # Segurança: só calcula se estiver encerrada e sem WO
        if not self.encerrada or self.houve_wo:
            self.pontuacao_a = 0
            self.pontuacao_b = 0
            return

        # Base: placar - gols contra
        self.pontuacao_a = (self.placar_a - self.gols_contra_a)
        self.pontuacao_b = (self.placar_b - self.gols_contra_b)

        # Bônus por vitória
        if self.vencedora_id == self.equipe_a_id:
            self.pontuacao_a += 1
        elif self.vencedora_id == self.equipe_b_id:
            self.pontuacao_b += 1

    def clean(self):
        errors = {}

        # use _id, nunca o objeto
        if not self.equipe_a_id:
            errors['equipe_a'] = "Informe a equipe A."

        if not self.equipe_b_id:
            errors['equipe_b'] = "Informe a equipe B."

        if errors:
            raise ValidationError(errors)

        # agora é seguro acessar os objetos
        if self.equipe_a_id == self.equipe_b_id:
            raise ValidationError(
                {"equipe_b": "Equipe A e B não podem ser a mesma."}
            )

        if self.gols_contra_a < 0:
            raise ValidationError({"gols_contra_a": "Não pode ser negativo."})

        if self.gols_contra_b < 0:
            raise ValidationError({"gols_contra_b": "Não pode ser negativo."})

        if self.houve_wo:
            if not self.equipe_wo_id:
                raise ValidationError(
                    {"equipe_wo": "Informe qual equipe deu WO."}
                )

            if self.equipe_wo_id not in (self.equipe_a_id, self.equipe_b_id):
                raise ValidationError(
                    {"equipe_wo": "Equipe WO deve participar da partida."}
                )

            if self.placar_a is not None or self.placar_b is not None:
                raise ValidationError(
                    "Partida com WO não deve ter placar."
                )

        if self.encerrada and not self.houve_wo:
            if self.placar_a is None or self.placar_b is None:
                raise ValidationError(
                    "Informe os dois placares para encerrar a partida."
                )

            if self.placar_a == self.placar_b:
                raise ValidationError("Não pode haver empate.")

    def save(self, *args, **kwargs):
        self.full_clean()  # 🔥 ESSENCIAL

        if self.encerrada:
            self.vencedora = self.definir_vencedora()

            if not self.houve_wo:
                self.calcular_pontuacoes()
            else:
                self.pontuacao_a = 0
                self.pontuacao_b = 0
        else:
            self.vencedora = None
            self.pontuacao_a = 0
            self.pontuacao_b = 0

        super().save(*args, **kwargs)

