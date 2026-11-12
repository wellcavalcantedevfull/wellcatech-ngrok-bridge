from pyngrok import ngrok


class TunnelManager:
    """Gerencia o ciclo de vida do túnel Ngrok."""

    def __init__(self):
        self.tunel_ativo = None

    def definir_token(self, token: str) -> None:
        if token:
            ngrok.set_auth_token(token)

    def conectar(self, porta: int, protocolo: str, token: str = "") -> str:
        """Abre o túnel e retorna o endereço formatado para o cliente."""
        if token:
            self.definir_token(token)

        self.tunel_ativo = ngrok.connect(addr=porta, proto=protocolo)
        url_publica = self.tunel_ativo.public_url

        if protocolo == "tcp":
            return url_publica.replace("tcp://", "")
        return url_publica

    def desconectar(self) -> None:
        """Encerra o túnel ativo e finaliza o processo em segundo plano."""
        if self.tunel_ativo:
            try:
                ngrok.disconnect(self.tunel_ativo.public_url)
                ngrok.kill()
            except Exception:
                pass
            finally:
                self.tunel_ativo = None