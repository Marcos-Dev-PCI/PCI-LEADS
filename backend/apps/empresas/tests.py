from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction
from django.test import TestCase

from .models import Empresa, Socio, Telefone


class EmpresaTest(TestCase):
    def test_nome_exibicao_usa_nome_fantasia(self):
        empresa = Empresa.objects.create(razao_social="QUENTE LTDA", nome_fantasia="Quente Papelaria")
        self.assertEqual(empresa.nome_exibicao, "Quente Papelaria")

    def test_nome_exibicao_usa_razao_social_sem_nome_fantasia(self):
        empresa = Empresa.objects.create(razao_social="QUENTE LTDA")
        self.assertEqual(empresa.nome_exibicao, "QUENTE LTDA")

    def test_varias_empresas_sem_cnpj_sao_permitidas(self):
        Empresa.objects.create(razao_social="Sem CNPJ 1", cnpj="")
        Empresa.objects.create(razao_social="Sem CNPJ 2")
        self.assertEqual(Empresa.objects.filter(cnpj__isnull=True).count(), 2)

    def test_cnpj_repetido_nao_e_permitido(self):
        Empresa.objects.create(cnpj="12345678000190")
        with self.assertRaises(IntegrityError), transaction.atomic():
            Empresa.objects.create(cnpj="12345678000190")

    def test_cnpj_com_formato_errado_e_rejeitado(self):
        empresa = Empresa(cnpj="12.345.678/0001-90")
        with self.assertRaises(ValidationError):
            empresa.full_clean()

    def test_apagar_empresa_apaga_socios_e_telefones(self):
        empresa = Empresa.objects.create(cnpj="12345678000190")
        Socio.objects.create(empresa=empresa, nome="MARIA DA SILVA", faixa_etaria=4)
        Telefone.objects.create(empresa=empresa, ddd="61", numero="999998888", e164="+5561999998888")
        empresa.delete()
        self.assertEqual(Socio.objects.count(), 0)
        self.assertEqual(Telefone.objects.count(), 0)


class TelefoneTest(TestCase):
    def setUp(self):
        self.empresa = Empresa.objects.create(cnpj="12345678000190")

    def criar_telefone(self, empresa):
        return Telefone.objects.create(
            empresa=empresa, ddd="61", numero="999998888", e164="+5561999998888", eh_celular=True
        )

    def test_mesmo_telefone_na_mesma_empresa_nao_e_permitido(self):
        self.criar_telefone(self.empresa)
        with self.assertRaises(IntegrityError), transaction.atomic():
            self.criar_telefone(self.empresa)

    def test_mesmo_telefone_em_empresas_diferentes_e_permitido(self):
        outra = Empresa.objects.create(cnpj="98765432000110")
        self.criar_telefone(self.empresa)
        self.criar_telefone(outra)
        self.assertEqual(Telefone.objects.count(), 2)

    def test_acessar_socios_e_telefones_pela_empresa(self):
        Socio.objects.create(empresa=self.empresa, nome="JOÃO SOUZA")
        self.criar_telefone(self.empresa)
        self.assertEqual(self.empresa.socios.count(), 1)
        self.assertEqual(self.empresa.telefones.count(), 1)