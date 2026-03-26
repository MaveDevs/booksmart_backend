# API Referencia - Aplicación PWA Web (Dueños y Trabajadores)

Este documento centraliza los endpoints operacionales que consume la Progressive Web App (PWA) de **Booksmart**. Esta herramienta es usada por los negocios para administrar su catálogo interno, horarios, y despachar citas.

---

## 🔐 Autenticación
- **`POST /api/v1/auth/login/access-token`**: Loguear a un "Dueño" o a un "Trabajador". Devuelve el JWT.

## 🏪 Configuración de Negocio (Establecimiento y Servicios)
El negocio gestiona su propia vitrina (información pública, qué servicios ofrece y cuánto cuestan).
- **`GET /api/v1/establishments/me`**: Carga el perfil del negocio logueado.
- **`PUT /api/v1/establishments/me`**: Editar nombre comercial, logo, descripción o ubicación geográfica.
- **`GET /api/v1/services/` (con filtrado por `establecimiento_id`)**: Listar todos los servicios del local.
- **`POST /api/v1/services/`**: Dar de alta un nuevo servicio (Ej: "Decoloración - $500 - 1Hr").
- **`PUT /api/v1/services/{id}`**: Modificar un servicio y marcarlo como exclusivo o general.
- **`DELETE /api/v1/services/{id}`**: Archivar servicio (Borrado lógico para no perder histórico).

## 👥 Empleados (Trabajadores de Nómina)
Invitar a trabajadores a unirse al establecimiento. Como acordamos, el backend automágicamente les generará una cuenta de `Usuario` (TRABAJADOR) con contraseña nativa.
- **`GET /api/v1/workers/`**: Listar a la plantilla del negocio.
- **`POST /api/v1/workers/`**: Registrar empleado (`nombre, email`). Internamente el backend mapea su `usuario_id` para que pueda loguearse a la PWA con la temporal "WorkerTemp123!".
- **`PUT /api/v1/workers/{id}`**: Reasignar rol, vacaciones o despedir.

## 🕒 Horarios de Atención (Agendas)
Decidir cuándo el personal y el negocio laboran para bloquear inteligentemente la app cliente.
- **`GET /api/v1/agendas/`**: Leer las horas operativas del día/semana del negocio o de un *worker* en particular.
- **`POST /api/v1/agendas/`**: Fijar horarios: Lunes(09:00 - 18:00), comida(13:00 - 14:00).
- **`PUT /api/v1/agendas/{id}`**: Modificar urgencia de cierre (Ej. "Cerrar hoy temprano").

## 📅 Bandeja de Entrada y Contingencias de Citas
Aquí recae el trabajo del día a día (Control del Plan Freemium vs Pro).
- **`GET /api/v1/appointments/`**: Lista filtrada en matriz de las citas agendadas y por aceptar.
- **`POST /api/v1/appointments/{id}/accept`**: Aceptación manual de cita pendiente (La pasa a CONFIRMADA).
- **`POST /api/v1/appointments/{id}/decline`**: Intercambia cita a CANCELADA y libera el "Slot" a la App móvil automáticamente.
- **`PATCH /api/v1/appointments/{id}`**: Actualizar la cita a COMPLETADA (para cerrar tickets) o *reprogramar en caliente* una hora de inicio si el cliente está atorado en tráfico.

## 💭 Interacciones en Tiempo Real & Auto-Recordatorios
- **`GET /api/v1/messages/`**: Bandeja de chat ligada a la Cita.
- **`POST /api/v1/messages/`**: Escribir un recado al cliente. Socket despachado a la App Móvil.
- **`POST /api/v1/push-subscriptions/`**: Habilitar PWA para recibir notificaciones sonoras cuando llegue una reserva.
- **`GET /api/v1/auto-notifications/`**: (Solo Planes PRO) Configurar plantillas de "Aviso de llegada en 30 minutos vía SMS".

## 💳 Pagos Logísticos y Analíticas (Planes de Pago)
- **`GET /api/v1/analytics/ocupacion`**: Reporte semanal para saber porcentaje de ocupación (horas libres VS horas trabajadas) e identificar ineficiencias monetarias.
- **`GET /api/v1/payments/`**: Listar depósitos parciales dejados por clientes mediante tarjeta en Stripe/PayPal.
- **`PATCH /api/v1/subscriptions/upgrade`**: Pagar la suscripción a Booksmart Pro/Premium y desbloquear las Analíticas y Notificaciones automáticas.
