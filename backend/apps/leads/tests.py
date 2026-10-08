from django.contrib.auth.models import User
from rest_framework.test import APITestCase


class AutenticacaoTest(APITestCase):
    def setUp(self):
        User.objects.create_user("pedro", "pedro@pci.com", "senha-forte-123")

    def fazer_login(self, senha="senha-forte-123"):
        return self.client.post(
            "/api/auth/login/",
            {"username": "pedro", "password": senha},
            format="json",
        )

    def test_api_sem_token_retorna_401(self):
        resposta = self.client.get("/api/leads/")
        self.assertEqual(resposta.status_code, 401)

    def test_login_correto_retorna_token(self):
        resposta = self.fazer_login()
        self.assertEqual(resposta.status_code, 200)
        self.assertIn("token", resposta.data)

    def test_login_com_senha_errada_retorna_400(self):
        resposta = self.fazer_login(senha="errada")
        self.assertEqual(resposta.status_code, 400)

    def test_api_com_token_funciona(self):
        token = self.fazer_login().data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        resposta = self.client.get("/api/leads/")
        self.assertEqual(resposta.status_code, 200)

    def test_me_retorna_usuario_logado(self):
        token = self.fazer_login().data["token"]
        self.client.credentials(HTTP_AUTHORIZATION=f"Token {token}")
        resposta = self.client.get("/api/auth/me/")
        self.assertEqual(resposta.status_code, 200)
        self.assertEqual(resposta.data["username"], "pedro")