from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReportBase(BaseModel):
	establecimiento_id: int
	descripcion: str = Field(..., min_length=1)


class ReportCreate(ReportBase):
	pass


class ReportUpdate(BaseModel):
	establecimiento_id: Optional[int] = None
	descripcion: Optional[str] = Field(None, min_length=1)


class ReportResponse(ReportBase):
	reporte_id: int
	fecha_generacion: datetime

	class Config:
		from_attributes = True

