from sqlalchemy.orm import Session
from fastapi import HTTPException, status

from ..models.sql_models import UserSQL
from ..models.user_model import UserCreate, UserInDB
from ..core.security import get_password_hash, verify_password

class AuthService:
    def __init__(self, db: Session):
        self.db = db

    def get_user(self, email: str) -> UserSQL | None:
        return self.db.query(UserSQL).filter(UserSQL.email == email).first()

    def create_user(self, user: UserCreate) -> UserInDB:
        hashed_password = get_password_hash(user.password)
        db_user = UserSQL(email=user.email, hashed_password=hashed_password, role=user.role)
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return UserInDB.from_orm(db_user)

    def authenticate_user(self, email: str, password: str) -> UserSQL | None:
        user = self.get_user(email)
        if not user or not verify_password(password, user.hashed_password):
            return None
        return user

    def get_user_by_id(self, user_id: int) -> UserSQL | None:
        return self.db.query(UserSQL).filter(UserSQL.id == user_id).first()


