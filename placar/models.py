from django.db import models
from django.core.validators import FileExtensionValidator
from django.core.exceptions import ValidationError

class Campeonato(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.PositiveIntegerField()

    class Meta:
        ordering = ['-ano', 'nome']
        verbose_name = "Campeonato"
        verbose_name_plural = "Campeonatos"

    def __str__(self):
        return f"{self.nome} {self.ano}"


class Equipe(models.Model):
    nome = models.CharField(max_length=100)
    ano = models.PositiveIntegerField()
    serie = models.CharField(max_length=20)
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
        return f"{self.nome}"

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
    possui_placar = models.BooleanField(
        default=True,
        help_text="Desmarque se esta modalidade não utiliza placar (ex: Xadrez)."
    )

    def __str__(self):
        return f"{self.nome} - {self.categoria}"


class Fase(models.TextChoices):
    OITAVAS = 'OIT', 'Oitavas de Final'
    QUARTAS = 'QUA', 'Quartas de Final'
    SEMI = 'SEM', 'Semifinal'
    TERCEIRO = 'TER', 'Terceiro Lugar'
    FINAL = 'FIN', 'Final'

class NumeroPartida(models.TextChoices):
    PRIMEIRA = 'PRI', '1ª'
    SEGUNDA = 'SEG', '2ª'
    TERCEIRA = 'TER', '3ª'
    QUARTA = 'QUA', '4ª'
    QUINTA = 'QUI', '5ª'
    SEXTA = 'SEX', '6ª'
    SETIMA = 'SET', '7ª'
    OITAVA = 'OIT', '8ª'
    NONA = 'NON', '9ª'
    DECIMA = 'DEC', '10ª'
    DECIMAPRIMEIRA = 'DECPRI', '11ª'
    DECIMASEGUNDA = 'DECSEG', '12ª'

PROXIMAS_PARTIDAS = {
    "PRI": {"numero": "QUI", "campo": "equipe_b", "vencedora": True},
    "SEG": {"numero": "SEX", "campo": "equipe_b", "vencedora": True},
    "TER": {"numero": "SET", "campo": "equipe_b", "vencedora": True},
    "QUA": {"numero": "OIT", "campo": "equipe_b", "vencedora": True},
    "QUI": {"numero": "NON", "campo": "equipe_a", "vencedora": True},
    "SEX": {"numero": "NON", "campo": "equipe_b", "vencedora": True},
    "SET": {"numero": "DEC", "campo": "equipe_a", "vencedora": True},
    "OIT": {"numero": "DEC", "campo": "equipe_b", "vencedora": True},
    "NON": {"numero": "DECPRI", "campo": "equipe_a", "vencedora": True},   # vencedora da NON
    "DEC": {"numero": "DECSEG", "campo": "equipe_b", "vencedora": True},  # vencedora da DEC
    "DECPRI": {"numero": "DECSEG", "campo": "equipe_a", "vencedora": False}, # perdedora da DECPRI
    "DECSEG": None,  # Final, não há próxima
}

class Partida(models.Model):
    campeonato = models.ForeignKey(Campeonato, related_name='partidas', on_delete=models.CASCADE)
    fase = models.CharField(max_length=3, choices=Fase.choices)
    modalidade = models.ForeignKey(Modalidade, related_name='modalidade', on_delete=models.CASCADE)
    numero = models.CharField(max_length=6, verbose_name="Número da partida", choices=NumeroPartida.choices)
    data = models.DateField(verbose_name="Data")
    horario = models.TimeField(verbose_name="Horário", null=True, blank=True)
    equipe_a = models.ForeignKey(
        Equipe, related_name='partidas_equipe_a', verbose_name="Equipe A", on_delete=models.CASCADE, null=True,
        blank=True,)
    equipe_b = models.ForeignKey(
        Equipe, related_name='partidas_equipe_b', verbose_name="Equipe B", on_delete=models.CASCADE, null=True,
        blank=True,)
    iniciada = models.BooleanField("Partida iniciada", default=False)
    houve_wo = models.BooleanField("Houve WO?", default=False, help_text="Preencha ao iniciar a partida. Irá habilitar ou não  o placar.")
    equipe_wo = models.ForeignKey(Equipe,
                                  null=True,
                                  blank=True,
                                  related_name='wos',
                                  verbose_name="Equipe WO",
                                  on_delete=models.SET_NULL
                                  )
    placar_a = models.IntegerField("Placar Equipe A", null=True, blank=True)
    placar_b = models.IntegerField("Placar Equipe B", null=True, blank=True)
    vencedora = models.ForeignKey(Equipe, null=True, blank=True, related_name='vitorias',
                                  verbose_name="Equipe vencedora", on_delete=models.SET_NULL)
    encerrada = models.BooleanField("Partida encerrada", default=False)

    def definir_vencedora(self):
        # 🟨 Modalidade SEM placar
        if not self.modalidade.possui_placar:

            # WO define vencedora automaticamente
            if self.houve_wo:
                if self.equipe_wo_id == self.equipe_a_id:
                    return self.equipe_b
                elif self.equipe_wo_id == self.equipe_b_id:
                    return self.equipe_a
                return None

            # Sem WO → vencedora vem do formulário
            return self.vencedora

        # 🟦 Modalidade COM placar
        if self.houve_wo:
            if self.equipe_wo_id == self.equipe_a_id:
                return self.equipe_b
            elif self.equipe_wo_id == self.equipe_b_id:
                return self.equipe_a
            return None

        if self.placar_a > self.placar_b:
            return self.equipe_a
        elif self.placar_b > self.placar_a:
            return self.equipe_b

        return None

    def atualizar_proxima_partida(self):
        """
        Atualiza automaticamente a próxima partida conforme o fluxo do torneio.
        """
        if not self.vencedora or not self.encerrada:
            return  # só funciona se houver vencedora

        info = PROXIMAS_PARTIDAS.get(self.numero)
        if not info:
            return  # final ou sem mapeamento

        try:
            prox_partida = Partida.objects.get(
                campeonato=self.campeonato,
                numero=info["numero"]
            )
        except Partida.DoesNotExist:
            return

        # determina se vai colocar vencedora ou perdedora
        if info["vencedora"]:
            equipe = self.vencedora
        else:
            # perdedora → pega a outra equipe
            equipe = self.equipe_a if self.vencedora_id != self.equipe_a_id else self.equipe_b

        setattr(prox_partida, info["campo"], equipe)
        prox_partida.save()

    def clean(self):
        errors = {}

        if self.equipe_a_id and self.equipe_b_id:

            if self.equipe_a_id == self.equipe_b_id:
                raise ValidationError(
                    {"equipe_b": "Equipe A e B não podem ser a mesma."}
                )

            if self.encerrada and self.houve_wo is True:
                if self.equipe_wo_id not in (self.equipe_a_id, self.equipe_b_id):
                    errors['equipe_wo'] = "Escolha a equipe que não compareceu: Equipe A ou Equipe B."

        modalidade = self.modalidade

        # 🟦 MODALIDADE COM PLACAR
        if modalidade and modalidade.possui_placar:

            if self.encerrada and not self.houve_wo:
                if self.placar_a is None or self.placar_b is None:
                    raise ValidationError(
                        "Informe os dois placares para encerrar a partida."
                    )

            if (
                    self.placar_a is not None
                    and self.placar_b is not None
                    and self.placar_a == self.placar_b
            ):
                raise ValidationError("Não pode haver empate.")

        # 🟨 MODALIDADE SEM PLACAR
        if modalidade and not modalidade.possui_placar:

            # 🔒 encerrada
            if self.encerrada:
                if self.houve_wo:
                    # vencedora será definida automaticamente
                    pass
                else:
                    if not self.vencedora:
                        errors['vencedora'] = (
                            "Informe a equipe vencedora para encerrar a partida."
                        )

        if errors:
            raise ValidationError(errors)

    def save(self, *args, **kwargs):
        self.full_clean()  # 🔥 ESSENCIAL

        if self.encerrada:
            self.vencedora = self.definir_vencedora()
        else:
            self.vencedora = None

        super().save(*args, **kwargs)

        # 🔹 Atualiza próxima partida automaticamente
        if self.encerrada and self.vencedora:
            self.atualizar_proxima_partida()


class Danca(models.Model):

    COLOCACAO_CHOICES = [
        (1, '1º Lugar'),
        (2, '2º Lugar'),
        (3, '3º Lugar'),
        (4, '4º Lugar'),
        (5, '5º Lugar'),
        (6, '6º Lugar'),
        (7, '7º Lugar'),
        (8, '8º Lugar'),
        (9, '9º Lugar'),
        (10, '10º Lugar'),
        (11, '11º Lugar'),
        (12, '12º Lugar'),
        (0, 'Desclassificada'),
    ]

    campeonato = models.ForeignKey(Campeonato, related_name='dancas', on_delete=models.CASCADE)

    equipe = models.ForeignKey(
        'Equipe',
        on_delete=models.CASCADE,
        related_name='apresentacoes'
    )
    data_apresentacao = models.DateField()
    horario_apresentacao = models.TimeField()
    colocacao = models.IntegerField(choices=COLOCACAO_CHOICES, null=True, blank=True)
    observacoes = models.CharField( null=True, blank=True, max_length=255)

    def __str__(self):
        return (
            f"{self.equipe} - "
            f"{self.data_apresentacao} "
            f"{self.horario_apresentacao} "
        )

class Extra(models.Model):
    class Meta:
        verbose_name = "Doação ou penalidade"
        verbose_name_plural = "Doações ou penalidades"

    OCORRENCIAS_CHOICES = [
        (1, 'Doações'),
        (2, 'Penalidades'),
        ]
    campeonato = models.ForeignKey(Campeonato, related_name='pontosextras', on_delete=models.CASCADE)
    equipe = models.ForeignKey(
        Equipe,
        on_delete=models.CASCADE,
        related_name='pontos_extras'
    )
    ocorrencia = models.IntegerField(choices=OCORRENCIAS_CHOICES, null=True, blank=True)
    pontos = models.IntegerField()
    observacoes = models.TextField(blank=True, null=True, max_length=255)
    data_registro = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.equipe} - {self.pontos} pontos"
