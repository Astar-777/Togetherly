from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session


from app.api.deps import get_db
from app.services.auth import AuthService
from app.schemas.auth import UserRegister, UserLogin, TokenResponse

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=TokenResponse)
def register_user(payload: UserRegister, db: Session = Depends(get_db)):
    try:
        token = AuthService.register_user(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    

    return {"access_token": token, "token_type": "bearer"}


@router.post("/login", response_model=TokenResponse)
def login(payload: UserLogin, db: Session = Depends(get_db)):
    try:
        token = AuthService.login_user(db, payload)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"}
        )
    
    return {"access_token": token, "token_type": "bearer"}
