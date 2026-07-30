import requests
from ..config import settings


def notificar_vacante(vacante) -> None:
    """Envía un mensaje formateado por Telegram para una vacante nueva."""
    texto = (
        f"🟢 *Nueva vacante detectada*\n\n"
        f"*{vacante.titulo}*\n"
        f"Empresa: {vacante.empresa}\n"
        f"Ubicación: {vacante.ubicacion or 'N/D'}\n"
        f"Fuente: {vacante.fuente}\n"
        f"{vacante.url}"
    )
    _enviar_mensaje(texto)


def notificar_resumen(total_nuevas: int) -> None:
    if total_nuevas == 0:
        return
    _enviar_mensaje(f"🔎 Corrida completada: {total_nuevas} vacante(s) nueva(s) encontradas.")


def _enviar_mensaje(texto: str) -> None:
    url = f"https://api.telegram.org/bot{settings.telegram_bot_token}/sendMessage"
    payload = {
        "chat_id": settings.telegram_chat_id,
        "text": texto,
        "parse_mode": "Markdown",
        "disable_web_page_preview": True,
    }
    try:
        resp = requests.post(url, json=payload, timeout=10)
        resp.raise_for_status()
    except requests.RequestException as exc:
        print(f"Error enviando notificación a Telegram: {exc}")
