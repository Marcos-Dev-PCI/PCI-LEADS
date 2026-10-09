from django.core.validators import RegexValidator
from django.db import models

so_digitos_14 = RegexValidator(r"^\d{14}$", "O CNPJ deve ter 14 dígitos, sem pontos ou barras.")
so_digitos_8 = RegexValidator(r"^\d{8}$", "O CEP deve ter 8 dígitos, sem traço.")
so_digitos_7 = RegexValidator(r"^\d{7}$", "O CNAE deve ter 7 dígitos, sem pontos ou barras.")


class Origem(models.TextChoices):
    """De onde veio a informação. Usado também pelo app leads."""

    RECEITA = "receita", "Receita Federal"
    CSV = "csv", "Planilha CSV"
    GOOGLE = "google", "Google"
    MANUAL = "manual", "Manual"


class Empresa(models.Model):
    """Um estabelecimento (CNPJ completo). Pode existir sem CNPJ quando vem de um CSV."""

    class Porte(models.TextChoices):
        NAO_INFORMADO = "00", "Não informado"
        ME = "01", "Microempresa (ME)"
        EPP = "03", "Empresa de Pequeno Porte (EPP)"
        DEMAIS = "05", "Demais"

    class SituacaoCadastral(models.TextChoices):
        NULA = "01", "Nula"
        ATIVA = "02", "Ativa"
        SUSPENSA = "03", "Suspensa"
        INAPTA = "04", "Inapta"
        BAIXADA = "08", "Baixada"

    cnpj = models.CharField(
        "CNPJ", max_length=14, unique=True, null=True, blank=True, validators=[so_digitos_14]
    )
    razao_social = models.CharField("razão social", max_length=255, blank=True)
    nome_fantasia = models.CharField("nome fantasia", max_length=255, blank=True)
    cnae_principal = models.CharField(
        "CNAE principal", max_length=7, blank=True, db_index=True, validators=[so_digitos_7]
    )
    cnaes_secundarios = models.JSONField("CNAEs secundários", default=list, blank=True)
    natureza_juridica = models.CharField("natureza jurídica", max_length=4, blank=True)
    porte = models.CharField(max_length=2, choices=Porte.choices, blank=True)
    capital_social = models.DecimalField(
        "capital social", max_digits=15, decimal_places=2, null=True, blank=True
    )
    data_abertura = models.DateField("data de abertura", null=True, blank=True)
    situacao_cadastral = models.CharField(
        "situação cadastral", max_length=2, choices=SituacaoCadastral.choices, blank=True
    )
    opcao_simples = models.BooleanField("optante pelo Simples", null=True, blank=True)
    opcao_mei = models.BooleanField("MEI", null=True, blank=True)

    logradouro = models.CharField(max_length=255, blank=True)
    numero = models.CharField("número", max_length=20, blank=True)
    complemento = models.CharField(max_length=255, blank=True)
    bairro = models.CharField(max_length=100, blank=True, db_index=True)
    cep = models.CharField("CEP", max_length=8, blank=True, validators=[so_digitos_8])
    municipio = models.CharField("município", max_length=100, blank=True)
    uf = models.CharField("UF", max_length=2, blank=True)

    email = models.EmailField("e-mail", blank=True)
    site = models.URLField(blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    distancia_asa_norte_km = models.DecimalField(
        "distância até a Asa Norte (km)", max_digits=6, decimal_places=2, null=True, blank=True
    )

    criado_em = models.DateTimeField("criado em", auto_now_add=True)
    atualizado_em = models.DateTimeField("atualizado em", auto_now=True)

    class Meta:
        verbose_name = "empresa"
        verbose_name_plural = "empresas"
        ordering = ["razao_social", "nome_fantasia"]

    def __str__(self):
        return self.nome_exibicao or f"Empresa {self.pk}"

    @property
    def nome_exibicao(self) -> str:
        return self.nome_fantasia or self.razao_social

    def save(self, *args, **kwargs):
        # Texto vazio vira NULL: o banco aceita várias empresas sem CNPJ,
        # mas não aceitaria várias com CNPJ "" (a coluna é única).
        if not self.cnpj:
            self.cnpj = None
        super().save(*args, **kwargs)


class Socio(models.Model):
    """Sócio ou administrador da empresa, como aparece na Receita."""

    class FaixaEtaria(models.IntegerChoices):
        NAO_SE_APLICA = 0, "Não se aplica"
        ATE_12 = 1, "0 a 12 anos"
        DE_13_A_20 = 2, "13 a 20 anos"
        DE_21_A_30 = 3, "21 a 30 anos"
        DE_31_A_40 = 4, "31 a 40 anos"
        DE_41_A_50 = 5, "41 a 50 anos"
        DE_51_A_60 = 6, "51 a 60 anos"
        DE_61_A_70 = 7, "61 a 70 anos"
        DE_71_A_80 = 8, "71 a 80 anos"
        ACIMA_DE_80 = 9, "Acima de 80 anos"

    empresa = models.ForeignKey(Empresa, related_name="socios", on_delete=models.CASCADE)
    nome = models.CharField(max_length=255)
    qualificacao = models.CharField("qualificação", max_length=100, blank=True)
    faixa_etaria = models.PositiveSmallIntegerField(
        "faixa etária", choices=FaixaEtaria.choices, null=True, blank=True
    )
    data_entrada = models.DateField("data de entrada", null=True, blank=True)

    class Meta:
        verbose_name = "sócio"
        verbose_name_plural = "sócios"
        ordering = ["nome"]

    def __str__(self):
        return self.nome


class Telefone(models.Model):
    empresa = models.ForeignKey(Empresa, related_name="telefones", on_delete=models.CASCADE)
    ddd = models.CharField("DDD", max_length=2)
    numero = models.CharField("número", max_length=9)
    e164 = models.CharField(
        "número internacional", max_length=14, help_text="Ex.: +5561999998888"
    )
    eh_celular = models.BooleanField("é celular", default=False)
    origem = models.CharField(max_length=10, choices=Origem.choices, default=Origem.MANUAL)

    class Meta:
        verbose_name = "telefone"
        verbose_name_plural = "telefones"
        constraints = [
            models.UniqueConstraint(fields=["empresa", "e164"], name="telefone_unico_por_empresa"),
        ]

    def __str__(self):
        return f"({self.ddd}) {self.numero}"