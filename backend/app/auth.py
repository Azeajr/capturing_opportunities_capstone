from fastapi import Depends, HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import get_config

config = get_config()

api_key_header = APIKeyHeader(name="API-Key")


def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != config.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key"
        )
    return api_key
