from typing import Optional

from pydantic import BaseModel, Field


class RoleBase(BaseModel):
	nombre: str = Field(..., min_length=1, max_length=50)
	descripcion: Optional[str] = None


class RoleCreate(RoleBase):
	pass


class RoleUpdate(BaseModel):
	nombre: Optional[str] = Field(None, min_length=1, max_length=50)
	descripcion: Optional[str] = None


class RoleResponse(RoleBase):
	rol_id: int

	class Config:
		from_attributes = True

