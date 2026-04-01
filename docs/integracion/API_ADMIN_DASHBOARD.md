# API Referencia - Dashboard Administrador (Superadmin)

Este documento detalla todos los endpoints expuestos para el control total de la plataforma **Booksmart**. Solo los usuarios con `rol_id = 3` (ADMIN) tienen autorización para consumirlos. Su propósito es alimentar el Panel Web Administrativo donde se gestiona el soporte, la facturación y la moderación del sistema.

---

## 🔐 Autenticación y Cuentas
- **`POST /api/v1/auth/login/access-token`**: Loguearse en el panel con correo y contraseña. Devuelve un JWT con permisos nivel Admin.

## 👥 Control de Usuarios y Roles (Catálogos)
Permite al Superadmin visualizar, bloquear o crear todas las entidades humanas del sistema.
- **`GET /api/v1/users/`**: Listar a todos los clientes, dueños y trabajadores del sistema.
- **`GET /api/v1/users/{id}`**: Ver expediente completo de un usuario.
- **`PUT /api/v1/users/{id}`**: Actualizar datos o cambiar roles.
- **`PATCH /api/v1/users/{id}`**: Suspender/Banear a un usuario temporalmente (`activo: false`).
- **`GET /api/v1/roles/`**: Listar todos los roles del sistema (Cliente, Dueño, Admin, Trabajador).

## 🏪 Moderación de Negocios (Establecimientos)
- **`GET /api/v1/establishments/`**: Listar todos los negocios registrados en la plataforma.
- **`PATCH /api/v1/establishments/{id}`**: Activar o desactivar (Banear) un modelo de negocio completo si incumple reglas.
- **`DELETE /api/v1/establishments/{id}`**: Borrado lógico o físico del establecimiento.

## 💰 Monetización: Planes y Suscripciones (Catálogos Base)
Endpoints para controlar los planes que puede elegir un negocio (Freemium, Pro, etc).
- **`POST /api/v1/plans/`**: Crear un nuevo modelo de Plan de suscripción dictando su precio.
- **`PUT /api/v1/plans/{id}`**: Modificar precio o capacidad de un plan.
- **`POST /api/v1/plan-features/`**: Configurar qué "Features" (Analíticas, Auto-notificaciones) se encienden según el Plan elegido.
- **`GET /api/v1/subscriptions/`**: Visualizar el histórico de pagos y suscripciones de todos los locales hacia la plataforma Booksmart.

## 🚩 Quejas y Soporte Técnico (Reportes)
- **`GET /api/v1/reports/`**: Bandeja de entrada de quejas (Ej: Un cliente reportó a un establecimiento por fraude).
- **`PATCH /api/v1/reports/{id}`**: Marcar reporte como `PENDIENTE`, `EN_REVISION`, `RESUELTO` o `RECHAZADO`.

## 📊 Analíticas Globales del Sistema
- **`GET /api/v1/analytics/system-overview`**: Métricas globales operativas de toda la plataforma (usuarios, establecimientos, citas, suscripciones e ingresos).
