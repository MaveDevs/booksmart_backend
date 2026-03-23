# 🗄️ Modelo de Datos & Relaciones - Base de Datos

## 📊 Diagrama ER (Entity-Relationship)

```
┌──────────────┐
│    USUARIO   │ (usuarios)
├──────────────┤
│ usuario_id   │◄─────┐
│ nombre       │      │ 1:N
│ apellido     │      │
│ correo       │      │
│ rol_id       │──────┼──┐
│ activo       │      │  │
│ fecha_creación│     │  │
└──────────────┘      │  │
       │              │  │
       │1:N           │  │
       │              │  │
       └──────────────┴──┴────────────┐
                                      │
              ┌───────────────────────┴─────────────────┐
              │                                         │
              ▼                                         ▼
    ┌──────────────────────┐              ┌──────────────────┐
    │  ESTABLECIMIENTO     │              │     ROL          │
    │  (establecimientos)  │              │    (rol)         │
    ├──────────────────────┤              ├──────────────────┤
    │ establecimiento_id   │              │ rol_id           │
    │ usuario_id (FK)      │              │ nombre (DUENO)   │
    │ nombre               │              │ descripcion      │
    │ descripcion          │              └──────────────────┘
    │ direccion            │
    │ latitud              │
    │ longitud             │
    │ telefono             │
    │ activo               │
    └──────────────────────┘
              │
              │1:N
              │
    ┌─────────┴───────────────────────┬──────────────────────┬──────────────┐
    │                                 │                      │              │
    ▼                                 ▼                      ▼              ▼
 ┌────────────┐              ┌──────────────┐        ┌──────────────┐  ┌──────────┐
 │ SERVICIO   │              │   AGENDA     │        │   PROFILE    │  │ RESENA   │
 │ (servicio) │              │  (agenda)    │        │  (profile)   │  │(resena)  │
 ├────────────┤              ├──────────────┤        ├──────────────┤  ├──────────┤
 │servicio_id │              │  agenda_id   │        │ profile_id   │  │resena_id│
 │est_id(FK)  │              │ est_id(FK)   │        │ est_id(FK)   │  │est_id(FK)│
 │ nombre     │              │dia_semana    │        │logo_url      │  │usuario_id│
 │descripcion │              │hora_inicio   │        │portada_url   │  │calific.  │
 │ duracion   │              │hora_fin      │        │descripcion   │  │comentario│
 │ precio     │              │activo        │        └──────────────┘  │fecha     │
 │ activo     │              └──────────────┘                           │activo    │
 └─────┬──────┘                                                         └──────────┘
       │
       │1:N
       │
       ▼
  ┌────────────────────┐
  │  CITA              │
  │  (cita)            │
  ├────────────────────┤
  │ cita_id            │
  │ cliente_id(FK)     │──────┐
  │ servicio_id(FK)    │      │
  │ fecha              │      │
  │ hora_inicio        │      │ (Usuario/Cliente)
  │ hora_fin           │      │
  │ estado             │      │
  │ fecha_creacion     │      │
  └────┬───────────────┘      │
       │                      │
       │1:N                   │
       │                      └──────────────────┐
       │                                        │
       ▼                                    1:N ▼
  ┌────────────────┐                 ┌──────────────────┐
  │  MENSAJE       │                 │   NOTIFICACION   │
  │  (mensaje)     │                 │ (notificacion)   │
  ├────────────────┤                 ├──────────────────┤
  │mensaje_id      │                 │notificacion_id   │
  │cita_id(FK)     │                 │usuario_id(FK)    │
  │emisor_id(FK)   │                 │mensaje           │
  │contenido       │                 │leida             │
  │fecha_envio     │                 │fecha_creacion    │
  └────────────────┘                 └──────────────────┘


    ┌──────────────────────────┐
    │  SUSCRIPCION             │
    │  (suscripcion)           │
    ├──────────────────────────┤
    │ suscripcion_id           │
    │ establecimiento_id(FK)   │─────┐
    │ plan_id(FK)              │     │1:N
    │ estado (ACTIVA...)       │     │
    │ fecha_inicio             │     │
    │ fecha_expiracion         │     │
    │ fecha_actualizacion      │     │
    └──────────────────────────┘     │
                                     │
    ┌────────────────────────────┐   │
    │    PLAN                    │   │
    │    (plan)                  │   │
    ├────────────────────────────┤   │
    │ plan_id                    │◄──┘
    │ nombre (BASICO, PREMIUM)   │
    │ descripcion                │
    │ precio                     │
    │ duracion_dias              │
    │ max_citas                  │
    │ max_trabajadores           │
    │ activo                     │
    └────────────────────────────┘


    ┌──────────────────────────┐
    │  WORKER                  │
    │  (worker) ⚠️ SIN USAR    │
    ├──────────────────────────┤
    │ worker_id                │
    │ establecimiento_id(FK)    │
    │ usuario_id(FK)           │
    │ rol_trabajador           │
    │ fecha_inicio             │
    │ activo                   │
    └──────────────────────────┘

    ┌──────────────────────────┐
    │  PUSH_SUBSCRIPTION       │
    │  (push_subscription)     │
    ├──────────────────────────┤
    │ push_sub_id              │
    │ usuario_id(FK)           │
    │ endpoint                 │
    │ p256dh                   │
    │ auth                     │
    │ fecha_creacion           │
    └──────────────────────────┘
```

---

## 🔗 Relaciones Detalladas

### 1️⃣ USUARIO ↔ ESTABLECIMIENTO
```
Relación: 1 USUARIO (DUENO) : N ESTABLECIMIENTOS
├─ Un dueño PUEDE tener múltiples negocios
├─ Un establecimiento PERTENECE a UN dueño
└─ Foreign Key: etablecimiento.usuario_id → usuario.usuario_id

Ejemplo:
┌─────────────────┐
│ USUARIO #1      │
│ Juan Pérez      │
├─────────────────┤
│ ROL: DUENO      │
└─────────────────┘
        │ 1:N
        │
    ┌───┴────┬──────────┐
    │         │          │
    ▼         ▼          ▼
[Estab 1]  [Estab 2]  [Estab 3]
Barbería     Salón      Clínica
```

### 2️⃣ ESTABLECIMIENTO ↔ SERVICIO
```
Relación: 1 ESTABLECIMIENTO : N SERVICIOS
├─ Un negocio OFRECE múltiples servicios
├─ Un servicio PERTENECE a UN establecimiento
└─ Foreign Key: servicio.establecimiento_id → establecimiento.establecimiento_id

Ejemplo:
┌────────────────────────┐
│ ESTABLECIMIENTO        │
│ Juan's Barbershop      │
├────────────────────────┤
└────────────────────────┘
        │ 1:N
        │
    ┌───┴────┬──────────┐
    │         │          │
    ▼         ▼          ▼
 [Corte]   [Barba]   [Tinte]
  $40        $25       $50
```

### 3️⃣ SERVICIO ↔ CITA
```
Relación: 1 SERVICIO : N CITAS
├─ Un servicio PUEDE tener N reservas
├─ Una cita RESERVA UN servicio
└─ Foreign Key: cita.servicio_id → servicio.servicio_id

Ejemplo:
┌────────────────────────┐
│ SERVICIO               │
│ Corte Clásico ($40)    │
│ Duración: 30 min       │
├────────────────────────┤
└────────────────────────┘
        │ 1:N
        │
    ┌───┴────┬──────────┐
    │         │          │
    ▼         ▼          ▼
 [Cita 1]  [Cita 2]  [Cita 3]
 10:00       14:00    17:00
  Juan      Carlos    Rosa
```

### 4️⃣ USUARIO (CLIENTE) ↔ CITA
```
Relación: 1 USUARIO (CLIENTE) : N CITAS
├─ Un cliente HACE múltiples reservas
├─ Una cita ES HECHA por UN cliente
└─ Foreign Key: cita.cliente_id → usuario.usuario_id

Ejemplo:
┌──────────────────────┐
│ USUARIO              │
│ Juan (CLIENTE)       │
├──────────────────────┤
└──────────────────────┘
        │ 1:N
        │
    ┌───┴────┬──────────┐
    │         │          │
    ▼         ▼          ▼
 [Cita 1]  [Cita 2]  [Cita 3]
 Barbería   Salón    Clínica
 16 Jan    22 Jan   30 Jan
```

### 5️⃣ CITA ↔ MENSAJE
```
Relación: 1 CITA : N MENSAJES
├─ Una cita PUEDE tener múltiples mensajes
├─ Un mensaje PERTENECE a UNA cita
└─ Foreign Key: mensaje.cita_id → cita.cita_id

Ejemplo:
┌──────────────────────────────────┐
│ CITA #1                          │
│ Juan - Corte - 10:00 - 16 Jan    │
├──────────────────────────────────┤
└──────────────────────────────────┘
        │ 1:N (Chat)
        │
    ┌───┴─────────┬──────────────┐
    │             │              │
    ▼             ▼              ▼
 [Msg 1]      [Msg 2]        [Msg 3]
 10:00 -      10:05 -        10:10 -
 "Hola"       "Ok"           "Gracia"
 (Juan)       (Owner)        (Juan)
```

### 6️⃣ USUARIO (CLIENTE) ↔ RESENA
```
Relación: 1 USUARIO : N RESENAS
Relación: 1 ESTABLECIMIENTO : N RESENAS
├─ Un cliente PUEDE dejar 1 resena POR establecimiento (UNIQUE constraint)
├─ Un establecimiento RECIBE N resenas
└─ Foreign Keys:
    - resena.usuario_id → usuario.usuario_id
    - resena.establecimiento_id → establecimiento.establecimiento_id
    - UNIQUE (usuario_id, establecimiento_id)

Ejemplo:
┌──────────────────────┐         ┌──────────────────────┐
│ USUARIO              │         │ ESTABLECIMIENTO      │
│ Juan                 │         │ Juan's Barbershop    │
├──────────────────────┤         ├──────────────────────┤
└──────────────────────┘         └──────────────────────┘
        │                               │
        │ N:1                           │ 1:N
        └───────────┬────────────────────┘
                    │
                    ▼
            ┌───────────────┐
            │ RESENA #1     │
            │ 5 ⭐⭐⭐⭐⭐    │
            │ "¡Excelente!" │
            └───────────────┘

IMPORTANTE: Juan solo puede dejar 1 resena en Juan's Barbershop
            Si intenta dejar otra, falla por UNIQUE constraint
```

### 7️⃣ ESTABLECIMIENTO ↔ AGENDA
```
Relación: 1 ESTABLECIMIENTO : 7 AGENDAS
├─ Un negocio TIENE 7 agendas (una por día)
├─ UNIQUE (establecimiento_id, dia_semana)
└─ Foreign Key: agenda.establecimiento_id → establecimiento.establecimiento_id

Ejemplo:
┌────────────────────────┐
│ ESTABLECIMIENTO        │
│ Juan's Barbershop      │
├────────────────────────┤
└────────────────────────┘
        │ 1:7
        │
┌───────┼───────┬────────┬────────┬────────┬────────┬────────┐
│       │       │        │        │        │        │        │
▼       ▼       ▼        ▼        ▼        ▼        ▼        ▼
LUNES  MARTES  MIER    JUEVES  VIERNES  SABADO  DOMINGO
9-18   9-18    9-18    9-18    9-18     10-17   CERRADO
```

### 8️⃣ ESTABLECIMIENTO ↔ SUSCRIPCION ↔ PLAN
```
Relación: 1 ESTABLECIMIENTO : 1 SUSCRIPCION : 1 PLAN
├─ Un negocio TIENE 1 suscripción activa (puede haber históricas)
├─ Una suscripción SE ASOCIA a 1 plan
├─ Un plan PUEDE tener N suscripciones
└─ Foreign Keys:
    - suscripcion.establecimiento_id → establecimiento.establecimiento_id
    - suscripcion.plan_id → plan.plan_id

Ejemplo:
┌────────────────────┐
│ ESTABLECIMIENTO    │
│ Juan's Barbershop  │
├────────────────────┤
└────────────────────┘
        │ 1:1
        │
        ▼
┌─────────────────────┐       ┌──────────────┐
│ SUSCRIPCION         │       │ PLAN         │
│ ACTIVA              │──────>│ PREMIUM      │
│ Desde: 1 Jan 2025  │ N:1   │ $9.99/mes    │
│ Hasta: 1 Feb 2025  │       │ 50 citas/mes │
└─────────────────────┘       └──────────────┘
```

### 9️⃣ USUARIO ↔ NOTIFICACION
```
Relación: 1 USUARIO : N NOTIFICACIONES
├─ Un usuario RECIBE múltiples notificaciones
├─ Una notificación ES PARA UN usuario
└─ Foreign Key: notificacion.usuario_id → usuario.usuario_id

Ejemplo (CLIENTE):
┌──────────────┐
│ USUARIO      │
│ Juan         │
├──────────────┤
└──────────────┘
        │ 1:N
        │
    ┌───┴────┬──────────┐
    │         │          │
    ▼         ▼          ▼
[Notif 1] [Notif 2] [Notif 3]
"Cita     "Nuevo   "Respon-"
confirma- mensaje" dió tu
da" ✓    ✓       mensaj"
```

---

## 📋 Tabla de Campos Clave

### USUARIO
```sql
CREATE TABLE usuario (
    usuario_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre VARCHAR(50) NOT NULL,
    apellido VARCHAR(50) NOT NULL,
    correo VARCHAR(100) UNIQUE NOT NULL,
    contrasena_hash VARCHAR(255) NOT NULL,
    rol_id INT FOREIGN KEY REFERENCES rol(rol_id),
    activo BOOLEAN DEFAULT TRUE,
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
```
**Valores de rol_id:**
- 1 = CLIENTE
- 2 = DUENO
- 3 = ADMIN

### ESTABLECIMIENTO
```sql
CREATE TABLE establecimiento (
    establecimiento_id INT PRIMARY KEY AUTO_INCREMENT,
    usuario_id INT FOREIGN KEY NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    direccion VARCHAR(255),
    latitud DECIMAL(9,6),     -- Ej: -12.047404
    longitud DECIMAL(9,6),    -- Ej: -77.042483
    telefono VARCHAR(20),
    activo BOOLEAN DEFAULT TRUE
);
```

### SERVICIO
```sql
CREATE TABLE servicio (
    servicio_id INT PRIMARY KEY AUTO_INCREMENT,
    establecimiento_id INT FOREIGN KEY NOT NULL,
    nombre VARCHAR(100) NOT NULL,
    descripcion TEXT,
    duracion INT NOT NULL,       -- En minutos
    precio DECIMAL(10,2) NOT NULL,
    activo BOOLEAN DEFAULT TRUE
);
```

### CITA
```sql
CREATE TABLE cita (
    cita_id INT PRIMARY KEY AUTO_INCREMENT,
    cliente_id INT FOREIGN KEY NOT NULL,
    servicio_id INT FOREIGN KEY NOT NULL,
    fecha DATE NOT NULL,
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    estado ENUM('PENDIENTE','CONFIRMADA','CANCELADA','COMPLETADA'),
    fecha_creacion TIMESTAMP DEFAULT NOW()
);
```
**Estados de cita:**
- PENDIENTE = Cliente reservó, espera confirmación del owner
- CONFIRMADA = Owner confirmó la cita
- COMPLETADA = Cita terminada, cliente puede dejar resena
- CANCELADA = Owner o cliente canceló

### AGENDA
```sql
CREATE TABLE agenda (
    agenda_id INT PRIMARY KEY AUTO_INCREMENT,
    establecimiento_id INT FOREIGN KEY NOT NULL,
    dia_semana ENUM('LUNES','MARTES','MIERCOLES','JUEVES','VIERNES','SABADO','DOMINGO'),
    hora_inicio TIME NOT NULL,
    hora_fin TIME NOT NULL,
    UNIQUE(establecimiento_id, dia_semana)
);
```

### MENSAJE
```sql
CREATE TABLE mensaje (
    mensaje_id INT PRIMARY KEY AUTO_INCREMENT,
    cita_id INT FOREIGN KEY,
    emisor_id INT FOREIGN KEY NOT NULL,
    contenido TEXT NOT NULL,
    fecha_envio TIMESTAMP DEFAULT NOW()
);
```

### RESENA
```sql
CREATE TABLE resena (
    resena_id INT PRIMARY KEY AUTO_INCREMENT,
    establecimiento_id INT FOREIGN KEY NOT NULL,
    usuario_id INT FOREIGN KEY NOT NULL,
    calificacion INT CHECK (calificacion BETWEEN 1 AND 5),
    comentario TEXT,
    fecha TIMESTAMP DEFAULT NOW(),
    UNIQUE(usuario_id, establecimiento_id)
);
```

### SUSCRIPCION
```sql
CREATE TABLE suscripcion (
    suscripcion_id INT PRIMARY KEY AUTO_INCREMENT,
    establecimiento_id INT FOREIGN KEY NOT NULL,
    plan_id INT FOREIGN KEY NOT NULL,
    estado ENUM('ACTIVA','CANCELADA','EXPIRADA'),
    fecha_inicio DATE NOT NULL,
    fecha_expiracion DATE NOT NULL,
    fecha_actualizacion TIMESTAMP
);
```

### PROFILE
```sql
CREATE TABLE profile (
    profile_id INT PRIMARY KEY AUTO_INCREMENT,
    establecimiento_id INT FOREIGN KEY UNIQUE NOT NULL,
    logo_url TEXT,
    portada_url TEXT,
    descripcion_larga TEXT
);
```

---

## 🎯 Flujo de Datos: Crear Cita

```
┌─────────────┐
│   CLIENTE   │
│   (Usuario) │
└──────┬──────┘
       │
       │ POST /api/v1/appointments
       │ {
       │   "cliente_id": 5,
       │   "servicio_id": 1,
       │   "fecha": "2025-01-30",
       │   "hora_inicio": "10:00",
       │   "hora_fin": "10:30"
       │ }
       │
       ▼
┌──────────────────┐
│    VALIDACION    │
├──────────────────┤
│✓ cliente_id OK   │
│✓ servicio_id OK  │
│✓ fecha future    │
│✓ hora valid      │
└──────┬───────────┘
       │
       ▼
┌────────────────────────────────┐
│  CREAR REGISTRO EN CITA        │
├────────────────────────────────┤
│ cita_id: 13                    │
│ cliente_id: 5                  │
│ servicio_id: 1                 │
│ fecha: 2025-01-30              │
│ hora_inicio: 10:00             │
│ hora_fin: 10:30                │
│ estado: PENDIENTE              │
│ fecha_creacion: NOW()          │
└────────────────────────────────┘
       │
       └─────┬───────────────┬──────────────┐
             │               │              │
             ▼               ▼              ▼
      ┌──────────────┐ ┌────────────┐ ┌──────────────┐
      │  NOTIFICAR   │ │ ACTUALIZAR │ │   RESPONSE   │
      │    OWNER     │ │  DASHBOARD │ │ {cita_id:13} │
      └──────────────┘ └────────────┘ └──────────────┘
```

---

## ⚙️ Constraints & Validaciones en BD

| Tabla | Constraint | Tipo | Descripción |
|-------|-----------|------|-------------|
| usuario | correo | UNIQUE | No hay dos usuarios con mismo email |
| usuario | rol_id | FK | Debe existir rol |
| establecimiento | usuario_id | FK | Debe existir usuario (dueño) |
| servicio | establecimiento_id | FK | Debe existir establecimiento |
| cita | cliente_id, servicio_id | FK | Ambos deben existir |
| cita | hora_fin > hora_inicio | CHECK | Validación de tiempo |
| agenda | (est_id, dia_semana) | UNIQUE | Un horario por día por negocio |
| agenda | hora_fin > hora_inicio | CHECK | Validación de tiempo |
| resena | (usuario_id, est_id) | UNIQUE | Un review por usuario por negocio |
| resena | calificacion | CHECK | Debe ser entre 1-5 |
| mensaje | cita_id, emisor_id | FK | Ambos deben existir |
| suscripcion | (est_id, plan_id) | N:1 | Relación válida |

---

## 🔐 Integridad Referencial

**ON DELETE CASCADE** (Si eliminas el padre, se eliminan los hijos):
- usuario → establecimientos, appointments, messages, etc.
- establecimiento → servicios, citas, agendas, reseñas
- servicio → citas
- cita → mensajes

**ON DELETE SET NULL** (Si eliminas padre, foreign key = NULL):
- usuario.rol_id (puede quedar NULL si rol se elimina, pero en BD rol es fijo)

---

## 📈 Crecimiento de Datos (Ejemplo)

Si tienes:
- 100 dueños
- 200 negocios (2 por dueño en promedio)
- 10 servicios por negocio = 2,000 servicios
- 50 citas por día × 365 días = 18,250 citas/año
- 1 resena por cada 10 citas = 1,825 resenas/año
- 5 mensajes por cita = 91,250 mensajes/año

**Tabla más grande: MENSAJE** ~100K registros/año

---

## 🧪 Casos de Test para Relaciones

```javascript
// Test 1: Crear cita invalida (servicio de otro negocio)
{
  cliente_id: 5,          // Cliente OK
  servicio_id: 1,         // Pertenece a establecimiento X
  // Pero cita queremos asignar a establecimiento Y
  // ← El backend debe validar esto
}

// Test 2: Owner no puede crear cita (solo cliente)
// POST /api/v1/appointments con rol=DUENO
// ← Debe retornar 403 Forbidden

// Test 3: Escribir en mensaje de otra cita
{
  cita_id: 10,  // No pertenece al usuario
  contenido: "Hola"
  // ← Backend valida que usuario sea cliente o owner de esa cita
}

// Test 4: Dejar 2 resenas en mismo negocio
// Primera: OK ✓
// Segunda: UNIQUE constraint error ✗

// Test 5: Confirmar cita de otro owner
{
  appointment_id: 5,
  estado: "CONFIRMADA"
  // ← Si usuario no es owner del servicio → 403
}
```

---

## 🎯 Summary de Relaciones

| De → A | Tipo | Campo FK | Comportamiento |
|--------|------|----------|----------------|
| Usuario → Rol | N:1 | usuario.rol_id | SET NULL |
| Usuario → Establecimiento | 1:N | est.usuario_id | CASCADE |
| Usuario → Cita (cliente) | 1:N | cita.cliente_id | CASCADE |
| Usuario → Mensaje (emisor) | 1:N | msg.emisor_id | CASCADE |
| Usuario → Reseña | 1:N | resena.usuario_id | CASCADE |
| Usuario → Notificación | 1:N | notif.usuario_id | CASCADE |
| Establecimiento → Servicio | 1:N | serv.est_id | CASCADE |
| Establecimiento → Agenda | 1:N | agenda.est_id | CASCADE |
| Establecimiento → Profile | 1:1 | profile.est_id | CASCADE |
| Establecimiento → Reseña | 1:N | resena.est_id | CASCADE |
| Establecimiento → Suscripción | 1:N | suscr.est_id | CASCADE |
| Servicio → Cita | 1:N | cita.serv_id | CASCADE |
| Cita → Mensaje | 1:N | msg.cita_id | CASCADE |
| Plan → Suscripción | 1:N | suscr.plan_id | - |

---

¿Necesitas profundizar en alguna relación específica o entender mejor cómo validar en el frontend?
