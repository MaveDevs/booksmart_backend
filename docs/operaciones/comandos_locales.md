Guia completa:
docs/operaciones/GUIA_ENTORNO_DESARROLLO.md

Para apagar el entorno:
docker compose -f docker-compose.dev.yml down

Para volver a levantar el entorno (en segundo plano):
docker compose -f docker-compose.dev.yml up -d

Verificar que la base este saludable antes de migrar:
docker compose -f docker-compose.dev.yml ps
# Esperar que db aparezca como healthy

Para ejecutar nuevas migraciones (si modificas los modelos en el futuro):
docker compose -f docker-compose.dev.yml exec api alembic upgrade head
