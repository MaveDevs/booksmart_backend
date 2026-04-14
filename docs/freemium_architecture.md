# Arquitectura y Estrategia Freemium - Booksmart Backend

Este documento detalla el diseño, la implementación actual y la hoja de ruta para el modelo de negocio Freemium de Booksmart.

## 1. Visión General
El objetivo del modelo Freemium es permitir el uso básico de la plataforma para captar negocios (adquisición), mientras se monetizan las funciones avanzadas, el ahorro de tiempo (automatizaciones) y la visibilidad premium.

---

## 2. Componentes del Núcleo

### A. Catálogo de Planes (`Plan`)
Define los niveles de servicio. Actualmente existen:
*   **FREE**: Funcionalidad básica, sin automatizaciones, ranking estándar.
*   **PREMIUM / PRO**: Full acceso, automatizaciones activas, boost en búsquedas.

### B. Matriz de Capacidades (`PlanFeature`)
En lugar de "hardcodear" checks de `plan_id == 2`, el sistema utiliza una matriz de características (`feature_key`). Esto permite crear mini-planes o promociones sin cambiar el código de los endpoints.

**Features Definidas (`FeatureKey`):**
*   `AUTO_REMINDERS`: Envío automático de notificaciones de recordatorio.
*   `DESTACADO_LISTING`: Multiplicador de visibilidad en el algoritmo de búsqueda.
*   `ANALYTICS_OCUPACION`: Acceso a métricas de productividad.
*   `REPORTES_AVANZADOS`: Reportes detallados de clientes y ventas.

### C. Estado de Usuario (`Subscription`)
Vincula un establecimiento con un plan. 
*   **Importante**: Una suscripción tiene un `estado` (ACTIVA, EXPIRADA, CANCELADA) y una `fecha_fin`. El sistema de ranking solo considera suscripciones **ACTIVAS**.

---

## 3. Implementación Sugerida: "The Feature Guardian" (Enforcement)

Para evitar repetir consultas a la base de datos en cada endpoint, se recomienda implementar una **Dependencia de FastAPI** que verifique si un negocio tiene permiso para usar una función:

```python
# app/api/deps.py (Propuesta de implementación)

def require_feature(feature_key: FeatureKey):
    """
    Dependencia para proteger endpoints PRO.
    Lanza 403 si el negocio no tiene el feature habilitado.
    """
    def _verifier(
        establishment_id: int, 
        db: Session = Depends(get_db)
    ):
        has_feature = db.query(PlanFeature)\
            .join(Subscription, PlanFeature.plan_id == Subscription.plan_id)\
            .filter(Subscription.establecimiento_id == establishment_id)\
            .filter(Subscription.estado == "ACTIVA")\
            .filter(PlanFeature.feature_key == feature_key)\
            .filter(PlanFeature.enabled == True)\
            .first()
        
        if not has_feature:
            raise HTTPException(
                status_code=403, 
                detail=f"El feature {feature_key} requiere una suscripción Premium activa."
            )
        return True
    return _verifier

# USO EN ROUTER:
@router.get("/advanced-stats")
def get_stats(
    establishment_id: int,
    _ = Depends(require_feature(FeatureKey.ANALYTICS_OCUPACION))
):
    # Solo llega aqui si es PREMIUM
    ...
```

---

## 4. Hoja de Ruta - Corto Plazo (Quick Wins)

### Fase 1: Auto-Provisioning (Mañana)
Modificar `crud_establishments.create_establishment` para que al crear un negocio, se le asigne el plan "FREE" por defecto.
*   *Meta:* Cero negocios "sin plan". Evita errores de visualización en la PWA.

### Fase 2: Cuotas y Límites (Usage Limits)
Extender la lógica para que los negocios gratuitos tengan límites físicos.
*   Ejemplo: Máximo de trabajadores o servicios permitidos en plan FREE.

### Fase 3: Ranking Dinámico (Optimización)
Asegurar que el algoritmo de búsqueda en `get_establishments_nearby` priorice siempre a los PRO, pero permitiendo que la cercanía siga siendo un factor relevante para no arruinar la UX.

---

