from typing import Generator, List
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from jose import JWTError, jwt

from .db import get_db
from .core.security import SECRET_KEY, ALGORITHM, oauth2_scheme
from .models.user_model import TokenData
from .models.sql_models import UserSQL
from .services.auth_service import AuthService

def get_current_user(db: Session = Depends(get_db), token: str = Depends(oauth2_scheme)) -> UserSQL:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    auth_service = AuthService(db)
    user = auth_service.get_user(email=token_data.email)
    if user is None:
        raise credentials_exception
    return user

def get_current_active_user(current_user: UserSQL = Depends(get_current_user)) -> UserSQL:
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user

def has_role(roles: List[str]):
    def role_checker(current_user: UserSQL = Depends(get_current_active_user)) -> bool:
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not enough permissions",
            )
        return True
    return role_checker


