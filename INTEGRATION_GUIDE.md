"""
INTEGRATION GUIDE - How to hook automation into existing CRUD operations

This guide shows how to optionally integrate the new notification orchestrator
into existing CRUD operations WITHOUT modifying existing code.

All integrations are backward compatible and can be added incrementally.
"""

# ============================================================================
# INTEGRATION PHASE 1: Appointment Notifications
# ============================================================================
#
# To enable automatic notifications for appointments, add these hooks to:
# app/crud/crud_appointments.py
#
# In the create_appointment() function, after db.refresh():
# ──────────────────────────────────────────────────────────────────────────
#
# from app.services.notification_orchestrator import orchestrator
# from app.crud.crud_services import get_service
#
#     db_appointment = ...  # existing code
#     db.refresh(db_appointment)
#
#     # NEW: Trigger notification orchestration (non-blocking)
#     service = get_service(db, db_appointment.servicio_id)
#     if service:
#         orchestrator.on_appointment_created_sync(
#             db, db_appointment.cita_id, service.establecimiento_id
#         )
#
#     return db_appointment
#
# ──────────────────────────────────────────────────────────────────────────
#
# In the update_appointment() function, after db.refresh():
# ──────────────────────────────────────────────────────────────────────────
#
#     db_appointment = ...  # existing code
#     db.refresh(db_appointment)
#
#     # NEW: Detect status changes and trigger notifications
#     new_status = appointment.model_dump(exclude_unset=True).get("estado")
#     if new_status:
#         service = get_service(db, db_appointment.servicio_id)
#         if not service:
#             return db_appointment
#
#         if new_status == "CONFIRMADA":
#             orchestrator.on_appointment_confirmed_sync(
#                 db, db_appointment.cita_id, service.establecimiento_id
#             )
#         elif new_status == "COMPLETADA":
#             orchestrator.on_appointment_completed_sync(
#                 db, db_appointment.cita_id, service.establecimiento_id
#             )
#         elif new_status == "CANCELADA":
#             orchestrator.on_appointment_cancelled_sync(
#                 db, db_appointment.cita_id, service.establecimiento_id
#             )
#
#     return db_appointment
#
# ──────────────────────────────────────────────────────────────────────────


# ============================================================================
# INTEGRATION PHASE 2: Message Notifications
# ============================================================================
#
# To enable automatic notifications for messages, add this hook to:
# app/crud/crud_messages.py
#
# In the create_message() function, after db.refresh():
# ──────────────────────────────────────────────────────────────────────────
#
# from app.services.notification_orchestrator import orchestrator
# from app.crud.crud_appointments import get_appointment
# from app.crud.crud_services import get_service
#
#     db_message = ...  # existing code
#     db.refresh(db_message)
#
#     # NEW: Trigger notification for new message
#     appointment = get_appointment(db, db_message.cita_id)
#     if appointment:
#         service = get_service(db, appointment.servicio_id)
#         if service:
#             orchestrator.on_message_received_sync(
#                 db, db_message.mensaje_id, service.establecimiento_id
#             )
#
#     return db_message
#
# ──────────────────────────────────────────────────────────────────────────


# ============================================================================
# INTEGRATION PHASE 3: Feature Gating in Endpoints
# ============================================================================
#
# To gate features (e.g., prevent FREE plan users from accessing premium
# analytics), add checks to endpoints:
#
# Example in app/api/v1/endpoints/analytics.py or new endpoint:
# ──────────────────────────────────────────────────────────────────────────
#
# from app.core.feature_gating import establishment_has_feature, assert_establishment_has_feature
# from app.models.plan_features import FeatureKey
#
# @router.get("/analytics/{establishment_id}")
# def get_advanced_analytics(
#     establishment_id: int,
#     db: Session = Depends(deps.get_db),
#     current_user: User = Depends(require_owner_or_admin()),
# ):
#     # Check if establishment's plan has ANALYTICS_OCUPACION feature
#     try:
#         assert_establishment_has_feature(
#             db, establishment_id, FeatureKey.ANALYTICS_OCUPACION
#         )
#     except ValueError:
#         raise HTTPException(
#             status_code=403,
#             detail="This feature requires a PREMIUM plan"
#         )
#
#     # ... rest of endpoint code
#
# ──────────────────────────────────────────────────────────────────────────


# ============================================================================
# INTEGRATION PHASE 4: Analytics Data Ingestion (Worker Job)
# ============================================================================
#
# To populate occupancy analytics, create a background job that:
# 1. Runs daily or on-demand
# 2. For each establishment with ANALYTICS_OCUPACION feature:
#    - Query all appointments for that date
#    - Group by time slot (1-hour buckets)
#    - Calculate rates (ocupacion, no-show, cancelacion)
#    - Create OccupancyAnalytics records
#    - Generate SuggestionPromocion for idle times
#
# Example skeleton in app/services/analytics_calculator.py:
# ──────────────────────────────────────────────────────────────────────────
#
# def calculate_daily_analytics(db: Session, establishment_id: int, fecha: date):
#     '''Calculate occupancy analytics for a date'''
#
#     # Get all appointments for this date at this establishment
#     appointments = db.query(Appointment).join(Service).filter(
#         Service.establecimiento_id == establishment_id,
#         Appointment.fecha == fecha
#     ).all()
#
#     # Group by hour (09:00-10:00, 10:00-11:00, etc.)
#     for hour in range(9, 18):  # Example: 9am-6pm
#         hora_inicio = time(hour, 0)
#         hora_fin = time(hour + 1, 0)
#
#         # Count appointments in this slot by status
#         confirmadas = len([a for a in appointments if a.hora_inicio >= hora_inicio and a.estado == "CONFIRMADA"])
#         completadas = len([a for a in appointments if a.estado == "COMPLETADA"])
#         canceladas = len([a for a in appointments if a.estado == "CANCELADA"])
#
#         # Calculate rates
#         tasa_ocupacion = (confirmadas / total_capacity) * 100 if total_capacity else 0
#         tasa_no_show = (confirmadas - completadas) / confirmadas * 100 if confirmadas else 0
#
#         # Create record
#         metric = OccupancyAnalyticsCreate(
#             establecimiento_id=establishment_id,
#             fecha=fecha,
#             dia_semana=fecha.strftime("%A").upper(),
#             hora_inicio=hora_inicio,
#             hora_fin=hora_fin,
#             citas_confirmadas=confirmadas,
#             citas_completadas=completadas,
#             tasa_ocupacion=tasa_ocupacion,
#             tasa_no_show=tasa_no_show,
#         )
#         crud_analytics.create_occupancy_metric(db, metric)
#
#         # If idle time, generate suggestion
#         if tasa_ocupacion < 50:
#             sugerencia = SuggestionPromocionCreate(
#                 establecimiento_id=establishment_id,
#                 titulo=f"Horario valle detectado: {hora_inicio}-{hora_fin}",
#                 descripcion="Tu ocupación está baja en esta franja. Considera ofrecer un descuento.",
#                 hora_inicio=hora_inicio,
#                 hora_fin=hora_fin,
#                 tasa_ocupacion=tasa_ocupacion,
#             )
#             crud_analytics.create_suggestion(db, sugerencia)
#
# ──────────────────────────────────────────────────────────────────────────


# ============================================================================
# SUMMARY OF CHANGES
# ============================================================================
#
# ✅ NO MODIFICATIONS to existing code required for core features
# ✅ All new models/endpoints are additive
# ✅ Feature gating is optional - can be gradually introduced
# ✅ Automation hooks are non-blocking (use sync wrappers)
# ✅ Backward compatible - existing API continues to work
#
# OPTIONAL INTEGRATIONS (for future phases):
# 1. Call orchestrator from CRUD on appointment/message changes
# 2. Call analytics calculator from background job
# 3. Add feature gates to existing endpoints (e.g., hide analytics for FREE)
#
# ============================================================================
