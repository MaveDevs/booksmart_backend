from typing import List, Optional

from sqlalchemy.orm import Session

from app.models import Establishment, Review, User
from app.schemas.ratings import ReviewCreate, ReviewUpdate


def get_review(db: Session, review_id: int) -> Optional[Review]:
    return db.query(Review).filter(Review.resena_id == review_id).first()


def get_review_by_user_and_establishment(
    db: Session, usuario_id: int, establecimiento_id: int
) -> Optional[Review]:
    return (
        db.query(Review)
        .filter(
            Review.usuario_id == usuario_id,
            Review.establecimiento_id == establecimiento_id,
        )
        .first()
    )


def get_reviews(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    establecimiento_id: Optional[int] = None,
    usuario_id: Optional[int] = None,
) -> List[Review]:
    query = db.query(Review)
    if establecimiento_id is not None:
        query = query.filter(Review.establecimiento_id == establecimiento_id)
    if usuario_id is not None:
        query = query.filter(Review.usuario_id == usuario_id)
    return query.offset(skip).limit(limit).all()


def create_review(db: Session, review: ReviewCreate) -> Review:
    # Verify establecimiento_id exists
    establishment = (
        db.query(Establishment)
        .filter(Establishment.establecimiento_id == review.establecimiento_id)
        .first()
    )
    if not establishment:
        raise ValueError(f"Establishment with id {review.establecimiento_id} does not exist")
    
    # Verify usuario_id exists
    user = db.query(User).filter(User.usuario_id == review.usuario_id).first()
    if not user:
        raise ValueError(f"User with id {review.usuario_id} does not exist")
    
    # Check if user already reviewed this establishment (Google Maps style - one review per user per place)
    existing_review = get_review_by_user_and_establishment(
        db, review.usuario_id, review.establecimiento_id
    )
    if existing_review:
        raise ValueError(
            f"User {review.usuario_id} has already reviewed establishment {review.establecimiento_id}. "
            "Use update to modify the existing review."
        )
    
    review_data = review.model_dump()
    db_review = Review(**review_data)  # type: ignore[arg-type]
    db.add(db_review)
    db.commit()
    db.refresh(db_review)
    return db_review


def update_review(db: Session, review_id: int, review: ReviewUpdate) -> Optional[Review]:
    db_review = get_review(db, review_id)
    if not db_review:
        return None

    update_data = review.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_review, field, value)

    db.commit()
    db.refresh(db_review)
    return db_review


def delete_review(db: Session, review_id: int) -> bool:
    db_review = get_review(db, review_id)
    if not db_review:
        return False

    db.delete(db_review)
    db.commit()
    return True
