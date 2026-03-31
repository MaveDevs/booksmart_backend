# Guia para Levantar Entorno de Desarrollo (Docker)

Esta guia permite levantar Booksmart Backend en local usando Docker Compose.

## 1. Requisitos

- Docker Engine instalado
- Docker Compose v2 (`docker compose`)
- Acceso al repositorio
- Archivo `.env` compartido por el equipo

## 2. Preparacion inicial

1. Clona el repositorio.
2. Entra al directorio del backend:

```bash
cd booksmart_backend
```

3. Crea el archivo `.env` en la raiz del proyecto usando el archivo que te pase el equipo.

Notas:
- Para desarrollo con bypass de autenticacion, usa `JWT_AUTH_DISABLED=true`.
- En `docker-compose.dev.yml`, la API usa `DATABASE_URL` interna al contenedor (`db:3306`), por lo que no necesitas cambiar ese valor para Docker.

## 3. Levantar servicios

```bash
docker compose -f docker-compose.dev.yml up -d --build
```

Servicios esperados:
- API: `http://localhost:8000`
- Swagger: `http://localhost:8000/docs`
- MySQL: `localhost:3307` (host) -> `3306` (contenedor)
- Dozzle (logs): `http://localhost:8080`

## 4. Ejecutar migraciones

Siempre despues de levantar por primera vez o cuando haya cambios de modelos:

```bash
docker compose -f docker-compose.dev.yml exec api alembic upgrade head
```

## 5. Inicializar planes por defecto (recomendado)

Para habilitar flujo FREE/PREMIUM desde el inicio:

```bash
curl -X POST http://localhost:8000/api/v1/plans/initialize/defaults
```

Si `JWT_AUTH_DISABLED=false`, este endpoint requiere token admin.

## 6. Verificacion rapida

1. Verifica estado de contenedores:

```bash
docker compose -f docker-compose.dev.yml ps
```

2. Verifica logs del API:

```bash
docker compose -f docker-compose.dev.yml logs --tail=100 api
```

3. Prueba endpoint base:

```bash
curl http://localhost:8000/
```

## 7. Comandos utiles

Apagar entorno:

```bash
docker compose -f docker-compose.dev.yml down
```

Reiniciar entorno:

```bash
docker compose -f docker-compose.dev.yml down && docker compose -f docker-compose.dev.yml up -d
```

Recrear API para refrescar variables de entorno:

```bash
docker compose -f docker-compose.dev.yml up -d --force-recreate api
```

## 8. Troubleshooting rapido

- Error de puerto MySQL ocupado:
  - Cambia el puerto host en `docker-compose.dev.yml` (actual: `3307:3306`).

- La API no refleja cambios de `.env`:
  - Recreate del contenedor API (`--force-recreate api`).

- Migraciones no aplicadas:
  - Ejecuta `alembic upgrade head` dentro del contenedor API.

- Error de auth en desarrollo:
  - Verifica `JWT_AUTH_DISABLED=true` y reinicia API.
