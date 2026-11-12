import json
import os
import sys

CONFIG_FILE = "config_ngrok.json"


def caminho_recurso(caminho_relativo: str) -> str:
    """Retorna o caminho correto do arquivo em dev ou empacotado no .exe."""
    base_path = getattr(sys, "_MEIPASS", os.path.abspath("."))
    return os.path.join(base_path, caminho_relativo)


def carregar_token() -> str:
    """Lê o AuthToken salvo no arquivo JSON local."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f).get("authtoken", "")
        except Exception:
            return ""
    return ""


def salvar_token(token: str) -> None:
    """Salva o AuthToken no arquivo JSON local."""
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"authtoken": token}, f, indent=2)