from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class ProfileBase(BaseModel):
	establecimiento_id: int
	descripcion_publica: Optional[str] = None
	imagen_logo: Optional[str] = None
	imagen_portada: Optional[str] = None


class ProfileCreate(ProfileBase):
	pass


class ProfileUpdate(BaseModel):
	descripcion_publica: Optional[str] = None
	imagen_logo: Optional[str] = None
	imagen_portada: Optional[str] = None


class ProfileResponse(ProfileBase):
	perfil_id: int
	fecha_actualizacion: datetime

	class Config:
		from_attributes = True

