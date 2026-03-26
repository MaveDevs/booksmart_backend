# API Referencia - Aplicación Móvil (Cliente Final)

Este documento es una guía extensa para el Frontend de la aplicación Mobile (iOS/Android). Explica los llamados a los endpoints del **Booksmart** backend para lograr que un usuario encuentre un negocio, agende, califique su experiencia, chatee, y consuma notificaciones.

---

## 🔐 Identidad de Cliente
- **`POST /api/v1/users/`**: Registro nativo (Sign-up) rellenando campos mínimos.
- **`POST /api/v1/auth/login/access-token`**: Loguearse. Asigna el token nivel `CLIENTE` (rol ID 1).
- **`GET /api/v1/profiles/me`**: Leer datos del perfil, como foto o datos de contacto.
- **`PUT /api/v1/profiles/me`**: Editar sus propios detalles.

## 🔎 Exploración de Catálogos (Negocios y Servicios)
El negocio en plan Pro goza de Boost (visualización destacada).
- **`GET /api/v1/establishments/`**: Búsqueda global con parámetros (Ej. Filtros espaciales `lat/long` o Categorías si implementas un parámetro `query="Peluquería"`). Trae la lista de las estéticas con estrellas.
- **`GET /api/v1/establishments/{id}`**: Perfil semipúblico: Trae reviews, nombre, fotos galería.
- **`GET /api/v1/services/?establishment_id=X`**: Llama a todos los servicios que un negocio dado vende (`precio, titulo, duracion_minutos`).

## 🗓 Comprobación de Horarios Disponibles
- **`GET /api/v1/appointments/availability/slots`**: Endpoint de cálculo automático. La app dicta el `servicio_id` y `target_date`, y backend escupe un arreglo `available_slots: ["10:30", "11:00"]` que están garantizados a no empalmar y respetar el break de comida de la `Agenda` del negocio.

## ✅ Cierre y Reservación (Booking)
- **`POST /api/v1/appointments/`**: Confirmar al seleccionarlo. Nace como PENDIENTE.
- **`GET /api/v1/appointments/me`**: Para poblar la vista del cliente "Mis Reservas del Mes" (Filtradas implícitamente por su token).
- **`PATCH /api/v1/appointments/{id}`**: Por el rol de CLIENTE, la seguridad solo le permite setear la constante a `"CANCELADA"` si decide abortar su viaje de manera anticipada. O si cambia su servicio de uñas por pedicure, etc.
- **`POST /api/v1/payments/`**: En caso de requerir "Hook" de anticipo con Stripe (Ej. Transferencias bancarias validadas u otras pasarelas). Trae su control de estados.

## 🗣 Interacciones (Notificaciones Push y Chats en Cita)
En Booksmart la mensajería es transitoria o atada a una cita viva.
- **`POST /api/v1/push-subscriptions/`**: Al arrancar la App Mobile y dar "YES" en permisos de iOS, se vincula el Token Firebase/APNs.
- **`GET /api/v1/notifications/`**: Bandeja de entrada de Alertas para renderizar campanitas (Ej. *"Tu pago fue exitoso"* / *"El Barbero aceptó tu cita"*).
- **`GET /api/v1/messages/?cita_id=X`**: Mensajes tipo WhatsApp hacia la PWA de la sucursal para informar demoras (`ws://dominio.com/api/v1/ws`).

## ⭐ Post-Servicio (Reviews y Ranking)
- **`POST /api/v1/ratings/`**: Se dispara el día después de que el barbero/pwa marcara la cita como COMPLETADA en su Dashboard. El cliente deja de `1` a `5` Estrellitas en el servicio o el local y este feedback alimenta el rating general en la lista de Búsqueda de Locales.
- **`GET /api/v1/ratings/?establishment_id=X`**: Visualización de los Testimonios en el perfil público del local para los consumidores curiosos.
