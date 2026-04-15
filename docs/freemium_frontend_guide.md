# Guía de Integración Freemium: Frontends

Esta guía detalla los requisitos y tareas específicas para cada uno de los frontends de Booksmart para soportar el modelo de negocio Freemium.

---

## 1. Conceptos Compartidos (Base)
Todos los frontends deben entender el modelo de `Subscription` y `PlanFeature`.
*   **Endpoint Clave**: `GET /api/v1/subscriptions/my-establishment` (devuelve el plan activo y sus features).
*   **Regla de Oro**: Nunca ocultar funciones sin explicar por qué. Usar "locked states" para fomentar el upgrade.

---

## 2. PWA: Dashboard del Socio (Angular)
**Público:** Dueños de negocios. Es el frontend donde más se "siente" el freemium.

### Necesidades Técnicas:
1.  **Interyectores de Pago (Soft Paywalls)**:
    *   Implementar un componente UI de "Feature Bloqueada" que se superponga a secciones Premium (Analíticas, Automatizaciones).
    *   Botón de acción: `Ir a Planes`.
2.  **Flujo de Suscripción**:
    *   Integración con Stripe o pasarela elegida para capturar el pago.
    *   Actualización de estado en tiempo real (vía WebSockets/RealtimeService) para desbloquear funciones inmediatamente después del pago.
3.  **Gestión de Cuotas**:
    *   Si el plan FREE tiene un límite de "Máximo 3 servicios", el formulario de creación debe mostrar un contador: `Servicios: 2/3`.
    *   Deshabilitar el botón "Crear" al llegar al límite con un tooltip: "Mejora a Pro para añadir más".

### UX Requerida:
*   **Badges de Estatus**: Mostrar un badge "PRO" o "PREMIUM" cerca del logo del negocio en el sidebar para reforzar el valor del estatus.

---

## 3. App Móvil: Cliente (Flutter)
**Público:** Usuarios finales que buscan y reservan. El freemium aquí es de "Visibilidad".

### Necesidades Técnicas:
1.  **Etiquetas de Prioridad**:
    *   En el listado de resultados (`Nearby`), resaltar visualmente a los negocios Premium.
    *   Usar un ribete o icono de "Destacado".
2.  **Algoritmo de Ordenamiento**:
    *   Asegurar que la búsqueda respete el `ranking_score` enviado por el backend (que ya incluye el bono por suscripción).
3.  **Filtros Avanzados**:
    *   Podrias permitir que el usuario filtre por "Negocios Top" (solo Premium).

### UX Requerida:
*   **Percepción de Calidad**: Los negocios premium deben lucir más "confiables" visualmente.

---

## 4. Web Admin Panel (Angular - Interno)
**Público:** Equipo interno de Booksmart. Es donde se configura el negocio.

### Necesidades Técnicas:
1.  **CRUD de Planes y Features**:
    *   Interfaz para crear nuevos planes (ej. "Plan Trial 7 días").
    *   Editor de la matriz de features: Marcar qué `feature_key` pertenece a qué `plan_id`.
2.  **Gestión de Suscripciones Manuales**:
    *   Botón para "Regalar Premium" a un negocio específico por tiempo limitado (Cortesia/Venta manual).
3.  **Dashboard de Ingresos (MRR)**:
    *   Métricas de cuántos usuarios han pasado de Free a Pro esta semana.
    *   Tasa de cancelación (Churn).

### UX Requerida:
*   **Funcional y Analítica**: No necesita ser tan estética como la PWA, pero sí muy precisa en los datos.

---

## Resumen de Tareas para Mañana por Perfil:

| Frontend | Tarea Prioritaria | Objetivo |
| :--- | :--- | :--- |
| **PWA** | Implementar Check de Features | Bloquear Analíticas si no es Pro. |
| **Flutter** | Diseño de Tarjeta "Destacada" | Diferenciar negocios Premium en el mapa. |
| **Admin** | Editor de Planes | Poder cambiar precios y features desde la web. |

---

