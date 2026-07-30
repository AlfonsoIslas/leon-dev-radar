import asyncio
from .scrapers.computrabajo import ComputrabajoScraper
from .storage.db import init_db, ya_vista, guardar_vacante
from .notifier.telegram import notificar_vacante, notificar_resumen
from .config import settings
from .scrapers.indeed import IndeedScraper



# Agrega aquí más scrapers conforme los vayas construyendo
SCRAPERS = [ComputrabajoScraper, IndeedScraper]


async def ejecutar_pipeline():
    settings.validar()
    init_db()

    nuevas = []

    for ScraperCls in SCRAPERS:
        scraper = ScraperCls(headless=True)
        vacantes = await scraper.run()
        print(f"[{scraper.nombre_fuente}] encontradas: {len(vacantes)}")

        for vacante in vacantes:
            if ya_vista(vacante.hash_unico()):
                continue
            guardar_vacante(vacante)
            notificar_vacante(vacante)
            nuevas.append(vacante)

    notificar_resumen(len(nuevas))
    print(f"Pipeline terminado. Vacantes nuevas: {len(nuevas)}")


def main():
    asyncio.run(ejecutar_pipeline())


if __name__ == "__main__":
    main()
