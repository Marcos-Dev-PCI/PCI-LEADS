from django.test import TestCase
from .models import Lead

class LeadModelTest(TestCase):
    def test_create_lead(self):
        lead = Lead.objects.create(
            name="Contato Teste",
            company="Empresa Teste",
            city="Brasília",
            state="DF",
        )
        self.assertEqual(lead.company, "Empresa Teste")
