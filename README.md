# León Dev Radar 🔎

Bot que scrapea vacantes de desarrollador junior/trainee en León/remoto
(Computrabajo e Indeed) y avisa por Telegram cuando aparece algo nuevo.
Corre solo, cada 6 horas, vía GitHub Actions — sin servidor que mantener.

## Cómo funciona
1. `ComputrabajoScraper` e `IndeedScraper` (Playwright) visitan cada
   portal y extraen vacantes que coincidan con el filtro junior/trainee
2. Cada vacante se hashea (`título+empresa+fuente`) para detectar
   duplicados frente a lo ya notificado
3. Solo las vacantes nuevas se guardan en SQLite y se notifican por
   Telegram
4. Un workflow de GitHub Actions repite este proceso cada 6 horas,
   persistiendo la base de datos entre corridas mediante artifacts

## Setup local (sin Docker)
```bash
python -m venv .venv && source .venv/bin/activate   # en Windows: .venv\Scripts\activate
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

## Automatización con GitHub Actions
El workflow vive en `.github/workflows/scraping.yml` y corre cada 6
horas (`cron: "0 */6 * * *"`), además de poder dispararse manualmente
desde la pestaña **Actions** del repo.

Como cada corrida de GitHub Actions empieza en un contenedor limpio,
la base de datos SQLite viaja entre corridas como **artifact**: se
descarga al inicio (con `dawidd6/action-download-artifact`, que sí
puede leer artifacts de corridas anteriores, a diferencia de la
acción oficial) y se vuelve a subir al final.

**Requisito:** configura estos secrets en *Settings → Secrets and
variables → Actions*:
- `TELEGRAM_BOT_TOKEN`
- `TELEGRAM_CHAT_ID`

## Agregar otro portal
1. Crea `src/scrapers/nuevo_portal.py` heredando de `BaseScraper`
2. Implementa `async def scrape(self) -> list[Vacante]`
3. Agrégalo a la lista `SCRAPERS` en `src/pipeline.py`

## Notas de diseño (bugs reales que aparecieron y cómo se resolvieron)
- **SQLite no crea su carpeta contenedora sola** — `data/` se asegura
  con `os.makedirs` antes de abrir la conexión (`storage/db.py`)
- **Markdown de Telegram rompe con títulos que traen paréntesis o
  guiones bajos** (comunes en vacantes reales, ej. "Full Stack") —
  se optó por texto plano en vez de parsear/escapar cada caso
- **Indeed regenera parámetros de tracking en la URL en cada carga
  de página** — el hash de dedupe originalmente incluía la URL
  completa, lo que hacía que la misma vacante pareciera "nueva" en
  cada corrida; se resolvió hasheando solo `título+empresa+fuente`
- **Indeed detecta automatización con más frecuencia que
  Computrabajo** — el scraper corre con espera aleatoria entre
  acciones y detecta si la respuesta es un challenge/captcha para
  salir limpio en vez de fallar

## Roadmap
- [ ] Scraper de OCC
- [ ] Filtro configurable de palabras clave vía .env