"""Punto de entrada. En local: python -m src.main
Dentro del contenedor, esto es lo que dispara el cron."""

from .pipeline import main

if __name__ == "__main__":
    main()
