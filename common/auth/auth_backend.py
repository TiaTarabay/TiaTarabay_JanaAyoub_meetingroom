from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext



#   JWT + Security Settings
SECRET_KEY = "your_secret_key"    
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Extract the token from Authorization: Bearer <token>
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")



#   Password Helper Functions

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain: str, hashed: str) -> bool:
    """Check if the plain password matches the hashed one."""
    return pwd_context.verify(plain, hashed)



#   Create JWT Token

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    """Create a JWT access token with expiration time."""
    payload = data.copy()

    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)

    payload["exp"] = expire

    token = jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)
    return token


# ==============================
#   Decode Token → Get User
# ==============================

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db=None,
    user_model=None,
):
    """
    Decode the JWT token, get the user ID from it,
    then load the user from the database.

    NOTE:
    - db and user_model are passed from each microservice
      (so this file stays reusable).
    """

    # Safety check: microservice MUST pass db + model
    if db is None or user_model is None:
        raise RuntimeError(
            "get_current_user() requires db and user_model arguments"
        )

    # Decode token
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = payload.get("id")

        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token: missing user ID",
            )

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate token",
        )

    # Load user from DB
    user = db.query(user_model).filter(user_model.id == user_id).first()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return user
