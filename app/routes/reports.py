from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.calculation import Calculation
from app.auth.dependencies import get_current_active_user

router = APIRouter(prefix="/reports", tags=["Reports"])


@router.get("/usage")
def calculation_usage_report(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_active_user),
):
    """
    Report Feature:
    - Total calculations
    - Count by type
    - Average result
    """

    total = db.query(func.count(Calculation.id)).filter(
        Calculation.user_id == current_user.id
    ).scalar()

    by_type = (
        db.query(Calculation.type, func.count(Calculation.id))
        .filter(Calculation.user_id == current_user.id)
        .group_by(Calculation.type)
        .all()
    )

    avg_result = db.query(func.avg(Calculation.result)).filter(
        Calculation.user_id == current_user.id
    ).scalar()

    return {
        "total_calculations": total,
        "by_type": {t: c for t, c in by_type},
        "average_result": round(avg_result, 2) if avg_result is not None else None,
    }
