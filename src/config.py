import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class Settings:
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "")

    def validar(self):
        faltantes = [
            nombre
            for nombre, valor in [
                ("TELEGRAM_BOT_TOKEN", self.telegram_bot_token),
                ("TELEGRAM_CHAT_ID", self.telegram_chat_id),
            ]
            if not valor
        ]
        if faltantes:
            raise RuntimeError(
                f"Faltan variables de entorno: {', '.join(faltantes)}. "
                f"Revisa tu archivo .env (usa .env.example como guía)."
            )


settings = Settings()
