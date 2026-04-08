from fastapi import HTTPException, status

class YmmoException(HTTPException):
    def __init__(self, status_code: int, detail: str, error_code: str = "GENERIC_ERROR"):
        super().__init__(status_code=status_code, detail={"message": detail, "code": error_code})

class AuthenticationError(YmmoException):
    def __init__(self):
        super().__init__(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identifiants invalides ou session expiree",
            error_code="AUTH_FAILED"
        )

class ForbiddenError(YmmoException):
    def __init__(self, pole: str):
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Acces refuse pour le pole {pole}",
            error_code="INSUFFICIENT_PERMISSIONS"
        )