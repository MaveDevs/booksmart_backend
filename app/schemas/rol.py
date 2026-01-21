from typing import Optional

from pydantic import BaseModel


class RoleBase(BaseModel):
	nombre: str
	descripcion: Optional[str] = None


class RoleCreate(RoleBase):
	pass


class RoleResponse(RoleBase):
	rol_id: int

	class Config:
		from_attributes = True

