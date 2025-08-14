# ZKAuth Python SDK

**v1.3.0** - Zero-knowledge proof authentication for Python applications.

⚠️ **IMPORTANT**: ZKAuth uses Zero-Knowledge Proofs, NOT traditional passwords! The SDK requires cognitive questions for enhanced security.

## Installation

```bash
pip install zkauth-sdk
```

## Quick Start

> **🔑 First time?** Get your API key at: **[ZKAuth Developer Platform](https://zkauth-devleoper-dashboard.vercel.app)**

The SDK connects to the ZKAuth engine automatically - you just need your API key!

### Basic Usage

```python
import asyncio
from zkauth import ZKAuthSDK, SignUpData, SignInData

async def main():
    async with ZKAuthSDK(
        api_key="zka_live_your_api_key_here"
    ) as client:
        # Sign up a new user with ZKP format (SDK handles commitment generation)
        signup_data = SignUpData(
            email="user@example.com",
            password="secure-password",
            cognitive_question="What is your favorite color?",
            cognitive_answer="blue"
        )
        signup_result = await client.sign_up(signup_data)
        
        if signup_result.success:
            print(f"User registered: {signup_result.user.email}")
            print(f"Registration token: {signup_result.token}")
        
        # Sign in with ZKP authentication
        signin_data = SignInData(
            email="user@example.com",
            password="secure-password"
        )
        signin_result = await client.sign_in(signin_data)
        
        if signin_result.success:
            print(f"User authenticated: {signin_result.user.email}")
            print(f"Session token: {signin_result.token}")
        else:
            print(f"Authentication failed: {signin_result.error}")

# Run the async function
asyncio.run(main())
```

### Django Integration

```python
# settings.py
INSTALLED_APPS = [
    # ... other apps
    'zkauth.integrations.django',
]

ZKAUTH_CONFIG = {
    'API_KEY': 'zka_live_your_api_key_here',
    'BASE_URL': 'https://zkauth-engine.vercel.app',
    'ENABLE_DEVICE_FINGERPRINTING': True,
}

# views.py
from django.http import JsonResponse
from zkauth.integrations.django import zkauth_required

@zkauth_required
def protected_view(request):
    user = request.zkauth_user
    return JsonResponse({
        'message': 'Access granted',
        'user': {
            'id': user.id,
            'email': user.email,
            'created_at': user.created_at.isoformat()
        }
    })

# middleware.py
from zkauth.integrations.django_middleware import ZKAuthMiddleware

# Add to MIDDLEWARE in settings.py
MIDDLEWARE = [
    # ... other middleware
    'zkauth.integrations.django_middleware.ZKAuthMiddleware',
]
```

### FastAPI Integration

```python
from fastapi import FastAPI, Depends, HTTPException
from zkauth.integrations.fastapi import ZKAuthMiddleware, get_current_user
from zkauth.models import User

app = FastAPI(title="ZKAuth FastAPI Demo")

# Add ZKAuth middleware
app.add_middleware(
    ZKAuthMiddleware,
    api_key="zka_live_your_api_key_here",
    base_url="https://zkauth-engine.vercel.app"
)

@app.get("/protected")
async def protected_route(user: User = Depends(get_current_user)):
    return {
        "message": "Access granted",
        "user": {
            "id": user.id,
            "email": user.email,
            "created_at": user.created_at
        }
    }

@app.post("/auth/signup")
async def signup(
    email: str, 
    password: str, 
    cognitive_question: str, 
    cognitive_answer: str
):
    from zkauth import SignUpData
    async with ZKAuthSDK(api_key="zka_live_your_api_key_here") as client:
        signup_data = SignUpData(
            email=email,
            password=password,
            cognitive_question=cognitive_question,
            cognitive_answer=cognitive_answer
        )
        result = await client.sign_up(signup_data)
        if not result.success:
            raise HTTPException(status_code=400, detail=result.error)
        return {"user": result.user.dict(), "token": result.token}

@app.post("/auth/signin")
async def signin(email: str, password: str):
    from zkauth import SignInData
    async with ZKAuthSDK(api_key="zka_live_your_api_key_here") as client:
        signin_data = SignInData(email=email, password=password)
        result = await client.sign_in(signin_data)
        if not result.success:
            raise HTTPException(status_code=401, detail=result.error)
        return {"user": result.user.dict(), "token": result.token}
```

### Advanced Usage

```python
import asyncio
from zkauth import ZKAuthSDK
from zkauth.exceptions import AuthenticationError, ValidationError

async def advanced_example():
    # Initialize with custom configuration
    client = ZKAuthSDK(
        api_key="zka_live_your_api_key_here",
        base_url="https://zkauth-engine.vercel.app",  # Optional: defaults to this
        timeout=60.0,  # Request timeout in seconds
        max_retries=5,  # Number of retry attempts
        enable_device_fingerprinting=True  # Enable device security
    )
    
    try:
        # Health check
        if not await client.health_check():
            print("⚠️ ZKAuth service is not available")
            return
        
        # Register user with ZKP format and metadata
        from zkauth import SignUpData
        signup_data = SignUpData(
            email="advanced@example.com",
            password="SecureP@ssw0rd123",
            cognitive_question="What city were you born in?",
            cognitive_answer="New York",
            metadata={
                "signup_source": "mobile_app",
                "referral_code": "REF123",
                "user_preferences": {
                    "theme": "dark",
                    "notifications": True
                }
            }
        )
        result = await client.sign_up(signup_data)
        
        if result.success:
            print(f"✅ User registered: {result.user.email}")
            
            # Get user information
            user_info = await client.get_user_info()
            print(f"User ID: {user_info.id}")
            print(f"Created: {user_info.created_at}")
            
            # Get session information
            session_info = await client.get_session_info()
            print(f"Session expires: {session_info.expires_at}")
            
            # Change password
            password_change = await client.change_password(
                current_password="SecureP@ssw0rd123",
                new_password="NewSecureP@ssw0rd456",
                email="advanced@example.com"
            )
            
            if password_change.success:
                print("✅ Password changed successfully")
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
    except AuthenticationError as e:
        print(f"❌ Authentication failed: {e}")
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
    finally:
        await client.close()

# Run the example
asyncio.run(advanced_example())
```

## Features

- ✅ **Zero-knowledge proof authentication** - Real cryptographic ZK proofs using Groth16 protocol
- ✅ **Async/await support** - Built for modern Python async applications
- ✅ **Django and FastAPI integrations** - Ready-made middleware and decorators
- ✅ **Type hints with Pydantic models** - Full type safety and validation
- ✅ **Comprehensive error handling** - Structured exceptions for all scenarios
- ✅ **Session management** - Automatic token handling and refresh
- ✅ **Device fingerprinting** - Hardware-based security with fallbacks
- ✅ **Python 3.8+ support** - Compatible with modern Python versions
- ✅ **Production ready** - Retry logic, timeouts, and robust error handling

## API Reference

### Core Methods

```python
# Authentication with ZKP format
await client.sign_up(user_data: SignUpData) -> AuthResult
await client.sign_in(user_data: SignInData) -> AuthResult
await client.approve_device(approval_code: str) -> AuthResult

# Session management
await client.get_user_info() -> User
await client.get_session_info() -> SessionInfo
await client.verify_token(token: str) -> bool
await client.refresh_token() -> Optional[str]

# Account management
await client.change_password(current_password: str, new_password: str, email: str) -> AuthResult
await client.sign_out() -> None

# Utility
await client.health_check() -> bool
await client.close() -> None  # Always call this or use async context manager
```

### Configuration

```python
client = ZKAuthSDK(
    api_key: str,                           # Required: Your ZKAuth API key
    base_url: str = "https://zkauth-engine.vercel.app",  # Optional: Custom base URL
    timeout: float = 30.0,                  # Optional: Request timeout in seconds
    max_retries: int = 3,                   # Optional: Number of retry attempts
    enable_device_fingerprinting: bool = True  # Optional: Enable device security
)
```

### Error Handling

All methods return structured error responses:

```python
class AuthResult:
    success: bool
    user: Optional[User] = None
    token: Optional[str] = None
    error: Optional[str] = None
    requires_device_verification: bool = False
```

**Type Definitions:**
```python
class SignUpData:
    email: str
    password: str
    cognitive_question: str
    cognitive_answer: str
    metadata: Optional[Dict[str, Any]] = None

class SignInData:
    email: str
    password: str

class User:
    id: str
    email: str
    created_at: datetime
    last_login: Optional[datetime] = None
    metadata: Dict[str, Any] = {}
```

**Exception Types:**
- `ZKAuthError` - Base exception for all ZKAuth errors
- `ValidationError` - Input validation errors (email format, password strength, cognitive questions)
- `AuthenticationError` - Authentication failures (wrong credentials, expired tokens)
- `NetworkError` - Network connectivity issues
- `APIError` - Server-side errors with HTTP status codes

## Getting Your API Key

1. Visit the **[ZKAuth Developer Platform](https://zkauth-devleoper-dashboard.vercel.app)** ← Register here!
2. Sign up for a developer account
3. Create a new project
4. Generate your API keys (test and live)
5. Use the live key (`zka_live_...`) for production

> **Note**: The ZKAuth engine runs at `https://zkauth-engine.vercel.app` (used internally by the SDK), but developers register at the **Developer Platform** link above.

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run tests with coverage
pytest --cov=zkauth

# Format code
black zkauth/
isort zkauth/

# Type checking
mypy zkauth/
```

## License

MIT