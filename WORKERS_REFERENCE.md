# 👷 Workers - API Reference

## Endpoints Disponibles

### Base URL
```
/api/v1/workers
```

---

### Listar trabajadores (de un negocio o todos)

```
GET /workers
GET /workers?establishment_id=1&skip=0&limit=100

Response:
[
  {
    "trabajador_id": 1,
    "establecimiento_id": 1,
    "nombre": "Carlos",
    "apellido": "López",
    "email": "carlos@email.com",
    "telefono": "+51987654321",
    "foto_perfil": "https://...",
    "especialidad": "Corte moderno",
    "descripcion": "Especialista en cortes...",
    "activo": true,
    "fecha_contratacion": "2025-01-10",
    "fecha_creacion": "2025-01-16T10:00:00"
  }
]
```

---

### Ver un trabajador específico

```
GET /workers/{worker_id}

Response:
{
  "trabajador_id": 1,
  "establecimiento_id": 1,
  "nombre": "Carlos",
  ...
}
```

---

### Crear trabajador

```
POST /workers
Headers: Authorization: Bearer {token}

Body:
{
  "establecimiento_id": 1,
  "nombre": "Carlos",
  "apellido": "López",
  "email": "carlos@email.com",
  "telefono": "+51987654321",
  "foto_perfil": "https://...",
  "especialidad": "Corte moderno",
  "descripcion": "Especialista en cortes...",
  "activo": true,
  "fecha_contratacion": "2025-01-10"
}

Response: {trabajador_id: 1, ...}

Permisos: DUENO (sus negocios) + ADMIN
```

---

### Editar trabajador (PUT)

```
PUT /workers/{worker_id}
Headers: Authorization: Bearer {token}

Body:
{
  "nombre": "Carlos Eduardo",
  "especialidad": "Corte premium",
  "activo": false
}

Response: {trabajador_id: 1, nombre: "Carlos Eduardo", ...}

Permisos: DUENO (sus negocios) + ADMIN
```

---

### Editar trabajador (PATCH)

```
PATCH /workers/{worker_id}
Headers: Authorization: Bearer {token}

Body:
{
  "email": "carlos.nuevo@email.com"
}

Response: {trabajador_id: 1, email: "carlos.nuevo@email.com", ...}

Permisos: DUENO (sus negocios) + ADMIN
```

---

### Eliminar trabajador

```
DELETE /workers/{worker_id}
Headers: Authorization: Bearer {token}

Response: {"detail": "Worker deleted successfully"}

Permisos: DUENO (sus negocios) + ADMIN
```

---

## 🔐 Permisos

| Acción | CLIENTE | DUENO | ADMIN |
|--------|---------|-------|-------|
| GET /workers | ✅ | ✅ | ✅ |
| GET /workers/{id} | ✅ | ✅ | ✅ |
| POST /workers | ❌ | ✅ (sus negocios) | ✅ |
| PUT /workers/{id} | ❌ | ✅ (sus negocios) | ✅ |
| PATCH /workers/{id} | ❌ | ✅ (sus negocios) | ✅ |
| DELETE /workers/{id} | ❌ | ✅ (sus negocios) | ✅ |

---

## 📋 Campos

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| trabajador_id | int | Auto | ID (auto-generado) |
| establecimiento_id | int | ✅ | ID del negocio |
| nombre | string(50) | ✅ | Nombre del trabajador |
| apellido | string(50) | ✅ | Apellido del trabajador |
| email | string(100) | ❌ | Email (opcional) |
| telefono | string(20) | ❌ | Teléfono (opcional) |
| foto_perfil | string(255) | ❌ | URL de foto (opcional) |
| especialidad | string(100) | ❌ | Especialidad (opcional) |
| descripcion | text | ❌ | Descripción/bio (opcional) |
| activo | boolean | ✅ | Estado (default: true) |
| fecha_contratacion | date | ❌ | Fecha de contratación (opcional) |
| fecha_creacion | timestamp | Auto | Timestamp de creación |

---

## ✅ Validaciones

- `establecimiento_id` debe existir
- `nombre` y `apellido` son requeridos
- El owner solo puede gestionar workers de sus propios negocios
- Cascade delete: si se elimina el establecimiento, se eliminan sus workers

---

## 🧪 Ejemplo Completo

```bash
# 1. Owner crea un establecimiento
POST /api/v1/establishments
{
  "nombre": "Juan's Barbershop",
  ...
}
→ establishment_id = 1

# 2. Owner agrega un trabajador
POST /api/v1/workers
{
  "establecimiento_id": 1,
  "nombre": "Carlos",
  "apellido": "López",
  "especialidad": "Corte moderno",
  "fecha_contratacion": "2025-01-10"
}
→ trabajador_id = 1

# 3. Owner ve sus trabajadores
GET /api/v1/workers?establishment_id=1
→ [
  {
    "trabajador_id": 1,
    "nombre": "Carlos",
    "especialidad": "Corte moderno",
    ...
  }
]

# 4. Owner actualiza trabajador
PUT /api/v1/workers/1
{
  "especialidad": "Corte premium"
}

# 5. Owner elimina trabajador
DELETE /api/v1/workers/1
```

---

**Estado**: ✅ Completamente implementado
**Integración**: Listo para usar en frontend
**Base de datos**: Tabla `trabajador` con relación a `establecimiento`
