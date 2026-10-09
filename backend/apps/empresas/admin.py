from django.contrib import admin

from .models import Empresa, Socio, Telefone


class SocioInline(admin.TabularInline):
    model = Socio
    extra = 0


class TelefoneInline(admin.TabularInline):
    model = Telefone
    extra = 0


@admin.register(Empresa)
class EmpresaAdmin(admin.ModelAdmin):
    list_display = ("nome_exibicao", "cnpj", "cnae_principal", "bairro", "porte", "situacao_cadastral")
    list_filter = ("porte", "situacao_cadastral", "opcao_mei", "opcao_simples", "uf")
    search_fields = ("cnpj", "razao_social", "nome_fantasia", "bairro", "cnae_principal")
    readonly_fields = ("criado_em", "atualizado_em")
    inlines = [SocioInline, TelefoneInline]
    fieldsets = (
        ("Identificação", {"fields": ("cnpj", "razao_social", "nome_fantasia")}),
        (
            "Receita Federal",
            {
                "fields": (
                    "cnae_principal",
                    "cnaes_secundarios",
                    "natureza_juridica",
                    "porte",
                    "capital_social",
                    "data_abertura",
                    "situacao_cadastral",
                    "opcao_simples",
                    "opcao_mei",
                )
            },
        ),
        (
            "Endereço",
            {"fields": ("logradouro", "numero", "complemento", "bairro", "cep", "municipio", "uf")},
        ),
        ("Contato", {"fields": ("email", "site")}),
        ("Localização", {"fields": ("latitude", "longitude", "distancia_asa_norte_km")}),
        ("Registro", {"fields": ("criado_em", "atualizado_em")}),
    )

    @admin.display(description="nome", ordering="nome_fantasia")
    def nome_exibicao(self, obj):
        return obj.nome_exibicao


@admin.register(Telefone)
class TelefoneAdmin(admin.ModelAdmin):
    list_display = ("e164", "empresa", "eh_celular", "origem")
    list_filter = ("eh_celular", "origem", "ddd")
    search_fields = ("e164", "numero", "empresa__razao_social", "empresa__nome_fantasia")