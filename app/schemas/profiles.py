from typing import Optional

from pydantic import BaseModel, Field


class ProfileBase(BaseModel):
	establecimiento_id: int
	descripcion_publica: Optional[str] = None
	imagen_logo: Optional[str] = Field(None, max_length=255)
	imagen_portada: Optional[str] = Field(None, max_length=255)


class ProfileCreate(ProfileBase):
	pass


class ProfileUpdate(BaseModel):
	descripcion_publica: Optional[str] = None
	imagen_logo: Optional[str] = Field(None, max_length=255)
	imagen_portada: Optional[str] = Field(None, max_length=255)


class ProfileResponse(ProfileBase):
	perfil_id: int

	class Config:
		from_attributes = True

