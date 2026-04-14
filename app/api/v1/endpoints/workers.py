from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_workers, crud_establishments
from app.models import User
from app.schemas.workers import WorkerCreate, WorkerUpdate, WorkerResponse
from app.core.permissions import (
	require_owner_or_admin,
	validate_establishment_access,
	RoleType,
)

router = APIRouter()


@router.get("/", response_model=List[WorkerResponse])
def get_workers(
	establishment_id: int = Query(None),
	skip: int = 0,
	limit: int = 100,
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(deps.get_current_user),
):
	"""Any authenticated user can list workers (read-only)."""
	if establishment_id:
		return crud_workers.get_workers_by_establishment(db, establishment_id=establishment_id, skip=skip, limit=limit)
	return crud_workers.get_workers(db, skip=skip, limit=limit)


@router.get("/{worker_id}", response_model=WorkerResponse)
def get_worker(
	worker_id: int,
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(deps.get_current_user),
):
	"""Any authenticated user can view a worker (read-only)."""
	worker = crud_workers.get_worker(db, worker_id)
	if not worker:
		raise HTTPException(status_code=404, detail="Worker not found")
	return worker


@router.get("/me", response_model=WorkerResponse)
def get_my_worker_profile(
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(deps.get_current_user),
):
	"""Get worker profile linked to the authenticated user."""
	worker = crud_workers.get_worker_by_user(db, current_user.usuario_id)
	if not worker:
		raise HTTPException(status_code=404, detail="Worker profile not found for current user")
	return worker


@router.post("/", response_model=WorkerResponse)
def create_worker(
	worker: WorkerCreate,
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(require_owner_or_admin()),
):
	"""Only owners and admins can create workers. Owners can only create workers for their own establishments."""
	# Verify establishment exists and user has access
	establishment = crud_establishments.get_establishment(db, worker.establecimiento_id)
	if not establishment:
		raise HTTPException(status_code=404, detail="Establishment not found")
	
	# Owners can only create workers for their own establishments
	validate_establishment_access(current_user, establishment)
	
	try:
		return crud_workers.create_worker(db, worker)
	except ValueError as e:
		raise HTTPException(status_code=400, detail=str(e))


@router.put("/{worker_id}", response_model=WorkerResponse)
def update_worker(
	worker_id: int,
	worker: WorkerUpdate,
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(require_owner_or_admin()),
):
	"""Only owners and admins can update workers. Owners can only update workers for their own establishments."""
	db_worker = crud_workers.get_worker(db, worker_id)
	if not db_worker:
		raise HTTPException(status_code=404, detail="Worker not found")
	
	# Verify user has access to the establishment this worker belongs to
	establishment = crud_establishments.get_establishment(db, db_worker.establecimiento_id)
	if establishment:
		validate_establishment_access(current_user, establishment)
	
	db_worker = crud_workers.update_worker(db, worker_id, worker)
	return db_worker


@router.patch("/{worker_id}", response_model=WorkerResponse)
def patch_worker(
	worker_id: int,
	worker: WorkerUpdate,
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(require_owner_or_admin()),
):
	"""Only owners and admins can patch workers. Owners can only patch workers for their own establishments."""
	db_worker = crud_workers.get_worker(db, worker_id)
	if not db_worker:
		raise HTTPException(status_code=404, detail="Worker not found")
	
	# Verify user has access to the establishment this worker belongs to
	establishment = crud_establishments.get_establishment(db, db_worker.establecimiento_id)
	if establishment:
		validate_establishment_access(current_user, establishment)
	
	db_worker = crud_workers.update_worker(db, worker_id, worker)
	return db_worker


@router.delete("/{worker_id}")
def delete_worker(
	worker_id: int,
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(require_owner_or_admin()),
):
	"""Only owners and admins can delete workers. Owners can only delete workers for their own establishments."""
	db_worker = crud_workers.get_worker(db, worker_id)
	if not db_worker:
		raise HTTPException(status_code=404, detail="Worker not found")
	
	# Verify user has access to the establishment this worker belongs to
	establishment = crud_establishments.get_establishment(db, db_worker.establecimiento_id)
	if establishment:
		validate_establishment_access(current_user, establishment)
	
	success = crud_workers.delete_worker(db, worker_id)
	if success:
		return {"detail": "Worker deleted successfully"}
	raise HTTPException(status_code=500, detail="Error deleting worker")


@router.post("/{worker_id}/services")
def set_worker_services(
	worker_id: int,
	service_ids: List[int],
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(require_owner_or_admin()),
):
	"""Sets the list of services a worker can perform."""
	db_worker = crud_workers.get_worker(db, worker_id)
	if not db_worker:
		raise HTTPException(status_code=404, detail="Worker not found")
	
	establishment = crud_establishments.get_establishment(db, db_worker.establecimiento_id)
	if establishment:
		validate_establishment_access(current_user, establishment)
		
	updated_worker = crud_workers.set_worker_services(db, worker_id, service_ids)
	return {"message": "Servicios actualizados correctamente"}


@router.get("/{worker_id}/services")
def get_worker_services(
	worker_id: int,
	db: Session = Depends(deps.get_db),
	current_user: User = Depends(deps.get_current_user),
):
	"""Gets the list of services assigned to a worker."""
	services = crud_workers.get_worker_services(db, worker_id)
	return services
