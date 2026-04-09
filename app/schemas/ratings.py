from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class ReviewBase(BaseModel):
	establecimiento_id: int
	usuario_id: int
	calificacion: int = Field(..., ge=1, le=5)
	comentario: Optional[str] = None


class ReviewCreate(ReviewBase):
	pass


class ReviewUpdate(BaseModel):
	establecimiento_id: Optional[int] = None
	usuario_id: Optional[int] = None
	calificacion: Optional[int] = Field(None, ge=1, le=5)
	comentario: Optional[str] = None


class ReviewResponse(ReviewBase):
	resena_id: int
	fecha: datetime
	usuario_nombre: Optional[str] = None

	class Config:
		from_attributes = True

