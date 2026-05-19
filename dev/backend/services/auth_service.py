from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta, timezone
from jose import jwt, JWTError
from typing import Optional
from dotenv import load_dotenv
import os
import sys

load_dotenv()

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from database.database import get_user_by_email, insert_user

SECRET_KEY = os.getenv("SECRET_KEY", "fallback_secret_key_for_dev")
ALGORITHM = "HS256"

class AuthService:
    def __init__(self):
        self.ph = PasswordHasher()

    def hash_password(self, password: str) -> str:
        return self.ph.hash(password)

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        try:
            return self.ph.verify(hashed_password, plain_password)
        except (VerifyMismatchError, Exception):
            return False

    def authenticate(self, email: str, password: str):
        user_record = get_user_by_email(email)
        if user_record and self.verify_password(password, user_record["password_hash"]):
            return {"email": user_record["email"], "pole": user_record["pole"]}
        return None

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.now(timezone.utc) + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None
    
    def register_user(self, email: str, password: str, pole: str = "Utilisateur"):
        existing_user = get_user_by_email(email)
        if existing_user:
            raise ValueError("Cet email est déjà utilisé.")
            
        hashed_password = self.hash_password(password)
        insert_user(email, hashed_password, pole)
        return {"email": email, "pole": pole}