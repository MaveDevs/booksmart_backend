Para apagar el entorno:
docker compose -f docker-compose.dev.yml down

Para volver a levantar el entorno (en segundo plano):
docker compose -f docker-compose.dev.yml up -d

Para ejecutar nuevas migraciones (si modificas los modelos en el futuro):
docker compose -f docker-compose.dev.yml exec api alembic upgrade head
