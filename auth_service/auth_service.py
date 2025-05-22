from fastapi import FastAPI, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
import os
import uuid
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from psycopg2 import OperationalError
import consul_helpers as ch

SECRET_KEY = os.getenv("SECRET_KEY", "your_secret_key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

auth_service = FastAPI()

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

# Retry logic for connecting to PostgreSQL
def connect_to_postgres():
    retries = 5
    delay = 5  # seconds
    for i in range(retries):
        try:
            conn = psycopg2.connect(
            dbname=os.getenv("POSTGRES_DB", "auth_db"),
            user=os.getenv("POSTGRES_USER", "postgres"),
            password=os.getenv("POSTGRES_PASSWORD", "password"),
            host=os.getenv("POSTGRES_HOST", "postgres-auth"),
            port=os.getenv("POSTGRES_PORT", "5432"),
            cursor_factory=RealDictCursor)

            return conn
        except OperationalError as e:
            print(f"Error connecting to PostgreSQL: {e}")
            print(f"Connecting to PostgreSQL database {os.getenv('POSTGRES_DB', 'auth_db')} at {os.getenv('POSTGRES_HOST', 'localhost')}:{os.getenv('POSTGRES_PORT', '5432')} with user {os.getenv('POSTGRES_USER','postgres')} and password {os.getenv('POSTGRES_PASSWORD','password')}" )

            if i < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise HTTPException(status_code=500, detail="Could not connect to database after multiple retries")

# Establish the connection
conn = connect_to_postgres()
cursor = conn.cursor()

# Create tables if they don't exist
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY,
    username TEXT UNIQUE NOT NULL,
    hashed_password TEXT NOT NULL
);
''')
cursor.execute('''
CREATE TABLE IF NOT EXISTS revoked_tokens (
    token TEXT PRIMARY KEY,
    revoked_at TIMESTAMP DEFAULT now()
);
''')
conn.commit()

class User(BaseModel):
    username: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

# Utility functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def revoke_token(token: str):
    cursor.execute("INSERT INTO revoked_tokens (token) VALUES (%s) ON CONFLICT DO NOTHING", (token,))
    conn.commit()

def is_token_revoked(token: str) -> bool:
    cursor.execute("SELECT 1 FROM revoked_tokens WHERE token = %s", (token,))
    return cursor.fetchone() is not None

async def get_current_user(token: str = Depends(oauth2_scheme)):
    if is_token_revoked(token):
        raise HTTPException(status_code=401, detail="Token revoked")

    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")

    cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
    user = cursor.fetchone()
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Routes
@auth_service.post("/auth/register")
def register(user: User):
    hashed_password = get_password_hash(user.password)
    try:
        cursor.execute(
            "INSERT INTO users (id, username, hashed_password) VALUES (%s, %s, %s)",
            (str(uuid.uuid4()), user.username, hashed_password)
        )
        conn.commit()
    except psycopg2.errors.UniqueViolation:
        conn.rollback()
        raise HTTPException(status_code=400, detail="Username already registered")
    return {"message": "User registered successfully"}

@auth_service.post("/auth/login", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    cursor.execute("SELECT * FROM users WHERE username = %s", (form_data.username,))
    user = cursor.fetchone()
    if not user or not verify_password(form_data.password, user["hashed_password"]):
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token = create_access_token(data={"sub": user["username"]}, expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    return {"access_token": access_token, "token_type": "bearer"}

@auth_service.get("/auth/session/validate")
def validate_session(current_user: dict = Depends(get_current_user)):
    return {"username": current_user["username"]}

@auth_service.post("/auth/logout")
def logout(token: str = Depends(oauth2_scheme)):
    revoke_token(token)
    return {"message": "Session terminated"}

@auth_service.get("/health")
def health():
    return {"status": "Auth service is healthy"}

@auth_service.get("/auth/session/health")
def health():
    return {"status": "Auth service is healthy"}

@auth_service.on_event("startup")
def startup():
    print("Starting Auth service...")

    ch.register_consul_service(
        "auth", 
        os.getenv("INSTANCE_ID", "auth-0"), 
        os.getenv("INSTANCE_HOST", "localhost"), 
        int(os.getenv("INSTANCE_PORT", 9100)), 
        30, 60, "/health"
    )

    print("Auth service started")

@auth_service.on_event("shutdown")
def shutdown():
    conn.close()
    print("Auth service shut down")
