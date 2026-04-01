# API de Integracion - App Movil (Flutter)

Guia operativa para iOS/Android enfocada en `CLIENTE`.
Incluye booking, chat, notificaciones, reseñas y consideraciones por planes del negocio.

## 1. Stack recomendado en Flutter

- `dio` o `http` para REST.
- Interceptor para `Authorization: Bearer <jwt>`.
- `web_socket_channel` para realtime en `/api/v1/ws`.
- `riverpod`/`bloc` para estado de sesion y reservas.
- `flutter_secure_storage` para token.

## 2. Identidad de cliente

### Registro
- `POST /api/v1/users/`

Body base:

```json
{
	"nombre": "Ana",
	"apellido": "Perez",
	"correo": "ana@mail.com",
	"contrasena": "******",
	"rol_id": 1,
	"activo": true
}
```

### Login
- `POST /api/v1/auth/login/access-token`

```json
{
	"email": "ana@mail.com",
	"password": "******"
}
```

### Perfil de usuario
- `GET /api/v1/users/me`
- `GET /api/v1/users/{id}` (propio o admin)
- `PUT/PATCH /api/v1/users/{id}` (propio o admin)

Nota: en backend actual no existe `/profiles/me`.

## 3. Exploracion de negocios y servicios

- `GET /api/v1/establishments`
- `GET /api/v1/establishments/{establishment_id}`
- `GET /api/v1/services?establishment_id={id}`
- `GET /api/v1/ratings?establishment_id={id}`

Uso recomendado en Flutter:
- Pantalla Home: `establishments` + score promedio calculado desde `ratings`.
- Pantalla Negocio: detalle + servicios + reseñas.

## 4. Disponibilidad y booking

### Slots disponibles
- `GET /api/v1/appointments/availability/slots?servicio_id={id}&target_date=YYYY-MM-DD`

### Crear reserva
- `POST /api/v1/appointments`

```json
{
	"cliente_id": 11,
	"servicio_id": 7,
	"fecha": "2026-04-01",
	"hora_inicio": "10:00:00",
	"hora_fin": "10:30:00",
	"estado": "PENDIENTE"
}
```

### Consultar y gestionar reservas del cliente
- `GET /api/v1/appointments/me`
- `GET /api/v1/appointments/{appointment_id}`
- `PATCH /api/v1/appointments/{appointment_id}` (ejemplo: cancelar)

Estados usados:
- `PENDIENTE`
- `CONFIRMADA`
- `CANCELADA`
- `COMPLETADA`

## 5. Chat en contexto de cita

- `GET /api/v1/messages?cita_id={appointment_id}`
- `POST /api/v1/messages`

```json
{
	"cita_id": 321,
	"emisor_id": 11,
	"contenido": "Voy 10 min tarde"
}
```

Regla: `emisor_id` debe ser el usuario autenticado.

## 6. Notificaciones (in-app + realtime)

### API REST
- `GET /api/v1/notifications/me`
- `PATCH /api/v1/notifications/{notification_id}` (ejemplo: `leida=true`)

### WebSocket
- `WS /api/v1/ws?token=<jwt>`

Eventos del servidor:
- `notification`
- `message`
- `appointment`
- `ping`

Eventos del cliente:

```json
{"type":"ping"}
```

```json
{"type":"mark_read","id":123}
```

## 7. Push notifications en Flutter

El endpoint `push-subscriptions` actual usa contrato Web Push (`endpoint`, `p256dh`, `auth`), ideal para PWA navegador.

Para mobile Flutter nativo:
- Puedes usar `notifications` + `ws` inmediatamente.
- Si quieres FCM/APNs puro, se recomienda extender backend con un endpoint específico de device tokens mobile.

## 8. Pagos

En el backend actual, `payments` es de `DUENO/ADMIN` y no de cliente final:

- `GET /api/v1/payments` (owner/admin)
- `GET /api/v1/payments/{payment_id}` (owner/admin)
- `POST /api/v1/payments` (admin)

Para app cliente, el estado de pago debe reflejarse por:

- estado de reserva (`appointments`)
- notificaciones (`notifications/me`)
- eventos realtime (`ws`)

## 9. Reseñas (post servicio)

- `POST /api/v1/ratings`
- `GET /api/v1/ratings/me`
- `GET /api/v1/ratings?establishment_id={id}`

Flujo recomendado:
1. Detectar citas `COMPLETADA` en `appointments/me`.
2. Mostrar CTA de reseña.
3. Enviar rating y comentario.

## 10. Impacto de planes del negocio en experiencia mobile

Los planes aplican al establecimiento, no al cliente, pero afectan la experiencia visible:

- `DESTACADO_LISTING` y `CAMPAÑAS_VISIBILIDAD`:
	- Negocios premium pueden priorizarse en listados (segun logica de ranking en frontend/backend).
- `AUTO_REMINDERS` / `AUTO_CONFIRMACION` / `AUTO_RECOVERY`:
	- El cliente recibe mas eventos de estado y recordatorios.
- `ANALYTICS_OCUPACION` / `SUGERIR_PROMOS`:
	- Impactan al owner, pero terminan mejorando promos y ocupacion visible para cliente.

## 11. Checklist de integracion Flutter

1. Login + guardado seguro de JWT.
2. Interceptor HTTP con refresh de sesion (si aplica en app).
3. Home de negocios + detalle + servicios.
4. Flujo de reserva con slots.
5. Mis citas + cancelacion.
6. Chat por cita.
7. Notificaciones REST + WebSocket.
8. Reseñas post-servicio.
9. Manejo uniforme de errores `401`, `403`, `404`.
