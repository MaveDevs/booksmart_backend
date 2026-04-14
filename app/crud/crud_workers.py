from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Worker, User, Service
from app.schemas.workers import WorkerCreate, WorkerUpdate
from app.crud.crud_users import get_user_by_email
from app.core.security import get_password_hash


def get_worker(db: Session, worker_id: int) -> Optional[Worker]:
	return db.query(Worker).filter(Worker.trabajador_id == worker_id).first()


def get_workers(db: Session, skip: int = 0, limit: int = 100) -> List[Worker]:
	return db.query(Worker).offset(skip).limit(limit).all()


def get_worker_by_user(db: Session, user_id: int) -> Optional[Worker]:
	return db.query(Worker).filter(Worker.usuario_id == user_id).first()


def get_workers_by_establishment(
	db: Session, establishment_id: int, skip: int = 0, limit: int = 100
) -> List[Worker]:
	return (
		db.query(Worker)
		.filter(Worker.establecimiento_id == establishment_id)
		.offset(skip)
		.limit(limit)
		.all()
	)


def create_worker(db: Session, worker: WorkerCreate) -> Worker:
	# Verify establecimiento_id exists
	establishment = (
		db.query(Establishment)
		.filter(Establishment.establecimiento_id == worker.establecimiento_id)
		.first()
	)
	if not establishment:
		raise ValueError(f"Establishment with id {worker.establecimiento_id} does not exist")
	
	usuario_id = None
	if worker.email:
		worker.email = worker.email.strip().lower()
		existing_user = get_user_by_email(db, worker.email)
		
		if existing_user:
			# If user exists, we just link them
			usuario_id = existing_user.usuario_id
		else:
			# If not, create a new user account
			# Determine password
			raw_password = worker.contrasena.strip() if (worker.contrasena and worker.contrasena.strip()) else "WorkerTemp123!"
			
			new_user = User(
				nombre=worker.nombre,
				apellido=worker.apellido,
				correo=worker.email,
				contrasena_hash=get_password_hash(raw_password),
				rol_id=4,
				activo=True,
			)
			db.add(new_user)
			db.flush()
			usuario_id = new_user.usuario_id

	db_worker = Worker(**worker.model_dump())
	if usuario_id:
		db_worker.usuario_id = usuario_id
		
	db.add(db_worker)
	db.commit()
	db.refresh(db_worker)
	return db_worker


def update_worker(db: Session, worker_id: int, worker: WorkerUpdate) -> Optional[Worker]:
	db_worker = get_worker(db, worker_id)
	if not db_worker:
		return None
	
	update_data = worker.model_dump(exclude_unset=True)
	
	# If email is being updated, also update the linked user
	if "email" in update_data and update_data["email"] != db_worker.email:
		update_data["email"] = update_data["email"].strip().lower()
		new_email = update_data["email"]
		# Check if new email already exists in system for another user
		from app.crud.crud_users import get_user_by_email
		existing_user = get_user_by_email(db, new_email)
		if existing_user and (not db_worker.usuario_id or existing_user.usuario_id != db_worker.usuario_id):
			raise ValueError("Este correo ya está en uso por otro usuario.")
		
		# Update the linked user if it exists
		if db_worker.usuario_id:
			from app.models import User
			db_user = db.query(User).filter(User.usuario_id == db_worker.usuario_id).first()
			if db_user:
				db_user.correo = new_email
	
	
	# Handle password update
	if "contrasena" in update_data and update_data["contrasena"]:
		if db_worker.usuario_id:
			from app.models import User
			from app.core.security import get_password_hash
			db_user = db.query(User).filter(User.usuario_id == db_worker.usuario_id).first()
			if db_user and update_data["contrasena"].strip():
				db_user.contrasena_hash = get_password_hash(update_data["contrasena"].strip())
		update_data.pop("contrasena") # Remove from worker table update
	
	for field, value in update_data.items():
		setattr(db_worker, field, value)
	
	db.commit()
	db.refresh(db_worker)
	return db_worker


def delete_worker(db: Session, worker_id: int) -> bool:
	db_worker = get_worker(db, worker_id)
	if not db_worker:
		return False
	
	db.delete(db_worker)
	db.commit()
	return True


def set_worker_services(db: Session, worker_id: int, service_ids: List[int]) -> Optional[Worker]:
	"""
	Sets the list of services a worker can perform.
	Bulk updates the association table.
	"""
	db_worker = get_worker(db, worker_id)
	if not db_worker:
		return None
	
	if not service_ids:
		db_worker.services = []
	else:
		# Fetch all requested services in one query
		services = db.query(Service).filter(Service.servicio_id.in_(service_ids)).all()
		db_worker.services = services
		
	db.commit()
	db.refresh(db_worker)
	return db_worker


def get_worker_services(db: Session, worker_id: int) -> List[Service]:
	"""Gets all services assigned to a worker."""
	db_worker = get_worker(db, worker_id)
	if not db_worker:
		return []
	return db_worker.services
