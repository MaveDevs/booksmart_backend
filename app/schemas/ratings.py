from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
	trabajador_id: int
	cita_id: Optional[int] = None
	usuario_id: int
	calificacion: Optional[int] = Field(None, ge=1, le=5)
	comentario: Optional[str] = None


class ReviewCreate(ReviewBase):
	pass


class ReviewResponse(ReviewBase):
	resena_id: int
	fecha_creacion: datetime

	class Config:
		from_attributes = True

