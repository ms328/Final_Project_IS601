from typing import Optional, List
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.calculation import Calculation
from app.auth.dependencies import get_current_user
from app.schemas.calculation import CalculationResponse

router = APIRouter(prefix="/calculations", tags=["Calculations"])


@router.get("/", response_model=List[CalculationResponse])
def list_calculations(
    type: Optional[str] = Query(None, description="Filter by calculation type"),
    sort: str = Query("desc", regex="^(asc|desc)$"),
    limit: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """
    Option 1 Feature:
    - View calculation history
    - Filter by type
    - Sort by date
    """

    query = db.query(Calculation).filter(
        Calculation.user_id == current_user.id
    )

    if type:
        query = query.filter(Calculation.type == type)

    if sort == "asc":
        query = query.order_by(Calculation.created_at.asc())
    else:
        query = query.order_by(Calculation.created_at.desc())

    return query.limit(limit).all()
