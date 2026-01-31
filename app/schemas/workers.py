from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, EmailStr


class WorkerBase(BaseModel):
    establecimiento_id: int
    nombre: str
    apellido: str
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    foto_perfil: Optional[str] = None
    especialidad: Optional[str] = None
    descripcion: Optional[str] = None
    activo: bool = True
    fecha_contratacion: Optional[date] = None


class WorkerCreate(WorkerBase):
    pass


class WorkerUpdate(BaseModel):
    nombre: Optional[str] = None
    apellido: Optional[str] = None
    email: Optional[EmailStr] = None
    telefono: Optional[str] = None
    foto_perfil: Optional[str] = None
    especialidad: Optional[str] = None
    descripcion: Optional[str] = None
    activo: Optional[bool] = None
    fecha_contratacion: Optional[date] = None


class WorkerResponse(WorkerBase):
    trabajador_id: int
    fecha_creacion: datetime

    class Config:
        from_attributes = True


class WorkerServiceBase(BaseModel):
    trabajador_id: int
    servicio_id: int


class WorkerServiceCreate(WorkerServiceBase):
    pass


class WorkerServiceResponse(WorkerServiceBase):
    trabajador_servicio_id: int

    class Config:
        from_attributes = True


class ScheduleBlockBase(BaseModel):
    trabajador_id: int
    fecha_inicio: datetime
    fecha_fin: datetime
    motivo: Optional[str] = None


class ScheduleBlockCreate(ScheduleBlockBase):
    pass


class ScheduleBlockUpdate(BaseModel):
    trabajador_id: Optional[int] = None
    fecha_inicio: Optional[datetime] = None
    fecha_fin: Optional[datetime] = None
    motivo: Optional[str] = None


class ScheduleBlockResponse(ScheduleBlockBase):
    bloqueo_id: int

    class Config:
        from_attributes = True
