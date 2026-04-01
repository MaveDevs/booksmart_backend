"""
Analytics Endpoints - Owner/Admin dashboard for occupancy metrics and promotion suggestions

Provides:
- Occupancy metrics per time slot
- Idle time detection
- Promotion suggestions
- KPI dashboard
"""

from datetime import date, datetime, time, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_analytics, crud_establishments
from app.models import Appointment, Establishment, Payment, Subscription, User
from app.models.appointments import AppointmentStatus
from app.models.payments import PaymentStatus
from app.models.plan_features import FeatureKey
from app.core.feature_gating import establishment_has_feature
from app.core.permissions import RoleType, get_user_role_name, require_admin, require_owner_or_admin
from app.services.analytics_calculator import recalculate_daily_occupancy
from app.schemas.analytics import (
    AnalyticsSystemOverviewResponse,
    OccupancyAnalyticsResponse,
    SuggestionPromocionResponse,
    AnalyticsSummaryResponse,
    EstablishmentAnalyticsResponse,
)

router = APIRouter()


def _assert_feature_for_owner(
    db: Session,
    current_user: User,
    establecimiento_id: int,
    feature_key: FeatureKey,
) -> None:
    """Require feature access for owners while allowing admins to bypass gates."""
    user_role = get_user_role_name(current_user)
    if user_role == RoleType.ADMIN.value:
        return

    if not establishment_has_feature(db, establecimiento_id, feature_key):
        raise HTTPException(
            status_code=403,
            detail=f"Feature {feature_key.value} requires an upgraded plan",
        )


@router.get("/system-overview", response_model=AnalyticsSystemOverviewResponse)
def get_system_overview(
    db: Session = Depends(deps.get_db),
    _: User = Depends(require_admin()),
):
    """Global platform metrics for the admin dashboard."""
    today = date.today()
    month_start = today.replace(day=1)

    if month_start.month == 12:
        next_month_start = date(month_start.year + 1, 1, 1)
    else:
        next_month_start = date(month_start.year, month_start.month + 1, 1)

    month_start_dt = datetime.combine(month_start, time.min)
    next_month_start_dt = datetime.combine(next_month_start, time.min)

    total_users = db.query(func.count(User.usuario_id)).scalar() or 0
    active_users = db.query(func.count(User.usuario_id)).filter(User.activo.is_(True)).scalar() or 0

    total_establishments = db.query(func.count(Establishment.establecimiento_id)).scalar() or 0
    active_establishments = (
        db.query(func.count(Establishment.establecimiento_id))
        .filter(Establishment.activo.is_(True))
        .scalar()
        or 0
    )

    total_appointments = db.query(func.count(Appointment.cita_id)).scalar() or 0
    appointments_this_month = (
        db.query(func.count(Appointment.cita_id))
        .filter(Appointment.fecha >= month_start, Appointment.fecha < next_month_start)
        .scalar()
        or 0
    )
    completed_appointments_this_month = (
        db.query(func.count(Appointment.cita_id))
        .filter(
            Appointment.fecha >= month_start,
            Appointment.fecha < next_month_start,
            Appointment.estado == AppointmentStatus.COMPLETADA,
        )
        .scalar()
        or 0
    )
    cancelled_appointments_this_month = (
        db.query(func.count(Appointment.cita_id))
        .filter(
            Appointment.fecha >= month_start,
            Appointment.fecha < next_month_start,
            Appointment.estado == AppointmentStatus.CANCELADA,
        )
        .scalar()
        or 0
    )

    active_subscriptions = (
        db.query(func.count(Subscription.suscripcion_id))
        .filter(Subscription.estado == "ACTIVA")
        .scalar()
        or 0
    )

    revenue_total = (
        db.query(func.coalesce(func.sum(Payment.monto), 0))
        .filter(Payment.estado == PaymentStatus.COMPLETADO)
        .scalar()
    )
    revenue_this_month = (
        db.query(func.coalesce(func.sum(Payment.monto), 0))
        .filter(
            Payment.estado == PaymentStatus.COMPLETADO,
            Payment.fecha_pago >= month_start_dt,
            Payment.fecha_pago < next_month_start_dt,
        )
        .scalar()
    )

    return AnalyticsSystemOverviewResponse(
        generated_at=datetime.utcnow(),
        period_month=month_start.strftime("%Y-%m"),
        total_users=int(total_users),
        active_users=int(active_users),
        total_establishments=int(total_establishments),
        active_establishments=int(active_establishments),
        total_appointments=int(total_appointments),
        appointments_this_month=int(appointments_this_month),
        completed_appointments_this_month=int(completed_appointments_this_month),
        cancelled_appointments_this_month=int(cancelled_appointments_this_month),
        active_subscriptions=int(active_subscriptions),
        revenue_total=float(revenue_total or 0),
        revenue_this_month=float(revenue_this_month or 0),
    )


@router.post("/occupancy/recalculate/{establecimiento_id}")
def recalculate_occupancy_metrics(
    establecimiento_id: int,
    fecha: Optional[date] = Query(None),
    idle_threshold_percent: float = Query(50.0),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    Recalculate occupancy analytics for one day.
    - Owners can recalculate only their own establishments
    - Admins can recalculate all
    """
    user_role = get_user_role_name(current_user)

    establishment = crud_establishments.get_establishment(db, establecimiento_id)
    if not establishment:
        raise HTTPException(status_code=404, detail="Establishment not found")

    if user_role == RoleType.DUENO.value and establishment.usuario_id != current_user.usuario_id:
        raise HTTPException(status_code=403, detail="You don't own this establishment")

    _assert_feature_for_owner(
        db,
        current_user,
        establecimiento_id,
        FeatureKey.ANALYTICS_OCUPACION,
    )

    if not fecha:
        fecha = date.today()

    result = recalculate_daily_occupancy(
        db,
        establecimiento_id=establecimiento_id,
        target_date=fecha,
        idle_threshold_percent=idle_threshold_percent,
    )

    return {
        "establecimiento_id": establecimiento_id,
        "fecha": fecha,
        "idle_threshold_percent": idle_threshold_percent,
        **result,
    }


# ── Occupancy Metrics ────────────────────────────────────────────────────────


@router.get("/occupancy/", response_model=List[OccupancyAnalyticsResponse])
def get_occupancy_metrics(
    establecimiento_id: int = Query(...),
    fecha: Optional[date] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    Get occupancy metrics for an establishment.
    - Owners can only see their own establishments
    - Admins can see all
    """
    user_role = get_user_role_name(current_user)

    # Check access
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")

    # If no fecha provided, use today
    if not fecha:
        fecha = date.today()

    _assert_feature_for_owner(
        db,
        current_user,
        establecimiento_id,
        FeatureKey.ANALYTICS_OCUPACION,
    )

    return crud_analytics.get_occupancy_metrics(
        db, skip=skip, limit=limit, establecimiento_id=establecimiento_id, fecha=fecha
    )


@router.get("/occupancy/idle-times", response_model=List[OccupancyAnalyticsResponse])
def get_idle_time_slots(
    establecimiento_id: int = Query(...),
    fecha: Optional[date] = Query(None),
    threshold_percent: float = Query(50.0, description="Occupancy % below which is considered idle"),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    Get idle time slots (low occupancy periods) for an establishment.
    Useful for identifying when to run promotions.
    """
    user_role = get_user_role_name(current_user)

    # Check access
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")

    if not fecha:
        fecha = date.today()

    _assert_feature_for_owner(
        db,
        current_user,
        establecimiento_id,
        FeatureKey.ANALYTICS_OCUPACION,
    )

    return crud_analytics.get_idle_time_slots(
        db, establecimiento_id, fecha, threshold_percent
    )


# ── Promotion Suggestions ─────────────────────────────────────────────────────


@router.get("/suggestions/", response_model=List[SuggestionPromocionResponse])
def get_promotion_suggestions(
    establecimiento_id: int = Query(...),
    visto: Optional[bool] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    Get promotion suggestions for an establishment.
    - Owners can only see their own establishments
    - Admins can see all
    """
    user_role = get_user_role_name(current_user)

    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")

    _assert_feature_for_owner(
        db,
        current_user,
        establecimiento_id,
        FeatureKey.SUGERIR_PROMOS,
    )

    return crud_analytics.get_suggestions(
        db, skip=skip, limit=limit, establecimiento_id=establecimiento_id, visto=visto
    )


@router.get("/suggestions/unread")
def get_unread_suggestions(
    establecimiento_id: int = Query(...),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Get unread promotion suggestions for an establishment"""
    user_role = get_user_role_name(current_user)

    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")

    _assert_feature_for_owner(
        db,
        current_user,
        establecimiento_id,
        FeatureKey.SUGERIR_PROMOS,
    )

    suggestions = crud_analytics.get_unread_suggestions(db, establecimiento_id)
    return [SuggestionPromocionResponse.from_orm(s) for s in suggestions]


@router.put("/suggestions/{sugerencia_id}/mark-read")
def mark_suggestion_as_read(
    sugerencia_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Mark a suggestion as read by owner"""
    suggestion = crud_analytics.mark_suggestion_as_read(db, sugerencia_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    # Verify access
    user_role = get_user_role_name(current_user)
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, suggestion.establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")

    return SuggestionPromocionResponse.from_orm(suggestion)


@router.put("/suggestions/{sugerencia_id}/mark-implemented")
def mark_suggestion_as_implemented(
    sugerencia_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """Mark a suggestion as implemented"""
    suggestion = crud_analytics.mark_suggestion_as_implemented(db, sugerencia_id)
    if not suggestion:
        raise HTTPException(status_code=404, detail="Suggestion not found")

    # Verify access
    user_role = get_user_role_name(current_user)
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, suggestion.establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")

    return SuggestionPromocionResponse.from_orm(suggestion)


# ── Dashboard Summary ────────────────────────────────────────────────────────


@router.get("/dashboard/{establecimiento_id}", response_model=EstablishmentAnalyticsResponse)
def get_analytics_dashboard(
    establecimiento_id: int,
    fecha: Optional[date] = Query(None),
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(require_owner_or_admin()),
):
    """
    Get comprehensive analytics dashboard for an establishment.
    Includes occupancy metrics, idle times, and promotion suggestions.
    """
    user_role = get_user_role_name(current_user)

    # Check access
    if user_role == RoleType.DUENO.value:
        establishment = crud_establishments.get_establishment(db, establecimiento_id)
        if not establishment or establishment.usuario_id != current_user.usuario_id:
            raise HTTPException(status_code=403, detail="You don't own this establishment")

    if not fecha:
        fecha = date.today()

    _assert_feature_for_owner(
        db,
        current_user,
        establecimiento_id,
        FeatureKey.ANALYTICS_OCUPACION,
    )

    # Get all metrics for the day
    metricas = crud_analytics.get_occupancy_metrics_by_establishment_and_date(
        db, establecimiento_id, fecha
    )

    # Calculate summary
    if metricas:
        promedio_ocupacion = sum(m.tasa_ocupacion for m in metricas) / len(metricas)
        ocupacion_pico = max(m.tasa_ocupacion for m in metricas)
        ocupacion_valle = min(m.tasa_ocupacion for m in metricas)
        promedio_no_show = sum(m.tasa_no_show for m in metricas) / len(metricas)
        tasa_cancelacion = sum(m.tasa_cancelacion for m in metricas) / len(metricas)
        ingresos_totales = sum(m.ingresos_estimados for m in metricas)
        
        # Count idle slots (< 50% occupancy)
        slots_valle = len([m for m in metricas if m.tasa_ocupacion < 50])
        horas_valle_totales = f"{slots_valle}:00"  # Simplified (assume 1h per slot)
    else:
        promedio_ocupacion = 0.0
        ocupacion_pico = 0.0
        ocupacion_valle = 0.0
        promedio_no_show = 0.0
        tasa_cancelacion = 0.0
        ingresos_totales = 0.0
        slots_valle = 0
        horas_valle_totales = "0:00"

    # Get suggestions
    sugerencias = crud_analytics.get_suggestions(db, establecimiento_id=establecimiento_id)

    summary = AnalyticsSummaryResponse(
        establecimiento_id=establecimiento_id,
        fecha=fecha,
        promedio_ocupacion=promedio_ocupacion,
        ocupacion_pico=ocupacion_pico,
        ocupacion_valle=ocupacion_valle,
        promedio_no_show=promedio_no_show,
        tasa_cancelacion=tasa_cancelacion,
        ingresos_totales=ingresos_totales,
        slots_valle=slots_valle,
        horas_valle_totales=horas_valle_totales,
        sugerencias_pendientes=len([s for s in sugerencias if not s.visto]),
    )

    return EstablishmentAnalyticsResponse(
        establecimiento_id=establecimiento_id,
        fecha_analisis=datetime.utcnow(),
        summary=summary,
        metricas_por_franja=[OccupancyAnalyticsResponse.from_orm(m) for m in metricas],
        sugerencias=[SuggestionPromocionResponse.from_orm(s) for s in sugerencias],
    )
