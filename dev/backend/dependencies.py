from fastapi import Request, HTTPException, Depends
from services.auth_service import AuthService

auth_service = AuthService()

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifie")
    
    user = auth_service.verify_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    return user

def check_pole(allowed_poles: list):
    def role_checker(user: dict = Depends(get_current_user)):
        if user["pole"] not in allowed_poles:
            raise HTTPException(
                status_code=403, 
                detail=f"Acces Interdit : Votre pole ({user['pole']}) n'a pas les droits."
            )
        return user
    return role_checker