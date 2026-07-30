"""
Scraper de Computrabajo México, filtrado a vacantes de
desarrollador junior/trainee en León o remoto.

NOTA: los selectores CSS de sitios como Computrabajo cambian con
frecuencia. Si este scraper deja de traer resultados, lo primero
es abrir la URL en el navegador, inspeccionar el HTML actual y
actualizar los selectores de abajo — es normal y parte del
mantenimiento de cualquier scraper real.
"""

from playwright.async_api import async_playwright
from .base import BaseScraper, Vacante

BUSQUEDA = "desarrollador junior"
UBICACION = "leon"
URL_BASE = (
    f"https://mx.computrabajo.com/trabajo-de-{BUSQUEDA.replace(' ', '-')}"
    f"-en-{UBICACION}"
)

PALABRAS_CLAVE_JUNIOR = ["junior", "jr", "trainee", "practicante", "becario"]


class ComputrabajoScraper(BaseScraper):
    nombre_fuente = "computrabajo"

    async def scrape(self) -> list[Vacante]:
        vacantes: list[Vacante] = []

        async with async_playwright() as p:
            browser, page = await self._nueva_pagina(p)
            try:
                await page.goto(URL_BASE, wait_until="domcontentloaded")

                # Cada tarjeta de resultado suele tener esta clase;
                # ajustar si Computrabajo cambia su HTML.
                tarjetas = await page.query_selector_all("article.box_offer")

                for tarjeta in tarjetas:
                    titulo_el = await tarjeta.query_selector("h2 a")
                    empresa_el = await tarjeta.query_selector("p.dFlex a")

                    if not titulo_el:
                        continue

                    titulo = (await titulo_el.inner_text()).strip()
                    href = await titulo_el.get_attribute("href") or ""
                    url = href if href.startswith("http") else f"https://mx.computrabajo.com{href}"
                    empresa = (await empresa_el.inner_text()).strip() if empresa_el else "N/D"

                    if not self._es_relevante(titulo):
                        continue

                    vacantes.append(
                        Vacante(
                            titulo=titulo,
                            empresa=empresa,
                            url=url,
                            ubicacion="León / remoto",
                            fuente=self.nombre_fuente,
                        )
                    )
            finally:
                await browser.close()

        return vacantes

    @staticmethod
    def _es_relevante(titulo: str) -> bool:
        """Filtra solo puestos junior/entry-level relacionados a dev."""
        t = titulo.lower()
        es_dev = any(p in t for p in ["desarroll", "programador", "developer", "software"])
        es_junior = any(p in t for p in PALABRAS_CLAVE_JUNIOR)
        return es_dev and es_junior


# Prueba rápida manual: python -m src.scrapers.computrabajo
if __name__ == "__main__":
    import asyncio

    async def _main():
        scraper = ComputrabajoScraper(headless=False)
        resultados = await scraper.run()
        for v in resultados:
            print(f"- {v.titulo} @ {v.empresa} -> {v.url}")
        print(f"\nTotal: {len(resultados)} vacantes relevantes")

    asyncio.run(_main())
