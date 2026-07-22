from fastapi import APIRouter, HTTPException, status
from sqlalchemy.orm import Session

from app.dependencies import DB
from app.models.user import User
from app.schemas.auth import LoginRequest, LoginResponse, AuthUser
from app.utils.auth import verify_password, create_access_token

router = APIRouter(tags=["Auth"])


@router.post("/auth/login", response_model=LoginResponse)
def login(req: LoginRequest, db: DB):
    user = db.query(User).filter(
        User.email == req.email,
        User.role == req.role,
        User.is_active == True,
    ).first()

    if not user or not verify_password(req.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email, password, or role.",
        )

    token_data = {
        "sub": str(user.id),
        "role": user.role.value,
        "name": user.name,
        "email": user.email,
    }
    access_token = create_access_token(token_data)

    return LoginResponse(
        access_token=access_token,
        user=AuthUser(
            id=str(user.id),
            name=user.name,
            email=user.email,
            role=user.role,
        ),
    )
