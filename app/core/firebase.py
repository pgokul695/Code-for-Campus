import firebase_admin
from firebase_admin import credentials, auth
from fastapi import HTTPException, status
import json
from ..config import settings

def initialize_firebase():
    if not firebase_admin._apps:
        if settings.FIREBASE_CREDENTIALS_JSON:
            # For Railway deployment with JSON as env variable
            cred_dict = json.loads(settings.FIREBASE_CREDENTIALS_JSON)
            cred = credentials.Certificate(cred_dict)
        elif settings.FIREBASE_CREDENTIALS_PATH:
            # For local development with file path
            cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        else:
            raise ValueError("Firebase credentials not configured")
        
        firebase_admin.initialize_app(cred)

async def verify_firebase_token(token: str) -> dict:
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid authentication token: {str(e)}"
        )
