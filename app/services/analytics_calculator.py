from datetime import date, datetime, time, timedelta
from decimal import Decimal
from typing import Dict, List

from sqlalchemy.orm import Session

from app.crud import crud_analytics
from app.models import Agenda, Appointment, OccupancyAnalytics, Service, SuggestionPromocion, Worker
from app.models.analytics import DayOfWeek
from app.schemas.analytics import OccupancyAnalyticsCreate, SuggestionPromocionCreate

_WEEKDAY_MAP = {
    0: DayOfWeek.LUNES,
    1: DayOfWeek.MARTES,
    2: DayOfWeek.MIERCOLES,
    3: DayOfWeek.JUEVES,
    4: DayOfWeek.VIERNES,
    5: DayOfWeek.SABADO,
    6: DayOfWeek.DOMINGO,
}


def _get_day_enum(target_date: date) -> DayOfWeek:
    return _WEEKDAY_MAP[target_date.weekday()]


def _status_value(value) -> str:
    return value.value if hasattr(value, "value") else str(value)


def _slot_times(start_time: time, end_time: time) -> List[tuple[time, time]]:
    slots: List[tuple[time, time]] = []
    cursor = datetime.combine(date.today(), start_time)
    end_dt = datetime.combine(date.today(), end_time)

    while cursor < end_dt:
        next_cursor = min(cursor + timedelta(hours=1), end_dt)
        slots.append((cursor.time(), next_cursor.time()))
        cursor = next_cursor

    return slots


def recalculate_daily_occupancy(
    db: Session,
    establecimiento_id: int,
    target_date: date,
    idle_threshold_percent: float = 50.0,
) -> Dict[str, int]:
    """
    Recalculate occupancy analytics for one establishment and one date.

    - Clears existing occupancy metrics for that day
    - Builds hourly slots from agenda for weekday
    - Computes occupancy/no-show/cancellation/revenue per slot
    - Generates promotion suggestions for idle slots
    """
    day_enum = _get_day_enum(target_date)

    agendas = (
        db.query(Agenda)
        .filter(
            Agenda.establecimiento_id == establecimiento_id,
            Agenda.dia_semana == day_enum,
        )
        .all()
    )

    if not agendas:
        return {
            "slots_processed": 0,
            "metrics_created": 0,
            "suggestions_created": 0,
        }

    worker_capacity = (
        db.query(Worker)
        .filter(
            Worker.establecimiento_id == establecimiento_id,
            Worker.activo == True,
        )
        .count()
    )
    worker_capacity = max(worker_capacity, 1)

    appointments = (
        db.query(Appointment)
        .join(Service, Appointment.servicio_id == Service.servicio_id)
        .filter(
            Service.establecimiento_id == establecimiento_id,
            Appointment.fecha == target_date,
        )
        .all()
    )

    db.query(OccupancyAnalytics).filter(
        OccupancyAnalytics.establecimiento_id == establecimiento_id,
        OccupancyAnalytics.fecha == target_date,
    ).delete(synchronize_session=False)

    suggestion_prefix = f"[AUTO][{target_date.isoformat()}]"
    db.query(SuggestionPromocion).filter(
        SuggestionPromocion.establecimiento_id == establecimiento_id,
        SuggestionPromocion.titulo.like(f"{suggestion_prefix}%"),
    ).delete(synchronize_session=False)
    db.commit()

    slots_processed = 0
    metrics_created = 0
    suggestions_created = 0

    for agenda in agendas:
        for hora_inicio, hora_fin in _slot_times(agenda.hora_inicio, agenda.hora_fin):
            slots_processed += 1

            slot_appointments = [
                appt
                for appt in appointments
                if appt.hora_inicio < hora_fin and appt.hora_fin > hora_inicio
            ]

            total_slot = len(slot_appointments)
            confirmadas = sum(1 for a in slot_appointments if _status_value(a.estado) == "CONFIRMADA")
            completadas = sum(1 for a in slot_appointments if _status_value(a.estado) == "COMPLETADA")
            canceladas = sum(1 for a in slot_appointments if _status_value(a.estado) == "CANCELADA")
            pendientes = sum(1 for a in slot_appointments if _status_value(a.estado) == "PENDIENTE")

            capacidad_total = worker_capacity
            ocupadas = confirmadas + completadas + pendientes
            tasa_ocupacion = min((ocupadas / capacidad_total) * 100.0, 100.0) if capacidad_total else 0.0
            tasa_no_show = ((confirmadas - completadas) / confirmadas) * 100.0 if confirmadas > 0 else 0.0
            tasa_cancelacion = (canceladas / total_slot) * 100.0 if total_slot > 0 else 0.0

            ingresos_estimados = float(
                sum(
                    Decimal(str(a.service.precio))
                    for a in slot_appointments
                    if _status_value(a.estado) in {"CONFIRMADA", "COMPLETADA"}
                )
            )

            metric = OccupancyAnalyticsCreate(
                establecimiento_id=establecimiento_id,
                fecha=target_date,
                dia_semana=day_enum,
                hora_inicio=hora_inicio,
                hora_fin=hora_fin,
                capacidad_total=capacidad_total,
                citas_confirmadas=confirmadas,
                citas_completadas=completadas,
                citas_canceladas=canceladas,
                citas_pendientes=pendientes,
                tasa_ocupacion=round(tasa_ocupacion, 2),
                tasa_no_show=round(tasa_no_show, 2),
                tasa_cancelacion=round(tasa_cancelacion, 2),
                ingresos_estimados=round(ingresos_estimados, 2),
            )
            crud_analytics.create_occupancy_metric(db, metric)
            metrics_created += 1

            if tasa_ocupacion < idle_threshold_percent:
                if tasa_ocupacion < 20.0:
                    descuento_sugerido = 30.0
                elif tasa_ocupacion < 35.0:
                    descuento_sugerido = 20.0
                else:
                    descuento_sugerido = 10.0

                suggestion = SuggestionPromocionCreate(
                    establecimiento_id=establecimiento_id,
                    titulo=f"{suggestion_prefix} Horario valle {hora_inicio.strftime('%H:%M')}-{hora_fin.strftime('%H:%M')}",
                    descripcion=(
                        "Se detectó baja ocupación en esta franja. "
                        "Considera una promo limitada para aumentar reservas."
                    ),
                    hora_inicio=hora_inicio,
                    hora_fin=hora_fin,
                    tasa_ocupacion=round(tasa_ocupacion, 2),
                    descuento_sugerido=descuento_sugerido,
                    visto=False,
                    implementado=False,
                )
                crud_analytics.create_suggestion(db, suggestion)
                suggestions_created += 1

    return {
        "slots_processed": slots_processed,
        "metrics_created": metrics_created,
        "suggestions_created": suggestions_created,
    }
