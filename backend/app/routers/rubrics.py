from fastapi import APIRouter, HTTPException, status

from app.dependencies import DB, CurrentUser, CurrentFaculty, CurrentHOD
from app.models.rubric import Rubric
from app.schemas.rubric import RubricCreate, RubricOut

router = APIRouter(tags=["Rubrics"])


def _to_out(rubric: Rubric) -> RubricOut:
    from app.schemas.rubric import RubricCriteriaItem
    return RubricOut(
        rubricId=str(rubric.id),
        name=rubric.name,
        department=rubric.department,
        createdBy=rubric.creator.name,
        isApproved=rubric.is_approved,
        criteria=[RubricCriteriaItem(**c) for c in (rubric.criteria or [])],
        createdAt=rubric.created_at.isoformat(),
    )


@router.get("/rubrics", response_model=list[RubricOut])
def list_rubrics(current_user: CurrentUser, db: DB):
    rubrics = db.query(Rubric).order_by(Rubric.created_at.desc()).all()
    return [_to_out(r) for r in rubrics]


@router.post("/rubrics", response_model=RubricOut, status_code=status.HTTP_201_CREATED)
def create_rubric(payload: RubricCreate, current_user: CurrentFaculty, db: DB):
    rubric = Rubric(
        name=payload.name,
        department=payload.department,
        created_by_id=current_user.id,
        is_approved=False,
        criteria=[c.model_dump() for c in payload.criteria],
    )
    db.add(rubric)
    db.commit()
    db.refresh(rubric)
    return _to_out(rubric)


@router.patch("/rubrics/{rubric_id}/approve", response_model=RubricOut)
def approve_rubric(rubric_id: str, current_user: CurrentHOD, db: DB):
    rubric = db.query(Rubric).filter(Rubric.id == rubric_id).first()
    if not rubric:
        raise HTTPException(status_code=404, detail="Rubric not found")
    rubric.is_approved = True
    db.commit()
    db.refresh(rubric)
    return _to_out(rubric)
