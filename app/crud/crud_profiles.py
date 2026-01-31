from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Profile
from app.schemas.profiles import ProfileCreate, ProfileUpdate


def get_profile(db: Session, profile_id: int) -> Optional[Profile]:
    return db.query(Profile).filter(Profile.perfil_id == profile_id).first()


def get_profile_by_establishment(db: Session, establecimiento_id: int) -> Optional[Profile]:
    return db.query(Profile).filter(Profile.establecimiento_id == establecimiento_id).first()


def get_profiles(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
) -> List[Profile]:
    query = db.query(Profile)
    if establecimiento_id is not None:
        query = query.filter(Profile.establecimiento_id == establecimiento_id)
    return query.offset(skip).limit(limit).all()


def create_profile(db: Session, profile: ProfileCreate) -> Profile:
    # Verify establecimiento_id exists
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == profile.establecimiento_id)
        .first()
    )
    if not establishment:
        raise ValueError(f"Establishment with id {profile.establecimiento_id} does not exist")
    
    # Check if profile already exists for this establishment
    existing_profile = get_profile_by_establishment(db, profile.establecimiento_id)
    if existing_profile:
        raise ValueError(f"Profile already exists for establishment {profile.establecimiento_id}")
    
    profile_data = profile.model_dump()
    db_profile = Profile(**profile_data)  # type: ignore[arg-type]
    db.add(db_profile)
    db.commit()
    db.refresh(db_profile)
    return db_profile


def update_profile(db: Session, profile_id: int, profile: ProfileUpdate) -> Optional[Profile]:
    db_profile = get_profile(db, profile_id)
    if not db_profile:
        return None

    update_data = profile.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_profile, field, value)

    db.commit()
    db.refresh(db_profile)
    return db_profile


def delete_profile(db: Session, profile_id: int) -> bool:
    db_profile = get_profile(db, profile_id)
    if not db_profile:
        return False

    db.delete(db_profile)
    db.commit()
    return True
