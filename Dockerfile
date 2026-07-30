FROM python:3.12-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && playwright install --with-deps chromium

COPY . .

RUN mkdir -p data

# Corre el pipeline una vez al arrancar; el scheduling real
# lo hace GitHub Actions o el cron del host (ver README)
CMD ["python", "-m", "src.main"]
