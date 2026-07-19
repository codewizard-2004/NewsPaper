from fastapi import APIRouter, Depends
from app.core.firebase import get_current_user

router = APIRouter(
    prefix="/settings",
    tags=["settings"],
)

@router.get("/")
def get_settings(user: dict = Depends(get_current_user)):
    """
    Get settings for the currently authenticated user.
    """
    uid = user.get("uid")
    # TODO: Fetch from Firestore users/{uid}/settings
    return {"message": f"Hello {user.get('email')}, here are your settings.", "uid": uid}

@router.put("/")
def update_settings(settings: dict, user: dict = Depends(get_current_user)):
    """
    Update settings for the currently authenticated user.
    """
    uid = user.get("uid")
    # TODO: Save to Firestore users/{uid}/settings
    return {"message": "Settings updated successfully", "uid": uid}
