from pydantic import BaseModel, EmailStr


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class LoginResponse(BaseModel):
    user_id: str
    email: str
    access_token: str
    token_type: str = "bearer"
    role: str


class RegisterResponse(BaseModel):
    id: str
    email: str
    role: str
    message: str