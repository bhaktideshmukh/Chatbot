from pydantic import BaseModel
from typing import Optional

# Pydantic models to validate our incoming data
class LoginRequest(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    username: str
    role: str
    message: str

# Our Dummy Database
# Notice the roles exactly match the folder names in backend/data
users_db = {
    "peter": {"password": "password123", "role": "finance"},
    "sarah": {"password": "password123", "role": "hr"},
    "john": {"password": "password123", "role": "marketing"},
    "alice": {"password": "password123", "role": "engineering"},
    "boss": {"password": "boss123", "role": "c-level"},
    "intern": {"password": "password123", "role": "general"}
}

def authenticate_user(login_data: LoginRequest) -> Optional[UserResponse]:
    """
    Checks if the user exists and the password matches.
    Returns a UserResponse with their role if successful, else None.
    """
    user = users_db.get(login_data.username)
    
    if user and user["password"] == login_data.password:
        return UserResponse(
            username=login_data.username, 
            role=user["role"],
            message="Login successful!"
        )
    return None
