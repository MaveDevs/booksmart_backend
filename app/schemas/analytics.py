"""
Pydantic schemas for Analytics models
"""

from datetime import date, datetime, time
from typing import List, Optional

from pydantic import BaseModel, Field

from app.models.analytics import DayOfWeek


# ── OccupancyAnalytics Schemas ─────────────────────────────────────────────


class OccupancyAnalyticsBase(BaseModel):
    establecimiento_id: int
    fecha: date
    dia_semana: DayOfWeek
    hora_inicio: time
    hora_fin: time
    capacidad_total: int = 0
    citas_confirmadas: int = 0
    citas_completadas: int = 0
    citas_canceladas: int = 0
    citas_pendientes: int = 0
    tasa_ocupacion: float = 0.0
    tasa_no_show: float = 0.0
    tasa_cancelacion: float = 0.0
    ingresos_estimados: float = 0.0


class OccupancyAnalyticsCreate(OccupancyAnalyticsBase):
    pass


class OccupancyAnalyticsUpdate(BaseModel):
    establecimiento_id: Optional[int] = None
    fecha: Optional[date] = None
    dia_semana: Optional[DayOfWeek] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    capacidad_total: Optional[int] = None
    citas_confirmadas: Optional[int] = None
    citas_completadas: Optional[int] = None
    citas_canceladas: Optional[int] = None
    citas_pendientes: Optional[int] = None
    tasa_ocupacion: Optional[float] = None
    tasa_no_show: Optional[float] = None
    tasa_cancelacion: Optional[float] = None
    ingresos_estimados: Optional[float] = None


class OccupancyAnalyticsResponse(OccupancyAnalyticsBase):
    analytics_id: int
    calculado_en: datetime

    class Config:
        from_attributes = True


# ── SuggestionPromocion Schemas ────────────────────────────────────────────


class SuggestionPromocionBase(BaseModel):
    establecimiento_id: int
    titulo: str = Field(..., max_length=200)
    descripcion: str
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    tasa_ocupacion: Optional[float] = None
    descuento_sugerido: float = 20.0
    visto: bool = False
    implementado: bool = False


class SuggestionPromocionCreate(SuggestionPromocionBase):
    pass


class SuggestionPromocionUpdate(BaseModel):
    establecimiento_id: Optional[int] = None
    titulo: Optional[str] = Field(None, max_length=200)
    descripcion: Optional[str] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    tasa_ocupacion: Optional[float] = None
    descuento_sugerido: Optional[float] = None
    visto: Optional[bool] = None
    implementado: Optional[bool] = None


class SuggestionPromocionResponse(SuggestionPromocionBase):
    sugerencia_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


# ── Analytics Summary DTOs ────────────────────────────────────────────────


class AnalyticsSummaryResponse(BaseModel):
    """Summary KPIs for an establishment"""
    establecimiento_id: int
    fecha: date
    
    # Occupancy metrics
    promedio_ocupacion: float
    ocupacion_pico: float
    ocupacion_valle: float
    
    # No-show metrics
    promedio_no_show: float
    tasa_cancelacion: float
    
    # Revenue
    ingresos_totales: float
    
    # Idle times
    slots_valle: int  # Number of slots with low occupancy
    horas_valle_totales: str  # Total idle hours (HH:MM)
    
    # Suggestions
    sugerencias_pendientes: int


class EstablishmentAnalyticsResponse(BaseModel):
    """Full analytics for an establishment with recommendations"""
    establecimiento_id: int
    fecha_analisis: datetime
    
    # Summary
    summary: AnalyticsSummaryResponse
    
    # Detailed metrics
    metricas_por_franja: List[OccupancyAnalyticsResponse]
    
    # Recommendations
    sugerencias: List[SuggestionPromocionResponse]


class AnalyticsSystemOverviewResponse(BaseModel):
    """Global KPI response for admin dashboard."""

    generated_at: datetime
    period_month: str
    total_users: int
    active_users: int
    total_establishments: int
    active_establishments: int
    total_appointments: int
    appointments_this_month: int
    completed_appointments_this_month: int
    cancelled_appointments_this_month: int
    active_subscriptions: int
    revenue_total: float
    revenue_this_month: float
