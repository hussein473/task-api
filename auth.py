import os
from typing import Optional

from dotenv import load_dotenv
from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from supabase import create_client

load_dotenv()
supabase = create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_KEY"])
print("Supabase client ready")

bearer = HTTPBearer(auto_error=False)


def get_token(creds: Optional[HTTPAuthorizationCredentials] = Depends(bearer)) -> str:
    if creds is None or creds.scheme.lower() != "bearer" or not creds.credentials.strip():
        raise HTTPException(status_code=401, detail="Access token required")
    return creds.credentials.strip()


def verify_token(token: str = Depends(get_token)):
    try:
        user = supabase.auth.get_user(token).user  # asks Supabase: is this token real?
    except Exception:
        user = None
    if user is None:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    return user