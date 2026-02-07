from sqlalchemy.orm import Session
from app.models.user import User
from app.core.security import get_password_hash, verify_password, create_access_token
from app.schemas.auth import UserRegister, UserLogin


class AuthService:
    @staticmethod
    def register_user(db: Session, payload: UserRegister) -> str:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise ValueError("Email already registered")
        
        user = User(
            email=payload.email,
            hashed_password=get_password_hash(payload.password)
        )
        db.add(user)
        db.commit()
        db.refresh(user)

        token = create_access_token(data={"sub": user.email})
        return token
    

    @staticmethod
    def login_user(db: Session, payload: UserLogin) -> str:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not verify_password(payload.password, user.hashed_password):
            raise ValueError("Invalid credentials")
        
        token = create_access_token(data={"sub": user.email})
        return token
