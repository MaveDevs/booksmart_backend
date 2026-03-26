# 📱 Guía del Flujo Backend para Dashboard de Dueños (Owners)

## 🎯 Resumen Ejecutivo
Tu plataforma maneja **3 entidades principales** para los dueños (owners):
1. **El Negocio** (Establishment) - El corazón
2. **Los Servicios** (Services) - Qué ofreces
3. **Las Citas** (Appointments) - Tus ingresos
4. **Los Usuarios** (Workers) - Tu equipo

---

## 📊 Arquitectura de Datos

```
┌─────────────────────────────────────────┐
│           USER (ROLE: DUENO)            │
│      El dueño del negocio/business     │
└──────────────────┬──────────────────────┘
                   │
                   ├─ 👤 PROFILE
                   │  └─ Logo, portada, descripción pública
                   │
                   ├─ 🏢 ESTABLISHMENTS (1+ negocios)
                   │  ├─ 📍 Ubicación, teléfono, dirección / LATITUD & LONGITUD
                   │  ├─ 📅 AGENDAS (7 registros, uno por día)
                   │  │  └─ Lunes-Domingo: hora_inicio, hora_fin
                   │  ├─ 🛎️ SERVICES (múltiples)
                   │  │  ├─ nombre, descripción, precio, duración
                   │  │  └─ 📋 APPOINTMENTS (citas para este servicio)
                   │  │     ├─ cliente_id, fecha, hora_inicio, hora_fin
                   │  │     ├─ estado: PENDIENTE → CONFIRMADA → COMPLETADA
                   │  │     └─ 💬 MESSAGES (comunicación con cliente)
                   │  ├─ ⭐ RATINGS (reseñas 1-5)
                   │  │  └─ usuario_id, calificación, comentario
                   │  └─ 💳 SUBSCRIPTIONS
                   │     └─ Plan actual, estado, fecha_expiracion
                   │
                   └─ 👨‍💼 WORKERS (Tu equipo) - SIN ENDPOINTS AÚN


┌─────────────────────────────────────────┐
│    USER (ROLE: CLIENTE)                 │
│       Quien hace las reservas           │
└─────────────────────────────────────────┘
         │
         ├─ 📋 APPOINTMENTS (sus citas)
         ├─ ⭐ RATINGS (sus reseñas)
         ├─ 💬 MESSAGES (comunicación)
         └─ 🔔 PUSH_SUBSCRIPTIONS
```

---

## 🔄 FLUJO COMPLETO PARA UN OWNER

### FASE 1️⃣: SETUP INICIAL (One-time)
```
1. REGISTRARSE
   └─ POST /api/v1/login/register
      Crea: USER con rol_id = DUENO

2. CREAR ESTABLISHMENT
   └─ POST /api/v1/establishments
      Cuerpo:
      {
        "nombre": "Mi Peluquería",
        "descripcion": "Mejor peluquería del pueblo",
        "direccion": "Calle Principal 123",
        "latitud": -12.0432,
        "longitud": -77.0282,
        "telefono": "+51987654321"
      }
      Devuelve: establishment_id

3. CREAR PERFIL DEL NEGOCIO
   └─ POST /api/v1/profiles
      Cuerpo:
      {
        "establecimiento_id": 1,
        "logo_url": "https://...",
        "portada_url": "https://...",
        "descripcion_larga": "..."
      }
      Nota: Solo OWNER/ADMIN puede actualizar su perfil

4. CONFIGURAR HORARIOS (AGENDAS)
   └─ POST /api/v1/agendas (7 veces, una por día)
      Cuerpo (ejemplo):
      {
        "establecimiento_id": 1,
        "dia_semana": "LUNES",
        "hora_inicio": "09:00",
        "hora_fin": "18:00"
      }
      Validación: hora_fin > hora_inicio
      Nota: Cuando está vacío, el negocio cierra ese día

5. AÑADIR SERVICIOS
   └─ POST /api/v1/services
      Cuerpo (repetir por cada servicio):
      {
        "establecimiento_id": 1,
        "nombre": "Corte de Cabello",
        "descripcion": "Corte moderno con técnica...",
        "duracion": 30,  # minutos
        "precio": 50.00
      }
      Devuelve: servicio_id
```

### FASE 2️⃣: OPERACIÓN DIARIA (Recurring)

#### 📊 DASHBOARD DEL OWNER
```
GET /api/v1/establishments/?user_id={user_id}
└─ Lista todos los negocios del dueño
   Respuesta: [Establishment, Establishment, ...]
   
GET /api/v1/establishments/{establishment_id}
└─ Detalles completos de 1 negocio
   Devuelve: nombre, servicios (count), citas hoy, rating promedio
```

#### 📅 GESTIONAR AGENDAS
```
GET /api/v1/agendas?establishment_id={id}
└─ Ver los 7 días configurados

PUT /api/v1/agendas/{agenda_id}
└─ Modificar horario de un día
   {
     "hora_inicio": "08:00",
     "hora_fin": "19:00"
   }

DELETE /api/v1/agendas/{agenda_id}
└─ Cerrar un día (opcional)
```

#### 🛎️ GESTIONAR SERVICIOS
```
GET /api/v1/services?establishment_id={id}
└─ Ver todos los servicios del negocio

POST /api/v1/services
└─ Añadir nuevo servicio

PUT /api/v1/services/{service_id}
└─ Editar: nombre, precio, duración

DELETE /api/v1/services/{service_id}
└─ Eliminar servicio

GET /api/v1/services/{service_id}/appointments
└─ Ver citas asociadas a este servicio
```

#### 📋 GESTIONAR CITAS (IMPORTANTE)
```
LISTAR CITAS DEL OWNER
├─ GET /api/v1/appointments?establishment_id={id}
│  └─ Todas las citas de mis negocios
│     Estados: PENDIENTE, CONFIRMADA, CANCELADA, COMPLETADA
│
├─ GET /api/v1/appointments/{appointment_id}
│  └─ Detalle de 1 cita
│     Incluye: cliente_id, servicio_id, fecha, hora, estado
│
└─ Permiso: OWNER solo ve citas de sus establecimientos

CONFIRMAR UNA CITA
└─ PUT /api/v1/appointments/{appointment_id}
   Cuerpo:
   {
     "estado": "CONFIRMADA"
   }
   Nota: PENDIENTE → CONFIRMADA (cliente espera esto)

COMPLETAR UNA CITA
└─ PUT /api/v1/appointments/{appointment_id}
   Cuerpo:
   {
     "estado": "COMPLETADA"
   }
   Nota: Después, cliente puede dejar rating

CANCELAR UNA CITA
└─ PUT /api/v1/appointments/{appointment_id}
   Cuerpo:
   {
     "estado": "CANCELADA"
   }
   Nota: Si owner cancela debe notificar al cliente
```

#### 💬 MENSAJERÍA DURANTE CITA
```
ENVIAR MENSAJE
└─ POST /api/v1/messages
   Cuerpo:
   {
     "cita_id": 1,
     "contenido": "Hola, ¿qué color prefieres?"
   }
   Nota: Solo owner/cliente de esa cita pueden escribir

VER MENSAJES DE UNA CITA
└─ GET /api/v1/messages?appointment_id={id}
   Devuelve: lista de mensajes con timestamp

PERMISOS:
├─ CLIENTE: puede ver/enviar en sus citas
├─ OWNER: puede ver/enviar en citas de sus servicios
└─ ADMIN: full access
```

#### ⭐ GESTIONAR RATINGS
```
VER RATINGS DEL NEGOCIO
└─ GET /api/v1/ratings?establishment_id={id}
   Devuelve:
   {
     "resena_id": 1,
     "usuario_id": 5,
     "calificacion": 5,
     "comentario": "¡Excelente servicio!",
     "fecha": "2025-01-15"
   }

ESTADÍSTICAS
└─ Promedio de calificación
└─ Total de reseñas
└─ (Puedes calcularlo en frontend sumando ratings)

NOTA: Solo CLIENTE puede crear rating
      OWNER solo puede verlos
      ADMIN puede ver/eliminar
```

#### 💳 GESTIONAR SUSCRIPCIONES
```
VER SUSCRIPCIÓN ACTUAL
└─ GET /api/v1/subscriptions?establishment_id={id}
   Devuelve:
   {
     "subscripcion_id": 1,
     "establishment_id": 1,
     "plan_id": 1,
     "estado": "ACTIVA",
     "fecha_inicio": "2025-01-01",
     "fecha_expiracion": "2025-02-01"
   }

NOTA IMPORTANTE:
├─ OWNER: Solo puede LEER su suscripción
├─ ADMIN: Puede crear/actualizar/cancelar suscripciones
└─ Flujo: Owner → contrata plan → Admin activa → Owner paga
```

### FASE 3️⃣: ANÁLISIS (Reporting)

```
ESTADÍSTICAS POR NEGOCIO
├─ Total de citas: COUNT(appointments WHERE establishment_id=X)
├─ Citas confirmadas hoy: COUNT(appointments WHERE status=CONFIRMADA AND date=TODAY)
├─ Rating promedio: AVG(ratings WHERE establishment_id=X)
├─ Ingresos este mes: SUM(service.precio WHERE appointment.fecha IN this_month)
└─ Clientes únicos: COUNT(DISTINCT cliente_id WHERE appointment.establishment_id=X)

ENDPOINT PARA ESTO:
└─ Los KPIs se calculan en FRONTEND con los datos que traes
   No hay endpoint específico de "reportes" todavía
```

---

## 🔐 MATRIZ DE PERMISOS

| Acción | CLIENTE | DUENO | ADMIN |
|--------|---------|-------|-------|
| **ESTABLISHMENT** | | |
| Ver establecimientos | ✅ Todos | ✅ Sus negocios | ✅ Todos |
| Crear establecimiento | ❌ | ✅ | ✅ |
| Editar establecimiento | ❌ | ✅ Sus negocios | ✅ |
| Borrar establecimiento | ❌ | ✅ Sus negocios | ✅ |
| **SERVICES** | | |
| Ver servicios | ✅ Todos | ✅ Suyos | ✅ Todos |
| Crear servicio | ❌ | ✅ En sus negos | ✅ |
| Editar servicio | ❌ | ✅ Suyos | ✅ |
| **APPOINTMENTS** | | |
| Ver citas | ✅ Sus citas | ✅ Sus negocios | ✅ Todas |
| Crear cita | ✅ | ❌ | ✅ |
| Confirmar cita | ❌ | ✅ Sus negocios | ✅ |
| Cancelar cita | ✅ La suya | ✅ Sus negocios | ✅ |
| **MESSAGES** | | |
| Enviar mensaje | ✅ En sus citas | ✅ En sus negocios | ✅ |
| Ver mensajes | ✅ Sus citas | ✅ Sus negocios | ✅ |
| **RATINGS** | | |
| Ver ratings | ✅ Todos | ✅ Sus negocios | ✅ Todos |
| Crear rating | ✅ En sus citas | ❌ | ✅ |
| Editar rating | ✅ El suyo | ❌ | ✅ |

---

## 📱 ENDPOINTS CLAVE POR RECURSO

### ESTABLISHMENTS
```
GET    /api/v1/establishments                    # Listar
GET    /api/v1/establishments/{id}               # Detalle
POST   /api/v1/establishments                    # Crear
PUT    /api/v1/establishments/{id}               # Editar
DELETE /api/v1/establishments/{id}               # Borrar
```

### SERVICES
```
GET    /api/v1/services?establishment_id=X      # Listar por negocio
POST   /api/v1/services                         # Crear
PUT    /api/v1/services/{id}                    # Editar
DELETE /api/v1/services/{id}                    # Borrar
```

### APPOINTMENTS
```
GET    /api/v1/appointments                     # Listar (filtrado por user)
GET    /api/v1/appointments/{id}                # Detalle
POST   /api/v1/appointments                     # Crear (cliente)
PUT    /api/v1/appointments/{id}                # Cambiar estado
DELETE /api/v1/appointments/{id}                # Cancelar
```

### AGENDAS
```
GET    /api/v1/agendas?establishment_id=X      # Listar 7 días
POST   /api/v1/agendas                         # Crear para un día
PUT    /api/v1/agendas/{id}                    # Editar horario
DELETE /api/v1/agendas/{id}                    # Cerrar un día
```

### MESSAGES
```
GET    /api/v1/messages?appointment_id=X       # Ver chat de una cita
POST   /api/v1/messages                        # Enviar mensaje
```

### RATINGS
```
GET    /api/v1/ratings?establishment_id=X     # Ver reseñas del negocio
POST   /api/v1/ratings                        # Crear (cliente)
PUT    /api/v1/ratings/{id}                   # Editar (cliente/admin)
```

### PROFILES
```
GET    /api/v1/profiles/{id}                  # Ver perfil público
POST   /api/v1/profiles                       # Crear
PUT    /api/v1/profiles/{id}                  # Editar
```

### SUBSCRIPTIONS
```
GET    /api/v1/subscriptions?establishment_id=X  # Ver suscripción
```

---

## 🚨 WORKERS (⚠️ EN CONSTRUCCIÓN)

El modelo existe pero **NO HAY ENDPOINTS CRUD NI EN VIEWS**:
- Modelo: ✅ Definido
- Schemas: ✅ Definido
- CRUD: ❌ No existe
- Endpoints: ❌ No existe en API

**Lo que deberías agregar:**
```
POST   /api/v1/workers                 # Owner agrega worker
GET    /api/v1/workers?establishment_id=X  # Ver equipo
PUT    /api/v1/workers/{id}            # Editar permisos
DELETE /api/v1/workers/{id}            # Remover del equipo
```

---

## 🌐 FLUJO DE UN CLIENTE (Para entender el contexto)

```
1. CLIENTE VE NEGOCIO
   GET /api/v1/establishments
   GET /api/v1/establishments/{id}/profile

2. CLIENTE VE SERVICIOS Y HORARIOS
   GET /api/v1/services?establishment_id=X
   GET /api/v1/agendas?establishment_id=X

3. CLIENTE RESERVA
   POST /api/v1/appointments
   {
     "cliente_id": 5,
     "servicio_id": 1,
     "fecha": "2025-01-30",
     "hora_inicio": "14:00",
     "hora_fin": "14:30"
   }
   Status creado: PENDIENTE

4. CLIENTE + OWNER CHAT
   POST /api/v1/messages (ambos)
   GET /api/v1/messages?appointment_id=1 (ambos)

5. OWNER CONFIRMA
   PUT /api/v1/appointments/{id}
   {"estado": "CONFIRMADA"}

6. AFTER CITA COMPLETADA
   Cliente deja rating
   OWNER VE FEEDBACK
```

---

## 🎨 SUGERENCIAS PARA TU FRONTEND DE OWNER

### ✅ Pantallas Esenciales:
1. **Login/Register** - Crear user con rol DUENO
2. **Mi Perfil** - Editar nombre, email, foto
3. **Dashboard** - KPIs: citas hoy, rating, ingresos
4. **Mis Negocios** - Listar y crear establecimientos
5. **Configuración del Negocio**
   - Logo/Portada
   - Ubicación (mapa con lat/long)
   - Teléfono
   - **Horarios** (7 días de la semana)
   
6. **Gestión de Servicios**
   - Tabla: Nombre, Duración, Precio, Acciones
   - Crear/Editar/Borrar
   
7. **Calendario de Citas**
   - Vista mensual/semanal/diaria
   - Citas por color según estado
   - Click para confirmar/cancelar
   
8. **Mensajes/Chat**
   - Por cita
   - Notificaciones en tiempo real (WebSocket)
   
9. **Reseñas**
   - Rating promedio
   - List de reseñas con comentarios
   
10. **Suscripción**
    - Plan actual
    - Fecha de vencimiento
    - Botón para renovar → lleva a Admin (o integra Stripe)

### 🎯 Flujo Principal en Frontend:
```
Login (DUENO)
  ↓
Dashboard (KPIs)
  ├─ Ver negocios creados
  ├─ Crear nuevo negocio
  └─ Seleccionar uno
    ↓
    Panel del Negocio
    ├─ Horarios (AGENDAS)
    ├─ Servicios
    ├─ Citas (calendario)
    ├─ Mensajes
    ├─ Reseñas
    └─ Suscripción
```

---

## 🧪 Ejemplo Completo: Crear Negocio + Servicio

```bash
# 1. REGISTRARSE
POST /api/v1/login/register
{
  "nombre": "Juan",
  "apellido": "Pérez",
  "correo": "juan@peluqueria.com",
  "contrasena": "seguro123"
}
→ Devuelve: usuario_id = 1, rol_id = DUENO

# 2. CREAR NEGOCIO
POST /api/v1/establishments
Headers: Authorization: Bearer {token}
{
  "nombre": "Juan's Barbershop",
  "descripcion": "Barbería moderna",
  "direccion": "Calle 5 #123",
  "latitud": -12.0432,
  "longitud": -77.0282,
  "telefono": "+51987654321"
}
→ Devuelve: establishment_id = 1

# 3. CREAR PERFIL
POST /api/v1/profiles
{
  "establecimiento_id": 1,
  "logo_url": "https://...",
  "portada_url": "https://...",
  "descripcion_larga": "Somos la mejor barbería..."
}

# 4. CREAR HORARIOS (7 ciclos)
POST /api/v1/agendas
{
  "establecimiento_id": 1,
  "dia_semana": "LUNES",
  "hora_inicio": "09:00",
  "hora_fin": "19:00"
}

# 5. CREAR SERVICIOS
POST /api/v1/services
{
  "establecimiento_id": 1,
  "nombre": "Corte Clásico",
  "descripcion": "Corte con leyenda",
  "duracion": 30,
  "precio": 40.00
}

POST /api/v1/services
{
  "establecimiento_id": 1,
  "nombre": "Corte + Barba",
  "descripcion": "Corte profesional + arreglo de barba",
  "duracion": 45,
  "precio": 60.00
}

# 6. VER NEGOCIOS
GET /api/v1/establishments?user_id=1
→ Devuelve: [{Juan's Barbershop con servicios, horarios, etc}]

# 7. VER CITAS DEL NEGOCIO
GET /api/v1/appointments?establishment_id=1
→ Devuelve: [] (vacío al principio)

# 8. CLIENTE RESERVA (desde app cliente)
POST /api/v1/appointments
{
  "cliente_id": 5,
  "servicio_id": 1,
  "fecha": "2025-01-30",
  "hora_inicio": "10:00",
  "hora_fin": "10:30"
}

# 9. OWNER VE NUEVA CITA
GET /api/v1/appointments?establishment_id=1
→ Devuelve: [{cita con estado PENDIENTE}]

# 10. OWNER CONFIRMA
PUT /api/v1/appointments/{cita_id}
{
  "estado": "CONFIRMADA"
}

# 11. DESPUÉS DE LA CITA
PUT /api/v1/appointments/{cita_id}
{
  "estado": "COMPLETADA"
}

# 12. CLIENTE DEJA RESEÑA (desde app cliente)
POST /api/v1/ratings
{
  "establecimiento_id": 1,
  "usuario_id": 5,
  "calificacion": 5,
  "comentario": "¡Excelente trabajo!"
}

# 13. OWNER VE RESEÑA
GET /api/v1/ratings?establishment_id=1
→ Devuelve: [{reseña de 5 estrellas}]
```

---

## 📌 Resumen Rápido

| Entidad | GET | POST | PUT | DELETE | Permisos |
|---------|-----|------|-----|--------|----------|
| Establishment | ✅ | ✅ | ✅ | ✅ | DUENO suyos / ADMIN todos |
| Service | ✅ | ✅ | ✅ | ✅ | DUENO suyos / ADMIN todos |
| Appointment | ✅ | ✅ (CLIENTE) | ✅ (estado) | ✅ (CANCELAR) | DUENO suyos / ADMIN todos |
| Agenda | ✅ | ✅ | ✅ | ✅ | DUENO suyos / ADMIN todos |
| Message | ✅ | ✅ | ❌ | ❌ | Ambos en la cita |
| Rating | ✅ | ✅ (CLIENTE) | ✅ (CLIENTE) | ❌ | DUENO lee / ADMIN full |
| Profile | ✅ | ✅ | ✅ | ❌ | DUENO suyo / ADMIN todos |
| Subscription | ✅ | ❌ | ❌ | ❌ | DUENO read-only / ADMIN full |
| Worker | ❌ | ❌ | ❌ | ❌ | **NO IMPLEMENTADO** |

---

## 🎓 Conclusión

El backend tiene todo estructurado para que manejes:
✅ Tu negocio (ESTABLISHMENT)
✅ Tus servicios (SERVICES)
✅ Tus horarios (AGENDAS)
✅ Tus citas (APPOINTMENTS)
✅ Tu comunicación (MESSAGES)
✅ Tu reputación (RATINGS)
✅ Tu suscripción (SUBSCRIPTIONS)

**Falta:** Workers (equipo) - deberías completar esto si querés que los dueños gestionen empleados.

¿Necesitas entender algún endpoint específico en más detalle?
