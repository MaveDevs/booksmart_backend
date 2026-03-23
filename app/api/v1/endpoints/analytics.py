"""
Analytics Endpoints - Owner/Admin dashboard for occupancy metrics and promotion suggestions

Provides:
- Occupancy metrics per time slot
- Idle time detection
- Promotion suggestions
- KPI dashboard
"""

from datetime import date, datetime, timedelta
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_analytics, crud_establishments
from app.models import User
from app.core.permissions import RoleType, get_user_role_name, require_owner_or_admin
from app.schemas.analytics import (
    OccupancyAnalyticsResponse,
    SuggestionPromocionResponse,
    AnalyticsSummaryResponse,
    EstablishmentAnalyticsResponse,
)

router = APIRouter()


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
