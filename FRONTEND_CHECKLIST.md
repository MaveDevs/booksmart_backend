# 🎨 Frontend Checklist & Page Flows para Owner Dashboard

## 📋 Pantallas Necesarias (En Orden de Importancia)

### 1️⃣ **LOGIN & REGISTRO** (Priority: CRITICAL)
```
Path: /auth/login
- Email + Password
- Botón "¿No tienes cuenta?" → /auth/register

Path: /auth/register
- Nombre, Apellido
- Email, Password, Confirm Password
- Checkbox "Soy un dueño de negocio"
  └─ Si sí: rol_id = DUENO
  └─ Si no: rol_id = CLIENTE
- POST /api/v1/login/register
```

---

### 2️⃣ **DASHBOARD** (Priority: CRITICAL)
```
Path: /dashboard (solo para DUENO)

Layout:
┌─────────────────────────────────────────────┐
│     Bienvenido, [Nombre] | Mis Negocios ▼  │
├─────────────────────────────────────────────┤
│                                             │
│  📊 KPIs (Hoy)                              │
│  ┌──────────┬──────────┬──────────┐        │
│  │  Citas   │ Ingresos │  Rating  │        │
│  │    5     │  $320    │ 4.8 ⭐   │        │
│  └──────────┴──────────┴──────────┘        │
│                                             │
│  📅 Próximas Citas (Hoy)                    │
│  ┌─────────────────────────────────────┐   │
│  │ 10:00 - Corte | Juan | CONFIRMADA  │   │
│  │ 11:00 - Barba | SIN CONFIRMAR ⚠️  │   │
│  │ 14:00 - Tinte | María | COMPLETADA│   │
│  └─────────────────────────────────────┘   │
│  [Ver calendario completo →]                │
│                                             │
│  🏢 Mis Negocios                            │
│  ┌─────────────────────────────────────┐   │
│  │ • Juan's Barbershop (5 citas hoy)   │   │
│  │ • Salón María (2 citas hoy)         │   │
│  │ [+ Crear nuevo negocio]             │   │
│  └─────────────────────────────────────┘   │
└─────────────────────────────────────────────┘

Endpoints usados:
- GET /api/v1/establishments?user_id={id}
- GET /api/v1/appointments?establishment_id=X
- GET /api/v1/ratings?establishment_id=X
- GET /api/v1/subscriptions?establishment_id=X
```

---

### 3️⃣ **NEGOCIO - VISTA GENERAL** (Priority: CRITICAL)
```
Path: /negocio/{establishment_id}

Tabs:
┌─ General │ Servicios │ Calendario │ Mensajes │ Reseñas │ Suscripción ─┐

📋 TAB: GENERAL
├─ Logo + Portada (editable)
├─ Nombre: "Juan's Barbershop"
├─ Descripción (text area, editable)
├─ Ubicación
│  ├─ Dirección (text, editable)
│  ├─ Teléfono (text, editable)
│  └─ Mapa (con LAT/LONG)
│
└─ Estado: ACTIVO/INACTIVO (toggle)

Endpoints:
- GET /api/v1/establishments/{id}
- PUT /api/v1/establishments/{id}
- GET /api/v1/profiles/{id}
- PUT /api/v1/profiles/{id}
```

---

### 4️⃣ **HORARIOS (AGENDAS)** (Priority: CRITICAL)
```
Path: /negocio/{establishment_id}/horarios

┌────────────────────────────────────────┐
│  Horarios de Servicio                  │
├────────────────────────────────────────┤
│                                        │
│  Lunes:     09:00 - 19:00 [Cerrado] │
│  Martes:    09:00 - 19:00 [Editar]  │
│  Miércoles: 09:00 - 19:00 [Editar]  │
│  Jueves:    09:00 - 19:00 [Editar]  │
│  Viernes:   09:00 - 19:00 [Editar]  │
│  Sábado:    10:00 - 17:00 [Editar]  │
│  Domingo:   CERRADO  [Abrir]        │
│                                      │
└────────────────────────────────────────┘

MODAL EDITAR HORARIO (clicking en día):
┌──────────────────────────────────────┐
│ Editar Horario - Lunes               │
├──────────────────────────────────────┤
│ Hora Inicio: [09:00] (time input)   │
│ Hora Fin:    [19:00] (time input)   │
│                                      │
│ [Cerrar este día] [Guardar] [Cancel]│
└──────────────────────────────────────┘

Endpoints:
- GET /api/v1/agendas?establishment_id={id}
- POST /api/v1/agendas (si no existe día)
- PUT /api/v1/agendas/{agenda_id}
- DELETE /api/v1/agendas/{agenda_id}

Estado en DB:
- 7 registros (uno por día)
- Si no existe → mostrar "CERRADO"
- Si existe → mostrar horas
```

---

### 5️⃣ **SERVICIOS** (Priority: CRITICAL)
```
Path: /negocio/{establishment_id}/servicios

┌─────────────────────────────────────────────────┐
│ Servicios Ofrecidos                             │
├─────────────────────────────────────────────────┤
│                                                 │
│ Tabla:                                          │
│ ┌────────────────┬──────┬────────┬──────────┐  │
│ │ Nombre         │ Min. │ Precio │ Acciones │  │
│ ├────────────────┼──────┼────────┼──────────┤  │
│ │ Corte Clásico  │  30  │ $40.00 │ ✏️ 🗑️   │  │
│ │ Corte + Barba  │  45  │ $60.00 │ ✏️ 🗑️   │  │
│ │ Afeitada       │  20  │ $25.00 │ ✏️ 🗑️   │  │
│ └────────────────┴──────┴────────┴──────────┘  │
│                                                 │
│ [+ Nuevo Servicio]                             │
└─────────────────────────────────────────────────┘

FORM: Nuevo Servicio (clicking + Nuevo)
┌────────────────────────────────────────┐
│ Crear Servicio                         │
├────────────────────────────────────────┤
│ Nombre:       [____________________]   │
│ Descripción:  [____________________]   │
│               [____________________]   │
│ Duración (min): [30]                   │
│ Precio ($):     [40.00]                │
│                                        │
│ [Cancelar] [Guardar]                  │
└────────────────────────────────────────┘

Endpoints:
- GET /api/v1/services?establishment_id={id}
- POST /api/v1/services
- PUT /api/v1/services/{service_id}
- DELETE /api/v1/services/{service_id}
```

---

### 6️⃣ **CALENDARIO DE CITAS** (Priority: CRITICAL)
```
Path: /negocio/{establishment_id}/calendario

┌─────────────────────────────────────────────────┐
│ < Enero 2025 >                                  │
├─────────────────────────────────────────────────┤
│ Do  Lu  Ma  Mi  Ju  Vi  Sa                       │
│           1   2   3   4   5                      │
│  6   7   8   9  10  11  12                       │
│ 13  14  15 [16] 17  18  19   ← Hoy              │
│ 20  21  22  23  24  25  26                       │
│ 27  28  29  30  31                              │
└─────────────────────────────────────────────────┘

Clicking en día → Mostrar citas de ese día:
┌──────────────────────────────────────────┐
│ Citas - Jueves 16 Enero 2025             │
├──────────────────────────────────────────┤
│                                          │
│ 10:00 - 10:30                           │
│ Corte Clásico | Juan | CONFIRMADA ✅   │
│ [Chat] [Editar] [Marcar Completada]    │
│                                          │
│ 11:00 - 11:20                           │
│ Afeitada | Carlos | PENDIENTE ⚠️      │
│ [Chat] [Confirmar] [Cancelar]          │
│                                          │
│ 14:00 - 14:45                           │
│ Corte + Barba | Rosa | COMPLETADA ✅   │
│                                          │
└──────────────────────────────────────────┘

MODAL: Confirmar / Cancelar Cita
┌─────────────────────────────────────────┐
│ 11:00 - 11:20 Afeitada - Carlos         │
├─────────────────────────────────────────┤
│ Status: PENDIENTE                       │
│                                         │
│ [Confirmar] [Enviar Mensaje] [Cancelar]│
└─────────────────────────────────────────┘

Endpoints:
- GET /api/v1/appointments?establishment_id={id}
- PUT /api/v1/appointments/{appointment_id}
  └─ {"estado": "CONFIRMADA"} o "COMPLETADA"
```

---

### 7️⃣ **MENSAJES (CHAT POR CITA)** (Priority: HIGH)
```
Path: /negocio/{establishment_id}/mensajes

Sidebar con citas que tienen mensajes:
┌─────────────────────────────────────┬─────────────────────┐
│ Conversaciones                      │ Chat                │
│                                     │                     │
│ 👤 Juan - Corte Clásico            │ Juan ⓘ              │
│ "Hola, ¿puedo ir un poco..."       │ └─────────────────  │
│                                     │                     │
│ 👤 Carlos - Afeitada               │ 10:00 - Juan        │
│ Sin mensajes nuevos                 │ "Hola, ¿puedo ir..." │
│                                     │                     │
│ 👤 Rosa - Corte + Barba            │ 10:15 - Yo (Owner)  │
│ "Claro! Te espero"                 │ "Claro! Te espero"  │
│                                     │                     │
│ [+ Nueva cita]                      │ 10:30 - Juan        │
│                                     │ "Gracia, allá voy"  │
│                                     │                     │
│                                     │ [Escribir mensaj..] │
│                                     │ [Enviar]            │
└─────────────────────────────────────┴─────────────────────┘

Endpoints:
- GET /api/v1/messages?appointment_id={id}
- POST /api/v1/messages
  {"cita_id": 1, "contenido": "..."}

IMPORTANTE: Usar WebSocket para mensajes en tiempo real
- /ws/messages/{appointment_id}
```

---

### 8️⃣ **RESEÑAS** (Priority: MEDIUM)
```
Path: /negocio/{establishment_id}/resenas

┌────────────────────────────────────────────┐
│ Reseñas & Calificaciones                   │
├────────────────────────────────────────────┤
│                                            │
│ Rating Promedio: ⭐ 4.7 de 5 (23 reseñas)  │
│                                            │
│ Distribución:                              │
│ ⭐⭐⭐⭐⭐  15 (65%)  ███████████████        │
│ ⭐⭐⭐⭐    6  (26%)  ██████                │
│ ⭐⭐⭐      2  (9%)   ██                    │
│ ⭐⭐        0  (0%)   -                     │
│ ⭐         0  (0%)   -                     │
│                                            │
│ Reseñas Recientes:                         │
│ ┌────────────────────────────────────────┐ │
│ │ Juan ⭐⭐⭐⭐⭐ - 5 días atrás            │ │
│ │ "¡Excelente servicio, muy profesional!"│ │
│ │                                        │ │
│ │ Carlos ⭐⭐⭐⭐ - 2 semanas atrás        │ │
│ │ "Muy bueno pero un poco caro"         │ │
│ │                                        │ │
│ │ Rosa ⭐⭐⭐⭐⭐ - 1 mes atrás            │ │
│ │ "La mejor barbería de la ciudad"      │ │
│ └────────────────────────────────────────┘ │
│                                            │
└────────────────────────────────────────────┘

Endpoints:
- GET /api/v1/ratings?establishment_id={id}

NOTA: Owner SOLO LEE, no puede editar/borrar
      Solo ADMIN y CLIENTE (autor) pueden modificar
```

---

### 9️⃣ **SUSCRIPCIÓN** (Priority: MEDIUM-HIGH)
```
Path: /negocio/{establishment_id}/suscripcion

┌──────────────────────────────────────────────┐
│ Tu Suscripción                               │
├──────────────────────────────────────────────┤
│                                              │
│ Plan Actual:                                 │
│ ┌──────────────────────────────────────────┐ │
│ │ Plan PREMIUM                             │ │
│ │ Estado: ACTIVA ✅                        │ │
│ │ Fecha de Inicio: 1 Enero 2025            │ │
│ │ Fecha de Vencimiento: 1 Febrero 2025    │ │
│ │ Días Restantes: 12 días ⏳                │ │
│ │                                          │ │
│ │ Beneficios:                              │ │
│ │ • Hasta 50 citas/mes                    │ │
│ │ • 10 trabajadores                       │ │
│ │ • Chat en tiempo real                   │ │
│ │ • Reportes avanzados                    │ │
│ │                                          │ │
│ │ Precio: $9.99/mes                        │ │
│ └──────────────────────────────────────────┘ │
│                                              │
│ [Renovar Suscripción] [Ver otros planes]    │
│                                              │
└──────────────────────────────────────────────┘

Endpoints:
- GET /api/v1/subscriptions?establishment_id={id}

NOTA: Owner solo PUEDE LEER
      ADMIN maneja crear/actualizar suscripción
      Usuario ve info y redirige a Admin (o Stripe)
```

---

## 🔄 Flujos de Interacción Clave

### FLUJO 1: Owner Crea Nuevo Negocio
```
[Dashboard]
  ↓
[Click "+ Crear nuevo negocio"]
  ↓
[Modal/Formulario]
  - Nombre
  - Descripción
  - Dirección
  - Teléfono
  - Lat/Long (opcionalmente con mapa)
  ↓
[POST /api/v1/establishments] + [POST /api/v1/profiles]
  ↓
[Redirige a: /negocio/{nuevo_id}]
  ↓
[Sistema sugiere: "Configura horarios antes de recibir citas"]
```

### FLUJO 2: Owner Confirma Cita
```
[Calendario] O [Sidebar de citas pendientes]
  ↓
[Click en cita con estado PENDIENTE]
  ↓
[Modal muestra:
  - Cliente
  - Servicio
  - Fecha/Hora
  - Status actual: PENDIENTE]
  ↓
[Click botón "Confirmar cita"]
  ↓
[PUT /api/v1/appointments/{id}] con {"estado": "CONFIRMADA"}
  ↓
[✅ Confirmada - Enviar notificación a cliente]
  ↓
[Owner puede ver en calendario ahora CONFIRMADA]
  ↓
[Cliente recibe notificación (push/email/SMS)]
```

### FLUJO 3: Owner Completa Cita + Cliente Deja Reseña
```
[Calendario - Día de la cita]
  ↓
[Click en cita después de la hora programada]
  ↓
[Opción: "Marcar como Completada"]
  ↓
[PUT /api/v1/appointments/{id}] con {"estado": "COMPLETADA"}
  ↓
[Cliente recibe notificación: "Tu cita fue completada"]
  ↓
[Cliente puede dejar reseña]
  POST /api/v1/ratings
  {
    "establecimiento_id": 1,
    "usuario_id": 5,
    "calificacion": 5,
    "comentario": "..."
  }
  ↓
[Owner ve nueva reseña en tab "Reseñas"]
```

### FLUJO 4: Owner Comunica con Cliente
```
[Cita con estado PENDIENTE/CONFIRMADA]
  ↓
[Owner click en botón "Chat"]
  ↓
[Abre panel de mensajes]
  ↓
[Owner ve conversación anterior (si existe)]
  ↓
[Owner escribe mensaje]
  ↓
[POST /api/v1/messages]
  {
    "cita_id": 1,
    "contenido": "Hola, ¿a que hora llegas?"
  }
  ↓
[Websocket emite en tiempo real]
  ↓
[Cliente ve mensaje instantly]
  ↓
[Cliente responde]
  ↓
[Owner recibe respuesta in real-time]
```

---

## 🎯 Prioridad de Implementación

### FASE 1: MVP (Essencial)
- [ ] Login/Register
- [ ] Dashboard (KPIs básicos)
- [ ] Vista Negocio - General
- [ ] Horarios (Agendas)
- [ ] Servicios (CRUD)
- [ ] Calendario de Citas básico
- [ ] Confirmar/Cancelar citas

### FASE 2: Full featured
- [ ] Mensajes en tiempo real (WebSocket)
- [ ] Chat por cita
- [ ] Reseñas (lectura)
- [ ] Suscripción (lectura + link a admin)
- [ ] Notificaciones (push/browser)

### FASE 3: Advanced
- [ ] Workers/Equipo (cuando backends complete)
- [ ] Reportes avanzados (gráficos)
- [ ] Exportar datos
- [ ] Integraciones de pago (Stripe)
- [ ] SMS/Email notifications

---

## 🔌 Patrones de Llamadas API

### Patrón de Listado
```javascript
// Obtener lista de citas
const response = await fetch(
  `/api/v1/appointments?establishment_id=1`,
  {
    headers: { 'Authorization': `Bearer ${token}` }
  }
);
const appointments = await response.json();
// appointments = [
//   {cita_id: 1, cliente_id: 5, servicio_id: 1, fecha: "2025-01-30", ...},
//   {cita_id: 2, cliente_id: 6, servicio_id: 2, fecha: "2025-01-30", ...},
// ]
```

### Patrón de Creación
```javascript
// Crear nuevo servicio
const response = await fetch(
  `/api/v1/services`,
  {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      establecimiento_id: 1,
      nombre: "Corte Clásico",
      descripcion: "Corte con técnica...",
      duracion: 30,
      precio: 40.00
    })
  }
);
const newService = await response.json();
// {servicio_id: 5, establecimiento_id: 1, nombre: "Corte Clásico", ...}
```

### Patrón de Actualización
```javascript
// Cambiar estado de cita
const response = await fetch(
  `/api/v1/appointments/1`,
  {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${token}`
    },
    body: JSON.stringify({
      estado: "CONFIRMADA"  // O "COMPLETADA" o "CANCELADA"
    })
  }
);
const updatedAppointment = await response.json();
```

---

## 🎨 Sugerencias de UI/UX

1. **Color Coding para Estados**
   - 🟡 PENDIENTE (Amarillo) - Necesita acción
   - 🟢 CONFIRMADA (Verde) - Todo bien
   - 🟠 EN PROGRESO (Naranja) - En este momento
   - 🔵 COMPLETADA (Azul) - Terminado
   - 🔴 CANCELADA (Rojo) - Cancelado

2. **Notificaciones**
   - Nueva cita ingresa → Alert de sonido
   - Cliente responde mensaje → Notificación
   - Cita por vencer → Recordatorio

3. **Mobile Responsive**
   - Calendario adaptativo
   - Botones grandes en mobile
   - Sidebar colapsable

4. **Real-time Updates**
   - Socket.io para mensajes
   - Actualizar calendario cuando cliente crea cita
   - Notificar cuando cliente confirma/cancela

---

## 📚 Validaciones Importantes

**En Frontend:**
```javascript
// Validar horarios
if (horaFin <= horaInicio) {
  error("Hora fin debe ser después de hora inicio");
}

// Validar precio
if (precio < 0 || !precio) {
  error("Precio requerido y debe ser positivo");
}

// Validar duración
if (duracion < 5 || duracion > 480) {
  error("Duración debe ser entre 5 y 480 minutos");
}

// Validar fecha de cita
if (fecha < today) {
  error("No puedes crear cita en el pasado");
}
```

**Backend ya valida:**
✅ Usuario es DUENO (permisos)
✅ Cita belongs al establecimiento del owner
✅ hora_fin > hora_inicio (en agendas)
✅ Calificación 1-5 (en ratings)
✅ Un review por usuario por establecimiento (unique constraint)

---

## 🚀 Resumen de Endpoints por Pantalla

| Pantalla | GET | POST | PUT | DELETE |
|----------|-----|------|-----|--------|
| Dashboard | Establishments, Appointments | - | - | - |
| General | Establishments, Profiles | Profiles | Establishments, Profiles | Establishments |
| Horarios | Agendas | Agendas | Agendas | Agendas |
| Servicios | Services | Services | Services | Services |
| Calendario | Appointments | - | Appointments | - |
| Mensajes | Messages | Messages | - | - |
| Reseñas | Ratings | - | - | - |
| Suscripción | Subscriptions | - | - | - |

---

¿Sobre cuál pantalla te gustaría que profundice primero?
