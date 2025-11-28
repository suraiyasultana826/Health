from fastapi import APIRouter, HTTPException, Form, Request, Response
from fastapi.responses import RedirectResponse
from db.database import SessionLocal
from db import database
import hashlib
import secrets

router = APIRouter()

# Simple session storage (in production, use Redis or similar)
sessions = {}

def hash_password(password: str) -> str:
    """Hash password using SHA-256"""
    return hashlib.sha256(password.encode()).hexdigest()

def create_session(user_id: int) -> str:
    """Create a new session token"""
    token = secrets.token_urlsafe(32)
    sessions[token] = user_id
    return token

def get_user_from_session(token: str):
    """Get user from session token"""
    user_id = sessions.get(token)
    if not user_id:
        return None
    
    db = SessionLocal()
    try:
        user = db.query(database.User).filter(database.User.id == user_id).first()
        return user
    finally:
        db.close()

def delete_session(token: str):
    """Delete a session"""
    if token in sessions:
        del sessions[token]

@router.post("/register")
async def register(
    username: str = Form(...),
    password: str = Form(...),
    email: str = Form(...),
    role: str = Form("user")
):
    """Register a new user"""
    db = SessionLocal()
    try:
        # Check if username already exists
        existing_user = db.query(database.User).filter(
            database.User.username == username
        ).first()
        
        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")
        
        # Check if email already exists
        existing_email = db.query(database.User).filter(
            database.User.email == email
        ).first()
        
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already registered")
        
        # Create new user
        hashed_password = hash_password(password)
        new_user = database.User(
            username=username,
            password=hashed_password,
            email=email,
            role=role
        )
        
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        return {"status": "success", "message": "User registered successfully"}
    
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/login")
async def login(
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Login user"""
    db = SessionLocal()
    try:
        # Find user
        user = db.query(database.User).filter(
            database.User.username == username
        ).first()
        
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Verify password
        hashed_password = hash_password(password)
        if user.password != hashed_password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        
        # Create session
        token = create_session(user.id)
        
        # Set cookie
        response.set_cookie(
            key="session_token",
            value=token,
            httponly=True,
            max_age=86400,  # 24 hours
            samesite="lax"
        )
        
        return {
            "status": "success",
            "message": "Login successful",
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            }
        }
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        db.close()

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Logout user"""
    token = request.cookies.get("session_token")
    
    if token:
        delete_session(token)
    
    response.delete_cookie("session_token")
    
    return {"status": "success", "message": "Logged out successfully"}

@router.get("/check-auth")
async def check_auth(request: Request):
    """Check if user is authenticated"""
    token = request.cookies.get("session_token")
    
    if not token:
        return {"authenticated": False}
    
    user = get_user_from_session(token)
    
    if not user:
        return {"authenticated": False}
    
    return {
        "authenticated": True,
        "user": {
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        }
    }