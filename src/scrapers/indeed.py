"""
Scraper de Indeed México, filtrado a vacantes de desarrollador
junior/trainee en León o remoto.

Indeed es más estricto detectando automatización que Computrabajo:
- a veces exige resolver un captcha si detecta tráfico "no humano"
- cambia su HTML con más frecuencia
- puede bloquear temporalmente una IP que haga muchas requests seguidas

Por eso este scraper:
- usa un user-agent realista (heredado de BaseScraper)
- agrega una pequeña espera aleatoria entre acciones
- si Indeed te muestra un captcha, este scraper simplemente no
  encontrará resultados esa corrida — no está roto, es Indeed
  bloqueando. Si pasa seguido, considera correrlo con menor
  frecuencia (ej. cada 12h en vez de 6h) en el workflow de GitHub
  Actions, o quitarlo del pipeline y quedarte solo con Computrabajo.
"""

import random
import asyncio
from playwright.async_api import async_playwright
from .base import BaseScraper, Vacante

BUSQUEDA = "desarrollador junior"
UBICACION = "León, Guanajuato"
URL_BASE = (
    f"https://mx.indeed.com/jobs?q={BUSQUEDA.replace(' ', '+')}"
    f"&l={UBICACION.replace(' ', '+').replace(',', '%2C')}"
)

PALABRAS_CLAVE_JUNIOR = ["junior", "jr", "trainee", "practicante", "becario"]


class IndeedScraper(BaseScraper):
    nombre_fuente = "indeed"

    async def scrape(self) -> list[Vacante]:
        vacantes: list[Vacante] = []

        async with async_playwright() as p:
            browser, page = await self._nueva_pagina(p)
            try:
                await page.goto(URL_BASE, wait_until="domcontentloaded")

                await page.wait_for_timeout(random.randint(1500, 3000))

                if await self._hay_bloqueo(page):
                    print("[indeed] posible captcha/bloqueo detectado, "
                          "se omite esta corrida")
                    return []

                tarjetas = await page.query_selector_all(
                    "div.job_seen_beacon, td.resultContent"
                )

                for tarjeta in tarjetas:
                    titulo_el = await tarjeta.query_selector(
                        "h2.jobTitle a, a.jcs-JobTitle"
                    )
                    empresa_el = await tarjeta.query_selector(
                        "span[data-testid='company-name']"
                    )

                    if not titulo_el:
                        continue

                    titulo = (await titulo_el.inner_text()).strip()
                    href = await titulo_el.get_attribute("href") or ""
                    url = href if href.startswith("http") else f"https://mx.indeed.com{href}"
                    empresa = (
                        (await empresa_el.inner_text()).strip()
                        if empresa_el else "N/D"
                    )

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
    async def _hay_bloqueo(page) -> bool:
        """Heurística simple: si el título de la página o el body
        mencionan verificación humana, probablemente es un captcha."""
        titulo_pagina = (await page.title()).lower()
        señales = ["verify", "captcha", "unusual traffic", "human"]
        return any(s in titulo_pagina for s in señales)

    @staticmethod
    def _es_relevante(titulo: str) -> bool:
        t = titulo.lower()
        es_dev = any(p in t for p in ["desarroll", "programador", "developer", "software"])
        es_junior = any(p in t for p in PALABRAS_CLAVE_JUNIOR)
        return es_dev and es_junior


if __name__ == "__main__":

    async def _main():
        scraper = IndeedScraper(headless=False)
        resultados = await scraper.run()
        for v in resultados:
            print(f"- {v.titulo} @ {v.empresa} -> {v.url}")
        print(f"\nTotal: {len(resultados)} vacantes relevantes")

    asyncio.run(_main())