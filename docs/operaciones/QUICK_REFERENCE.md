# 🚀 Quick Reference - API Endpoints para Owner Dashboard

## 📱 Base URL
```
http://localhost:8000/api/v1/
```

## 🔐 Authentication
```
Header: Authorization: Bearer {access_token}

Login:
POST /login/access-token
{
  "username": "juan@email.com",
  "password": "seguro123"
}
→ Devuelve: {"access_token": "...", "token_type": "bearer"}
```

---

## 🏢 ESTABLISHMENTS

### Listar todos mis negocios
```
GET /establishments?user_id=1
Response: [
  {
    "establecimiento_id": 1,
    "usuario_id": 1,
    "nombre": "Juan's Barbershop",
    "descripcion": "...",
    "direccion": "Calle 5 #123",
    "latitud": -12.0432,
    "longitud": -77.0282,
    "telefono": "+51987654321",
    "activo": true
  }
]
```

### Ver un negocio específico
```
GET /establishments/1
Response: {id, nombre, descripcion, ...}
```

### Crear negocio
```
POST /establishments
{
  "nombre": "Juan's Barbershop",
  "descripcion": "Barbería moderna",
  "direccion": "Calle 5 #123",
  "latitud": -12.0432,
  "longitud": -77.0282,
  "telefono": "+51987654321"
}
Response: {establecimiento_id: 1, ...}
```

### Editar negocio
```
PUT /establishments/1
{
  "nombre": "Juan's Premium Barbership",
  "telefono": "+51987654322"
}
```

### Borrar negocio
```
DELETE /establishments/1
```

---

## 🛎️ SERVICES

### Listar servicios de un negocio
```
GET /services?establishment_id=1
Response: [
  {
    "servicio_id": 1,
    "establecimiento_id": 1,
    "nombre": "Corte Clásico",
    "descripcion": "Corte con técnica...",
    "duracion": 30,
    "precio": 40.00,
    "activo": true
  }
]
```

### Crear servicio
```
POST /services
{
  "establecimiento_id": 1,
  "nombre": "Corte Clásico",
  "descripcion": "Corte moderno",
  "duracion": 30,
  "precio": 40.00
}
```

### Editar servicio
```
PUT /services/1
{
  "precio": 45.00,
  "duracion": 35
}
```

### Borrar servicio
```
DELETE /services/1
```

---

## 📅 AGENDAS (Horarios - Crear 7 veces, uno por día)

### Listar horarios
```
GET /agendas?establishment_id=1
Response: [
  {
    "agenda_id": 1,
    "establecimiento_id": 1,
    "dia_semana": "LUNES",
    "hora_inicio": "09:00",
    "hora_fin": "18:00"
  },
  ...
  (7 días)
]
```

### Crear horario para un día
```
POST /agendas
{
  "establecimiento_id": 1,
  "dia_semana": "LUNES",
  "hora_inicio": "09:00",
  "hora_fin": "18:00"
}
```

### Editar horario
```
PUT /agendas/1
{
  "hora_inicio": "08:00",
  "hora_fin": "19:00"
}
```

### Borrar horario (cerrar día)
```
DELETE /agendas/1
```

---

## 📋 APPOINTMENTS (Citas)

### Listar citas de mi negocio
```
GET /appointments?establishment_id=1
Response: [
  {
    "cita_id": 1,
    "cliente_id": 5,
    "servicio_id": 1,
    "fecha": "2025-01-30",
    "hora_inicio": "10:00",
    "hora_fin": "10:30",
    "estado": "PENDIENTE",
    "fecha_creacion": "2025-01-16T10:00:00"
  }
]
```

### Ver detalle de una cita
```
GET /appointments/1
Response: {id, cliente_id, servicio_id, fecha, hora_inicio, ...}
```

### Confirmar cita (PENDIENTE → CONFIRMADA)
```
PUT /appointments/1
{
  "estado": "CONFIRMADA"
}
```

### Marcar cita como completada
```
PUT /appointments/1
{
  "estado": "COMPLETADA"
}
```

### Cancelar cita
```
PUT /appointments/1
{
  "estado": "CANCELADA"
}
```

---

## 💬 MESSAGES (Chat por cita)

### Ver mensajes de una cita
```
GET /messages?appointment_id=1
Response: [
  {
    "mensaje_id": 1,
    "cita_id": 1,
    "emisor_id": 5,
    "contenido": "Hola, ¿a que hora?",
    "fecha_envio": "2025-01-16T10:00:00"
  }
]
```

### Enviar mensaje
```
POST /messages
{
  "cita_id": 1,
  "contenido": "Hola Juan, ¿qué color prefieres?"
}
```

---

## ⭐ RATINGS (Reseñas)

### Ver reseñas del negocio
```
GET /ratings?establishment_id=1
Response: [
  {
    "resena_id": 1,
    "usuario_id": 5,
    "establecimiento_id": 1,
    "calificacion": 5,
    "comentario": "¡Excelente servicio!",
    "fecha": "2025-01-15T14:00:00"
  }
]
```

**Nota:** Solo CLIENTE puede crear/editar reseña
**Nota:** OWNER solo puede LEER

---

## 👤 PROFILES (Perfil del negocio)

### Ver perfil del negocio
```
GET /profiles/1
Response: {
  "profile_id": 1,
  "establecimiento_id": 1,
  "logo_url": "https://...",
  "portada_url": "https://...",
  "descripcion_larga": "Somos la mejor..."
}
```

### Crear perfil
```
POST /profiles
{
  "establecimiento_id": 1,
  "logo_url": "https://...",
  "portada_url": "https://...",
  "descripcion_larga": "Descripción pública..."
}
```

### Editar perfil
```
PUT /profiles/1
{
  "logo_url": "https://nuevo...",
  "descripcion_larga": "Nueva descripción..."
}
```

---

## 💳 SUBSCRIPTIONS (Solo Lectura para Owner)

### Ver suscripción del negocio
```
GET /subscriptions?establishment_id=1
Response: {
  "suscripcion_id": 1,
  "establecimiento_id": 1,
  "plan_id": 1,
  "estado": "ACTIVA",
  "fecha_inicio": "2025-01-01",
  "fecha_expiracion": "2025-02-01"
}
```

**Nota:** OWNER solo puede LEER
**Nota:** ADMIN es quien crea/actualiza suscripciones

---

## 🔔 NOTIFICATIONS

### Ver mis notificaciones
```
GET /notifications?user_id=1
Response: [
  {
    "notificacion_id": 1,
    "usuario_id": 1,
    "mensaje": "Nueva cita de Juan",
    "leida": false,
    "fecha_creacion": "2025-01-16T10:00:00"
  }
]
```

### Marcar como leída
```
PUT /notifications/1
{
  "leida": true
}
```

---

## 📊 Queries Útiles (Llamadas Combinadas)

### Dashboard - Traer todo lo esencial
```javascript
// 1. Mis establecimientos
GET /establishments?user_id=1

// Para cada establecimiento:
// 2. Citas de hoy
GET /appointments?establishment_id=1&date=2025-01-16

// 3. Rating promedio
GET /ratings?establishment_id=1

// 4. Suscripción
GET /subscriptions?establishment_id=1

// Agrupar datos en frontend
const dashboard = {
  establishments: [...],
  appointmentsToday: [
    { establishment_id: 1, appointments: [...] },
    { establishment_id: 2, appointments: [...] }
  ],
  ratings: { establishment_id: 1, avg: 4.8, count: 23 },
  subscriptions: [...]
}
```

### Pantalla de Negocio
```javascript
// 1. Establecimiento
GET /establishments/1

// 2. Servicios
GET /services?establishment_id=1

// 3. Horarios
GET /agendas?establishment_id=1

// 4. Citas (todas)
GET /appointments?establishment_id=1

// 5. Reseñas
GET /ratings?establishment_id=1

// 6. Perfil
GET /profiles/1

// 7. Suscripción
GET /subscriptions?establishment_id=1
```

---

## ✅ Estados de Cita

```
PENDIENTE   → Cliente reservó, espera confirmación
CONFIRMADA  → Owner confirmó, cliente confirmado
COMPLETADA  → Cita done, cliente puede dejar review
CANCELADA   → Owner o cliente canceló
```

---

## 📍 Días de Semana en Agenda
```
LUNES
MARTES
MIERCOLES
JUEVES
VIERNES
SABADO
DOMINGO
```

---

## 🎭 Roles en Sistema
```
CLIENTE  → Crea/ve sus citas, deja reseñas
DUENO    → Crea negocios, servicios, confirma citas
ADMIN    → Acceso a todo, maneja suscripciones
```

---

## 🔐 Permisos por Rol (Owner)

```
✅ GET   /establishments              (mis negocios)
✅ POST  /establishments              (crear)
✅ PUT   /establishments/id           (editar mío)
✅ DELETE /establishments/id          (borrar mío)

✅ GET   /services (establishment_id=mío)
✅ POST  /services (establ_id=mío)
✅ PUT   /services/id (de mi neg)
✅ DELETE /services/id (de mi neg)

✅ GET   /appointments (establishment_id=mío)
✅ PUT   /appointments/id (estado, de mi neg)
❌ POST  /appointments (cliente hace esto)
❌ DELETE /appointments (cliente cancela)

✅ GET   /agendas (establishment_id=mío)
✅ POST  /agendas (mi neg)
✅ PUT   /agendas/id (mío)
✅ DELETE /agendas/id (mío)

✅ GET   /messages (de mis citas)
✅ POST  /messages (en mis citas)

✅ GET   /ratings (establishment_id=mío)
❌ POST  /ratings (solo cliente)

✅ GET   /profiles/id (mío)
✅ POST  /profiles (mío)
✅ PUT   /profiles/id (mío)

✅ GET   /subscriptions (mío, read-only)
❌ POST  /subscriptions (solo admin)
❌ PUT   /subscriptions (solo admin)
```

---

## 🚨 Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| 401 Unauthorized | Token inválido/expirado | Login de nuevo |
| 403 Forbidden | No tienes permisos | Verifica rol (DUENO) |
| 404 Not Found | Recurso no existe | Verifica ID |
| 422 Unprocessable Entity | Datos inválidos | Revisa formato |
| 409 Conflict | Duplicado (ej: review x2) | Ya existe |

---

## 💡 Tips Desarrollo

1. **Agrupa llamadas API**
   - No hagas 1 llamada por servicio
   - Trae lista con `/services?establishment_id=1`

2. **Usa filtros en GET**
   ```
   GET /appointments?establishment_id=1&skip=0&limit=100
   ```

3. **Cachea datos en Frontend**
   - Establecimientos cambian poco
   - Servicios cambias cada tanto
   - Citas y mensajes sí requieren actualizaciones frecuentes

4. **WebSocket para Real-time**
   ```
   WS /api/v1/ws/messages/{appointment_id}
   ```

5. **Errores amigables**
   - No muestres errores técnicos al user
   - "Cita confirmada ✓" no "200 OK"

---

## 📚 Archivos Relacionados

- [GUIA_FLUJO_NEGOCIO.md](GUIA_FLUJO_NEGOCIO.md) - Flujo completo
- [FRONTEND_CHECKLIST.md](FRONTEND_CHECKLIST.md) - Diseño de pantallas
- [MODELO_DATOS_RELACIONES.md](MODELO_DATOS_RELACIONES.md) - Estructura BD

---

## 🎯 Template JSON para Frontend

```javascript
// Estado global recomendado en frontend
const ownerState = {
  user: {
    usuario_id: 1,
    nombre: "Juan",
    rol: "DUENO"
  },
  
  establishments: [
    {
      establecimiento_id: 1,
      nombre: "Juan's Barbershop",
      profile: { logo_url, portada_url },
      services: [...],
      agendas: [...],
      appointments: [...],
      ratings: [...],
      subscription: {...}
    }
  ],
  
  currentEstablishment: 1,
  
  messages: {
    // cita_id: [messages...]
    1: [
      {mensaje_id, emisor_id, contenido, fecha}
    ]
  },
  
  notifications: [...],
  
  loading: false,
  error: null
}
```

---

Usa esta sheet como referencia rápida mientras desarrollas! 🚀
