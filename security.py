from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from database import get_connection
from psycopg2.errors import UniqueViolation
from auth import create_access_token

router = APIRouter(prefix="/auth", tags=["auth"])

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class AuthRequest(BaseModel):
    email: EmailStr
    password: str


@router.post("/register", status_code=status.HTTP_201_CREATED)
def register(body: AuthRequest):
    hashed_password = pwd_context.hash(body.password)

    try:
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO users (email, password)
                    VALUES (%s, %s)
                    RETURNING id
                    """,
                    (body.email, hashed_password),
                )
                conn.commit()
    except UniqueViolation:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User already exists",
        )

    return {"message": "User created successfully"}


@router.post("/login")
def login(body: AuthRequest):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT id, password FROM users WHERE email = %s", (body.email,))
            user = cur.fetchone()

    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not pwd_context.verify(body.password, user["password"]):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = create_access_token({"sub": str(user["id"])})
    return {"access_token": token, "token_type": "bearer"}
