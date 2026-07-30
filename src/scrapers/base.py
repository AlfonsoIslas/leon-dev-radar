"""
Clase base para todos los scrapers de vacantes.

Cada portal (Computrabajo, OCC, etc.) implementa su propia subclase
que solo necesita definir `scrape()` y devolver una lista de dicts
con las llaves: titulo, empresa, url, ubicacion (opcional).
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from playwright.async_api import async_playwright


@dataclass
class Vacante:
    titulo: str
    empresa: str
    url: str
    ubicacion: str = ""
    fuente: str = ""

    def hash_unico(self) -> str:
        """Hash para detectar duplicados: mismo puesto+empresa+fuente.

        Deliberadamente NO incluye la URL completa: portales como
        Indeed regeneran parámetros de tracking en cada carga de
        página, así que la misma vacante tendría una URL distinta
        en cada corrida y el dedupe nunca funcionaría.
        """
        import hashlib
        base = f"{self.titulo}|{self.empresa}|{self.fuente}".lower().strip()
        return hashlib.sha256(base.encode()).hexdigest()


class BaseScraper(ABC):
    """Todo scraper concreto hereda de aquí."""

    nombre_fuente: str = "base"

    def __init__(self, headless: bool = True, timeout_ms: int = 15000):
        self.headless = headless
        self.timeout_ms = timeout_ms

    @abstractmethod
    async def scrape(self) -> list[Vacante]:
        """Debe devolver la lista de vacantes encontradas en esta corrida."""
        raise NotImplementedError

    async def _nueva_pagina(self, playwright):
        """Helper: abre browser + contexto + page ya configurados."""
        browser = await playwright.chromium.launch(headless=self.headless)
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/124.0 Safari/537.36"
            )
        )
        page = await context.new_page()
        page.set_default_timeout(self.timeout_ms)
        return browser, page

    async def run(self) -> list[Vacante]:
        """Punto de entrada único: maneja errores para que un scraper
        roto no tumbe el pipeline completo."""
        try:
            return await self.scrape()
        except Exception as exc:
            print(f"[{self.nombre_fuente}] error durante scraping: {exc}")
            return []


__all__ = ["BaseScraper", "Vacante", "async_playwright"]
