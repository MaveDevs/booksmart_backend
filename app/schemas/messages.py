from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class MessageBase(BaseModel):
	cita_id: int
	emisor_id: int
	contenido: str = Field(..., min_length=1)


class MessageCreate(MessageBase):
	pass


class MessageUpdate(BaseModel):
	cita_id: Optional[int] = None
	emisor_id: Optional[int] = None
	contenido: Optional[str] = Field(None, min_length=1)


class MessageResponse(MessageBase):
	mensaje_id: int
	fecha_envio: datetime

	class Config:
		from_attributes = True

