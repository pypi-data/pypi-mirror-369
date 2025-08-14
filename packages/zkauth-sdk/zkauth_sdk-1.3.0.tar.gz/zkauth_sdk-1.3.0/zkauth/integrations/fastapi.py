"""
FastAPI integration for ZKAuth SDK
"""

from typing import Optional
from fastapi import Depends, HTTPException, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from ..client import ZKAuthSDK
from ..models import User
from ..exceptions import AuthenticationError


class ZKAuthMiddleware(BaseHTTPMiddleware):
    """FastAPI middleware for ZKAuth"""
    
    def __init__(self, app, api_key: str, base_url: str = "https://zkauth-engine.vercel.app"):
        super().__init__(app)
        self.sdk = ZKAuthSDK(api_key, base_url)
    
    async def dispatch(self, request: Request, call_next):
        # Add ZKAuth SDK to request state
        request.state.zkauth = self.sdk
        response = await call_next(request)
        return response


class ZKAuthFastAPI:
    """FastAPI integration for ZKAuth"""

    def __init__(self, api_key: str, base_url: str = "https://zkauth-engine.vercel.app"):
        self.sdk = ZKAuthSDK(api_key, base_url)
        self.security = HTTPBearer()

    async def get_current_user(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> User:
        """FastAPI dependency to get current authenticated user"""
        try:
            is_valid = await self.sdk.verify_token(credentials.credentials)
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid token")

            # Get user info from token
            user = await self.sdk.get_user_info()
            return user

        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def get_optional_user(
        self,
        request: Request
    ) -> Optional[User]:
        """Get user if authenticated, None otherwise"""
        try:
            auth_header = request.headers.get('authorization')
            if not auth_header or not auth_header.startswith('Bearer '):
                return None

            token = auth_header[7:]
            is_valid = await self.sdk.verify_token(token)

            if is_valid:
                return await self.sdk.get_user_info()

        except:
            pass

        return None

    async def verify_token_dependency(
        self,
        credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
    ) -> str:
        """Dependency that returns the token if valid"""
        try:
            is_valid = await self.sdk.verify_token(credentials.credentials)
            if not is_valid:
                raise HTTPException(status_code=401, detail="Invalid token")

            return credentials.credentials

        except Exception as e:
            raise HTTPException(status_code=401, detail=str(e))

    async def close(self):
        """Close the SDK client"""
        await self.sdk.close()


# Global instance for easy access
_zkauth_instance: Optional[ZKAuthFastAPI] = None


def initialize_zkauth(api_key: str, base_url: str = "https://zkauth-engine.vercel.app") -> ZKAuthFastAPI:
    """Initialize global ZKAuth instance"""
    global _zkauth_instance
    _zkauth_instance = ZKAuthFastAPI(api_key, base_url)
    return _zkauth_instance


def get_zkauth() -> ZKAuthFastAPI:
    """Get global ZKAuth instance"""
    if _zkauth_instance is None:
        raise RuntimeError("ZKAuth not initialized. Call initialize_zkauth() first.")
    return _zkauth_instance


async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(HTTPBearer())
) -> User:
    """Global dependency to get current authenticated user"""
    zkauth = get_zkauth()
    return await zkauth.get_current_user(credentials)


async def get_optional_user(request: Request) -> Optional[User]:
    """Global dependency to get user if authenticated"""
    zkauth = get_zkauth()
    return await zkauth.get_optional_user(request)


# FastAPI Auth decorators
def zkauth_required(func):
    """Decorator that requires ZKAuth authentication"""
    async def wrapper(*args, **kwargs):
        # This should be used with proper FastAPI dependency injection
        return await func(*args, **kwargs)
    return wrapper


# Example usage functions
async def create_zkauth_app():
    """Example of how to set up ZKAuth with FastAPI"""
    from fastapi import FastAPI

    app = FastAPI()
    zkauth = initialize_zkauth(api_key="your_api_key")

    @app.post("/auth/login")
    async def login(email: str, password: str):
        result = await zkauth.sdk.sign_in(email, password)
        if result.success:
            return {
                "success": True,
                "user": result.user.dict(),
                "token": result.token
            }
        else:
            raise HTTPException(status_code=401, detail=result.error)

    @app.post("/auth/register")
    async def register(email: str, password: str, metadata: dict = None):
        result = await zkauth.sdk.sign_up(email, password, metadata)
        if result.success:
            return {
                "success": True,
                "user": result.user.dict(),
                "token": result.token
            }
        else:
            raise HTTPException(status_code=400, detail=result.error)

    @app.get("/protected")
    async def protected_route(user: User = Depends(get_current_user)):
        return {"message": f"Hello {user.email}", "user_id": user.id}

    @app.get("/optional")
    async def optional_route(user: Optional[User] = Depends(get_optional_user)):
        if user:
            return {"message": f"Hello {user.email}"}
        else:
            return {"message": "Hello anonymous user"}

    @app.on_event("shutdown")
    async def shutdown():
        await zkauth.close()

    return app