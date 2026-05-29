from fastapi import Request, HTTPException, Depends
from services.auth_service import AuthService
from database.database import get_user_by_email

auth_service = AuthService()

async def get_current_user(request: Request):
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(status_code=401, detail="Non authentifié")
    
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Session invalide")
    
    user_db = get_user_by_email(payload["email"])
    
    if not user_db:
        raise HTTPException(status_code=401, detail="Utilisateur introuvable ou supprimé")

    return {"email": user_db["email"], "pole": user_db["pole"]}

def check_pole(allowed_poles: list):
    def role_checker(user: dict = Depends(get_current_user)):
        if user["pole"] not in allowed_poles:
            raise HTTPException(
                status_code=403, 
                detail=f"Accès Interdit : Votre pôle actuel ({user['pole']}) n'a pas les droits."
            )
        return user
    return role_checker