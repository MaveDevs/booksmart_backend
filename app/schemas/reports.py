from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field

from app.models.reports import ReportStatus


class ReportBase(BaseModel):
	establecimiento_id: int
	descripcion: str = Field(..., min_length=1)


class ReportCreate(ReportBase):
	estado: ReportStatus = ReportStatus.PENDIENTE


class ReportUpdate(BaseModel):
	establecimiento_id: Optional[int] = None
	descripcion: Optional[str] = Field(None, min_length=1)
	estado: Optional[ReportStatus] = None


class ReportResponse(ReportBase):
	reporte_id: int
	estado: ReportStatus
	fecha_generacion: datetime

	class Config:
		from_attributes = True

