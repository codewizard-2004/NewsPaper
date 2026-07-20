import os
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Security
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from dotenv import load_dotenv

load_dotenv()

# Initialize Firebase Admin SDK
# Try to load from service account key if provided, else initialize default app
def init_firebase():
    if not firebase_admin._apps:
        cert_path = os.getenv("FIREBASE_CREDENTIALS_PATH")
        if cert_path and os.path.exists(cert_path):
            cred = credentials.Certificate(cert_path)
            firebase_admin.initialize_app(cred)
        else:
            # If no service account is provided, default initialization
            # Note: without service account, verify_id_token still works by downloading public keys
            firebase_admin.initialize_app()

init_firebase()

security = HTTPBearer()

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    """
    FastAPI dependency to verify the Firebase ID token.
    Extracts the Bearer token, verifies it, and returns the decoded user data.
    """
    token = credentials.credentials
    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(
            status_code=401,
            detail=f"Invalid authentication credentials: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )
