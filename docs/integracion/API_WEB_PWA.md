# API de Integracion - PWA (Angular 21)

Guia completa para la PWA de Booksmart orientada a `DUENO` y `TRABAJADOR`.
Esta version esta alineada con endpoints reales del backend actual.

## 1. Stack recomendado en Angular 21

- `HttpClient` + `provideHttpClient(withInterceptors(...))` para JWT.
- `Signals` para estado global de sesion, negocio seleccionado y feature gates.
- `RxJS` para polling liviano y composition de vistas (dashboard, calendario, chat).
- `SwPush` para registro Web Push en navegador.
- `WebSocket` nativo para tiempo real en `/api/v1/ws`.

## 2. Autenticacion y sesion

### Login
- `POST /api/v1/auth/login/access-token`

Body:

```json
{
	"email": "owner@negocio.com",
	"password": "******"
}
```

Respuesta esperada:

```json
{
	"access_token": "<jwt>",
	"token_type": "bearer"
}
```

### Uso del token
- Header en cada request protegido: `Authorization: Bearer <jwt>`.
- WebSocket: `wss://<host>/api/v1/ws?token=<jwt>`.

## 3. Flujo funcional PWA por modulos

### 3.1 Negocio (Establecimiento + Perfil)

- `GET /api/v1/establishments?user_id={ownerId}`: negocios del dueño.
- `GET /api/v1/establishments/{establishment_id}`: detalle del negocio.
- `POST /api/v1/establishments`: crear establecimiento.
- `PUT/PATCH /api/v1/establishments/{establishment_id}`: editar negocio.
- `GET /api/v1/profiles?establecimiento_id={id}` o por id de perfil.
- `POST /api/v1/profiles`, `PUT/PATCH /api/v1/profiles/{profile_id}`.

Nota: en backend actual no existe `/establishments/me` ni `/profiles/me`.

### 3.2 Servicios

- `GET /api/v1/services?establishment_id={id}`
- `POST /api/v1/services`
- `PUT/PATCH /api/v1/services/{service_id}`
- `DELETE /api/v1/services/{service_id}`

### 3.3 Workers

- `GET /api/v1/workers?establecimiento_id={id}`
- `POST /api/v1/workers`
- `PUT/PATCH /api/v1/workers/{worker_id}`
- `DELETE /api/v1/workers/{worker_id}`

### 3.4 Agendas

- `GET /api/v1/agendas?establecimiento_id={id}`
- `POST /api/v1/agendas`
- `POST /api/v1/agendas/bulk` para carga masiva semanal.
- `PUT/PATCH /api/v1/agendas/{agenda_id}`
- `DELETE /api/v1/agendas/{agenda_id}`

Nota de negocio:
- El horario semanal sigue siendo la base de disponibilidad.
- Para feriados, eventos o días no laborables, el backend expone cierres especiales por fecha.
- Esos cierres no reemplazan el horario semanal; solo bloquean la disponibilidad en fechas puntuales.

### 3.5 Citas (core operativo)

- `GET /api/v1/appointments` con filtros (`servicio_id`, etc).
- `GET /api/v1/appointments/{appointment_id}`
- `PUT/PATCH /api/v1/appointments/{appointment_id}`
- `POST /api/v1/appointments/{appointment_id}/accept`
- `POST /api/v1/appointments/{appointment_id}/decline`

Slot discovery para UI:

- `GET /api/v1/appointments/availability/slots?servicio_id={id}&target_date=YYYY-MM-DD`

Respuesta ampliada recomendada:

```json
{
	"date": "2026-04-12",
	"servicio_id": 10,
	"available_slots": ["09:00", "10:00"],
	"busy_slots": ["11:00"],
	"closed": false,
	"closure_reason": null
}
```

Comportamiento esperado en frontend:
- Si `closed` es `true`, no permitir reserva.
- Si `closure_reason` existe, mostrar el motivo del cierre.
- Si el cliente ignora los campos nuevos, la integracion sigue funcionando igual.

### 3.6 Mensajeria en cita

- `GET /api/v1/messages?cita_id={appointment_id}`
- `POST /api/v1/messages`
- `PUT/PATCH /api/v1/messages/{message_id}`

Regla clave: `emisor_id` debe coincidir con el usuario autenticado.

### 3.7 Notificaciones

- `GET /api/v1/notifications/me`
- `PATCH /api/v1/notifications/{notification_id}` (ejemplo: `leida=true`)

Tiempo real:
- `WS /api/v1/ws?token=<jwt>`
- Eventos server: `notification`, `message`, `appointment`, `ping`.
- Evento cliente: `{"type":"mark_read","id":123}`.

### 3.8 Web Push en PWA

- `POST /api/v1/push-subscriptions`
- `GET /api/v1/push-subscriptions`
- `DELETE /api/v1/push-subscriptions?endpoint=<...>`

Payload de registro:

```json
{
	"endpoint": "https://fcm.googleapis.com/fcm/send/...",
	"keys": {
		"p256dh": "...",
		"auth": "..."
	}
}
```

## 4. Planes y features (impacto en la PWA)

### 4.1 Donde se gestiona

- Planes: `GET /api/v1/plans`, `POST/PUT/PATCH /api/v1/plans/{id}` (admin para escritura).
- Features por plan: `GET/POST /api/v1/plan-features`.
- Suscripcion por establecimiento: `GET /api/v1/subscriptions?establecimiento_id={id}`.

### 4.2 Features relevantes para producto

- `ANALYTICS_OCUPACION`: habilita consumo de ocupacion.
- `SUGERIR_PROMOS`: habilita sugerencias/promos.
- `AUTO_REMINDERS`, `AUTO_CONFIRMACION`, `AUTO_RECOVERY`, `AUTO_RESEÑA_PROMPT`: automatizaciones.
- `DESTACADO_LISTING`, `CAMPAÑAS_VISIBILIDAD`: visibilidad prioritaria.
- `REPORTES_AVANZADOS`: reporteria premium.

### 4.3 Comportamiento recomendado en frontend

- Cargar suscripcion y features al entrar a negocio.
- Guardar en estado (`signals`) y condicionar UI:
	- Ocultar modulo analytics si falta `ANALYTICS_OCUPACION`.
	- Ocultar sugerencias si falta `SUGERIR_PROMOS`.
	- Mostrar badge de plan y upsell contextual.

## 5. Analiticas para la PWA (owner)

Endpoints:

- `POST /api/v1/analytics/occupancy/recalculate/{establecimiento_id}`
- `GET /api/v1/analytics/occupancy/?establecimiento_id={id}&fecha=YYYY-MM-DD`
- `GET /api/v1/analytics/occupancy/idle-times?establecimiento_id={id}`
- `GET /api/v1/analytics/suggestions/?establecimiento_id={id}`
- `GET /api/v1/analytics/suggestions/unread?establecimiento_id={id}`
- `PUT /api/v1/analytics/suggestions/{sugerencia_id}/mark-read`
- `PUT /api/v1/analytics/suggestions/{sugerencia_id}/mark-implemented`
- `GET /api/v1/analytics/dashboard/{establecimiento_id}`

Feature gating backend:
- Si el plan no tiene feature, backend responde `403`.

## 6. Automatizaciones y notificaciones automaticas

El backend ya tiene modulo `auto-notifications`, pero en la API actual:

- Admin tiene control total (`GET/POST/PUT/PATCH/DELETE`).
- Owner no tiene listado global habilitado actualmente (`403` en `GET /auto-notifications`).

Recomendacion PWA:
- Consumir notificaciones operativas via `notifications` + `ws`.
- Tratar `auto-notifications` como modulo administrativo/interno hasta abrir filtros owner.

## 7. Visibilidad prioritaria (planes)

La visibilidad prioritaria se representa por features:

- `DESTACADO_LISTING`
- `CAMPAÑAS_VISIBILIDAD`

Backend actual:
- Define y persiste estas features por plan.
- No expone aun un endpoint dedicado de ranking/promocion visual para PWA.

Recomendacion:
- Mostrar estado de visibilidad en pantalla de plan/suscripcion.
- Si se requiere ranking en listados publicos, crear endpoint dedicado en siguiente fase.

## 8. Orden sugerido de integracion en Angular 21

1. Auth + interceptor JWT.
2. Selector de establecimiento (multi-negocio owner).
3. Servicios/agendas.
4. Calendario de citas + `accept/decline`.
5. Chat por cita + WS.
6. Notificaciones + Web Push.
7. Suscripcion/features + feature flags en UI.
8. Analytics/suggestions premium.

## 9. Checklist de release PWA

- Manejo de `403` por feature y por ownership.
- Reintentos para WS + heartbeat (`ping/pong`).
- Registro/desregistro de push al login/logout.
- Logs de UX para cambios de estado de cita.
- Pruebas con owner `FREE` y `PREMIUM`.
