from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.api import deps
from app.crud import crud_ratings
from app.models import User
from app.schemas.ratings import ReviewCreate, ReviewResponse, ReviewUpdate
from app.core.permissions import (
    RoleType,
    get_user_role_name,
    require_admin,
)

router = APIRouter()


@router.get("/", response_model=List[ReviewResponse])
def get_reviews(
    establecimiento_id: Optional[int] = Query(None),
    usuario_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can view reviews (read-only)."""
    return crud_ratings.get_reviews(
        db,
        skip=skip,
        limit=limit,
        establecimiento_id=establecimiento_id,
        usuario_id=usuario_id,
    )


@router.get("/me", response_model=List[ReviewResponse])
def get_my_reviews(
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Get current user's reviews."""
    return crud_ratings.get_reviews(
        db, skip=skip, limit=limit, usuario_id=current_user.usuario_id
    )


@router.get("/{review_id}", response_model=ReviewResponse)
def get_review(
    review_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Any authenticated user can view a review (read-only)."""
    review = crud_ratings.get_review(db, review_id)
    if not review:
        raise HTTPException(status_code=404, detail="Review not found")
    return review


@router.post("/", response_model=ReviewResponse)
def create_review(
    review: ReviewCreate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """
    Create a review. Clients can only create reviews as themselves.
    Google Maps style: one review per user per establishment (enforced in CRUD).
    """
    # Users can only create reviews for themselves
    if review.usuario_id != current_user.usuario_id:
        raise HTTPException(
            status_code=403,
            detail="You can only create reviews as yourself"
        )
    
    try:
        return crud_ratings.create_review(db, review)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{review_id}", response_model=ReviewResponse)
def update_review(
    review_id: int,
    review: ReviewUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Update a review. Users can only update their own reviews."""
    db_review = crud_ratings.get_review(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    user_role = get_user_role_name(current_user)
    if db_review.usuario_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only update your own reviews")
    
    db_review = crud_ratings.update_review(db, review_id, review)
    return db_review


@router.patch("/{review_id}", response_model=ReviewResponse)
def patch_review(
    review_id: int,
    review: ReviewUpdate,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Partial update for a review. Same rules as PUT."""
    db_review = crud_ratings.get_review(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    user_role = get_user_role_name(current_user)
    if db_review.usuario_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only update your own reviews")
    
    db_review = crud_ratings.update_review(db, review_id, review)
    return db_review


@router.delete("/{review_id}")
def delete_review(
    review_id: int,
    db: Session = Depends(deps.get_db),
    current_user: User = Depends(deps.get_current_user),
):
    """Delete a review. Users can only delete their own reviews. Admins can delete any."""
    db_review = crud_ratings.get_review(db, review_id)
    if not db_review:
        raise HTTPException(status_code=404, detail="Review not found")
    
    user_role = get_user_role_name(current_user)
    if db_review.usuario_id != current_user.usuario_id and user_role != RoleType.ADMIN.value:
        raise HTTPException(status_code=403, detail="You can only delete your own reviews")
    
    success = crud_ratings.delete_review(db, review_id)
    if not success:
        raise HTTPException(status_code=404, detail="Review not found")
    return {"message": "Review deleted successfully"}
