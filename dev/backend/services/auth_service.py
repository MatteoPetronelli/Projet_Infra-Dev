from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from datetime import datetime, timedelta
from jose import jwt, JWTError
from typing import Optional

SECRET_KEY = "ton_secret_tres_securise"
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
        mock_hash = "$argon2id$v=19$m=65536,t=3,p=4$dDMMS5OBxxm7qk+aAJYx/Q$PZ/JHKOBd9jHJQZCdQpsghnXhAiJPVaHAsJOUjDWpcI"
        
        if email == "directeur@ymmo.fr" and self.verify_password(password, mock_hash):
            return {"email": "directeur@ymmo.fr", "pole": "Direction"}
        return None

    def create_access_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=60)
        to_encode.update({"exp": expire})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    def verify_token(self, token: str) -> Optional[dict]:
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None