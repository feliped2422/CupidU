from unittest.mock import MagicMock, patch

from rest_framework.test import APISimpleTestCase


def _resposta_com_sessao():
    sessao = MagicMock(access_token="token-a", refresh_token="token-r")
    return MagicMock(session=sessao)


class VerifyOtpTests(APISimpleTestCase):
    url = "/api/auth/verify-otp"
    dados = {"email": "joao@sempreunama.com.br", "token": "123456"}

    @patch("app_CupidU.views.novo_cliente")
    def test_codigo_correto_devolve_tokens(self, novo_cliente):
        novo_cliente.return_value.auth.verify_otp.return_value = _resposta_com_sessao()
        r = self.client.post(self.url, self.dados, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.json()["access_token"], "token-a")

    @patch("app_CupidU.views.novo_cliente")
    def test_codigo_recusado_devolve_400(self, novo_cliente):
        novo_cliente.return_value.auth.verify_otp.side_effect = Exception("expired")
        r = self.client.post(self.url, self.dados, format="json")
        self.assertEqual(r.status_code, 400)

    @patch("app_CupidU.views.novo_cliente")
    def test_tenta_o_tipo_signup_se_o_email_falhar(self, novo_cliente):
        novo_cliente.return_value.auth.verify_otp.side_effect = [
            Exception("tipo errado"),
            _resposta_com_sessao(),
        ]
        r = self.client.post(self.url, self.dados, format="json")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(novo_cliente.return_value.auth.verify_otp.call_count, 2)

    @patch("app_CupidU.views.novo_cliente")
    def test_formato_invalido_nem_chama_o_supabase(self, novo_cliente):
        for token in ("12345", "1234567", "12ab56", ""):
            r = self.client.post(
                self.url,
                {"email": "joao@sempreunama.com.br", "token": token},
                format="json",
            )
            self.assertEqual(r.status_code, 400)
        novo_cliente.assert_not_called()

    @patch("app_CupidU.views.novo_cliente")
    def test_email_fora_do_dominio_devolve_400(self, novo_cliente):
        r = self.client.post(
            self.url, {"email": "a@gmail.com", "token": "123456"}, format="json"
        )
        self.assertEqual(r.status_code, 400)
        novo_cliente.assert_not_called()


class ResendOtpTests(APISimpleTestCase):
    url = "/api/auth/resend-otp"

    @patch("app_CupidU.views.novo_cliente")
    def test_reenvio_ok(self, novo_cliente):
        r = self.client.post(
            self.url, {"email": "joao@sempreunama.com.br"}, format="json"
        )
        self.assertEqual(r.status_code, 200)
        novo_cliente.return_value.auth.resend.assert_called_once()

    @patch("app_CupidU.views.novo_cliente")
    def test_reenvio_recusado_devolve_400(self, novo_cliente):
        novo_cliente.return_value.auth.resend.side_effect = Exception("rate limit")
        r = self.client.post(
            self.url, {"email": "joao@sempreunama.com.br"}, format="json"
        )
        self.assertEqual(r.status_code, 400)

    @patch("app_CupidU.views.novo_cliente")
    def test_email_fora_do_dominio_devolve_400(self, novo_cliente):
        r = self.client.post(self.url, {"email": "a@gmail.com"}, format="json")
        self.assertEqual(r.status_code, 400)
        novo_cliente.assert_not_called()