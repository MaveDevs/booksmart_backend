from datetime import datetime

from pydantic import BaseModel


class MessageBase(BaseModel):
	cita_id: int
	emisor_id: int
	contenido: str


class MessageCreate(MessageBase):
	pass


class MessageResponse(MessageBase):
	mensaje_id: int
	fecha_envio: datetime

	class Config:
		from_attributes = True

