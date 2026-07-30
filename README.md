# León Dev Radar 🔎

Bot que scrapea vacantes de desarrollador junior/trainee en León/remoto
y avisa por Telegram cuando aparece algo nuevo.

## Cómo funciona
1. `ComputrabajoScraper` (Playwright) visita el portal y extrae vacantes
2. Cada vacante se hashea (título+empresa+url) para detectar duplicados
3. Solo las vacantes nuevas se guardan en SQLite y se notifican por Telegram

## Setup local (sin Docker)
```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
playwright install chromium
cp .env.example .env   # llena TELEGRAM_BOT_TOKEN y TELEGRAM_CHAT_ID
python -m src.main
```

## Con Docker
```bash
cp .env.example .env   # llena tus credenciales
docker compose up --build
```

## Automatizar la corrida
Opción recomendada (gratis, sin mantener servidor):
crea un workflow de **GitHub Actions** con `on: schedule` (ej. cada 6 horas)
que construya la imagen y corra `python -m src.main`.

## Agregar otro portal
1. Crea `src/scrapers/nuevo_portal.py` heredando de `BaseScraper`
2. Implementa `async def scrape(self) -> list[Vacante]`
3. Agrégalo a la lista `SCRAPERS` en `src/pipeline.py`

## Roadmap
- [ ] Scraper de OCC
- [ ] Filtro configurable de palabras clave vía .env
- [ ] Deploy con GitHub Actions schedule
