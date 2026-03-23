"""
CRUD operations for Analytics (Occupancy metrics and promotion suggestions)
"""

from datetime import date, datetime
from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import OccupancyAnalytics, SuggestionPromocion
from app.schemas.analytics import (
    OccupancyAnalyticsCreate,
    OccupancyAnalyticsUpdate,
    SuggestionPromocionCreate,
    SuggestionPromocionUpdate,
)


# ── OccupancyAnalytics CRUD ──────────────────────────────────────────────────


def get_occupancy_metric(db: Session, analytics_id: int) -> Optional[OccupancyAnalytics]:
    """Get a specific occupancy metric"""
    return db.query(OccupancyAnalytics).filter(OccupancyAnalytics.analytics_id == analytics_id).first()


def get_occupancy_metrics(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
    fecha: Optional[date] = None,
) -> List[OccupancyAnalytics]:
    """Get occupancy metrics with optional filters"""
    query = db.query(OccupancyAnalytics)
    
    if establecimiento_id is not None:
        query = query.filter(OccupancyAnalytics.establecimiento_id == establecimiento_id)
    if fecha is not None:
        query = query.filter(OccupancyAnalytics.fecha == fecha)
    
    return query.offset(skip).limit(limit).all()


def get_occupancy_metrics_by_establishment_and_date(
    db: Session, establecimiento_id: int, fecha: date
) -> List[OccupancyAnalytics]:
    """Get all occupancy metrics for an establishment on a specific date"""
    return (
        db.query(OccupancyAnalytics)
        .filter(
            OccupancyAnalytics.establecimiento_id == establecimiento_id,
            OccupancyAnalytics.fecha == fecha,
        )
        .order_by(OccupancyAnalytics.hora_inicio)
        .all()
    )


def get_idle_time_slots(
    db: Session, establecimiento_id: int, fecha: date, threshold_percent: float = 50.0
) -> List[OccupancyAnalytics]:
    """
    Get time slots with low occupancy (idle times).
    
    Args:
        threshold_percent: Occupancy rate below which a slot is considered idle (default 50%)
    """
    return (
        db.query(OccupancyAnalytics)
        .filter(
            OccupancyAnalytics.establecimiento_id == establecimiento_id,
            OccupancyAnalytics.fecha == fecha,
            OccupancyAnalytics.tasa_ocupacion < threshold_percent,
        )
        .order_by(OccupancyAnalytics.hora_inicio)
        .all()
    )


def create_occupancy_metric(
    db: Session, metric: OccupancyAnalyticsCreate
) -> OccupancyAnalytics:
    """Create a new occupancy metric"""
    metric_data = metric.model_dump()
    db_metric = OccupancyAnalytics(**metric_data)  # type: ignore[arg-type]
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric


def update_occupancy_metric(
    db: Session,
    analytics_id: int,
    metric: OccupancyAnalyticsUpdate,
) -> Optional[OccupancyAnalytics]:
    """Update an occupancy metric"""
    db_metric = get_occupancy_metric(db, analytics_id)
    if not db_metric:
        return None

    update_data = metric.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_metric, field, value)

    db.commit()
    db.refresh(db_metric)
    return db_metric


def delete_occupancy_metric(db: Session, analytics_id: int) -> bool:
    """Delete an occupancy metric"""
    db_metric = get_occupancy_metric(db, analytics_id)
    if not db_metric:
        return False

    db.delete(db_metric)
    db.commit()
    return True


# ── SuggestionPromocion CRUD ───────────────────────────────────────────────


def get_suggestion(db: Session, sugerencia_id: int) -> Optional[SuggestionPromocion]:
    """Get a specific promotion suggestion"""
    return db.query(SuggestionPromocion).filter(SuggestionPromocion.sugerencia_id == sugerencia_id).first()


def get_suggestions(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
    visto: Optional[bool] = None,
) -> List[SuggestionPromocion]:
    """Get promotion suggestions with optional filters"""
    query = db.query(SuggestionPromocion)
    
    if establecimiento_id is not None:
        query = query.filter(SuggestionPromocion.establecimiento_id == establecimiento_id)
    if visto is not None:
        query = query.filter(SuggestionPromocion.visto == visto)
    
    return query.offset(skip).limit(limit).all()


def get_unread_suggestions(
    db: Session, establecimiento_id: int, limit: int = 50
) -> List[SuggestionPromocion]:
    """Get unread suggestions for an establishment"""
    return (
        db.query(SuggestionPromocion)
        .filter(
            SuggestionPromocion.establecimiento_id == establecimiento_id,
            SuggestionPromocion.visto == False,
        )
        .limit(limit)
        .all()
    )


def create_suggestion(
    db: Session, suggestion: SuggestionPromocionCreate
) -> SuggestionPromocion:
    """Create a new promotion suggestion"""
    suggestion_data = suggestion.model_dump()
    db_suggestion = SuggestionPromocion(**suggestion_data)  # type: ignore[arg-type]
    db.add(db_suggestion)
    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


def update_suggestion(
    db: Session,
    sugerencia_id: int,
    suggestion: SuggestionPromocionUpdate,
) -> Optional[SuggestionPromocion]:
    """Update a suggestion"""
    db_suggestion = get_suggestion(db, sugerencia_id)
    if not db_suggestion:
        return None

    update_data = suggestion.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_suggestion, field, value)

    db.commit()
    db.refresh(db_suggestion)
    return db_suggestion


def mark_suggestion_as_read(db: Session, sugerencia_id: int) -> Optional[SuggestionPromocion]:
    """Mark suggestion as read by owner"""
    return update_suggestion(
        db, sugerencia_id, SuggestionPromocionUpdate(visto=True)
    )


def mark_suggestion_as_implemented(db: Session, sugerencia_id: int) -> Optional[SuggestionPromocion]:
    """Mark suggestion as implemented"""
    return update_suggestion(
        db, sugerencia_id, SuggestionPromocionUpdate(implementado=True)
    )


def delete_suggestion(db: Session, sugerencia_id: int) -> bool:
    """Delete a suggestion"""
    db_suggestion = get_suggestion(db, sugerencia_id)
    if not db_suggestion:
        return False

    db.delete(db_suggestion)
    db.commit()
    return True
