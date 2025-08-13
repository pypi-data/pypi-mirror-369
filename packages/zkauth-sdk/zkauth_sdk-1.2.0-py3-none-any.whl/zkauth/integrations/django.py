"""
Django integration for ZKAuth SDK
"""

import asyncio
from typing import Optional

from django.contrib.auth.models import AnonymousUser
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
import json

from ..client import ZKAuthSDK
from ..models import User as ZKAuthUser


class ZKAuthMiddleware:
    """Django middleware for ZKAuth authentication"""

    def __init__(self, get_response):
        self.get_response = get_response
        # Initialize SDK with settings
        api_key = getattr(settings, 'ZKAUTH_API_KEY', None)
        if not api_key:
            raise ValueError("ZKAUTH_API_KEY setting is required")

        base_url = getattr(settings, 'ZKAUTH_BASE_URL', 'https://zkauth-engine.vercel.app')
        self.sdk = ZKAuthSDK(api_key, base_url)

    def __call__(self, request):
        # Check for ZKAuth token
        auth_header = request.headers.get('Authorization')
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header[7:]

            # Verify token asynchronously
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                is_valid = loop.run_until_complete(self.sdk.verify_token(token))
                if is_valid:
                    # Get or create user
                    user = self.get_or_create_user_from_token(token)
                    request.user = user
            except Exception as e:
                print(f"ZKAuth token validation error: {e}")
            finally:
                loop.close()

        response = self.get_response(request)
        return response

    def get_or_create_user_from_token(self, token):
        """Get or create user from token (simplified implementation)"""
        # In practice, you would decode the JWT token to get user info
        # This is a simplified implementation
        try:
            # You might want to create a custom user model or use Django's User model
            # For now, return AnonymousUser
            return AnonymousUser()
        except Exception:
            return AnonymousUser()


@csrf_exempt
@require_http_methods(["POST"])
def zkauth_login(request):
    """Handle ZKAuth login"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')

        if not email or not password:
            return JsonResponse({'error': 'Email and password required'}, status=400)

        # Use ZKAuth SDK
        api_key = getattr(settings, 'ZKAUTH_API_KEY')
        base_url = getattr(settings, 'ZKAUTH_BASE_URL', 'https://zkauth-engine.vercel.app')
        sdk = ZKAuthSDK(api_key, base_url)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(sdk.sign_in(email, password))

            if result.success:
                # Store user session
                request.session['zkauth_token'] = result.token
                request.session['zkauth_user'] = {
                    'id': result.user.id,
                    'email': result.user.email
                }

                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': result.user.id,
                        'email': result.user.email
                    }
                })
            else:
                return JsonResponse({'error': result.error}, status=401)

        finally:
            loop.run_until_complete(sdk.close())
            loop.close()

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def zkauth_register(request):
    """Handle ZKAuth registration"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        password = data.get('password')
        metadata = data.get('metadata', {})

        if not email or not password:
            return JsonResponse({'error': 'Email and password required'}, status=400)

        # Use ZKAuth SDK
        api_key = getattr(settings, 'ZKAUTH_API_KEY')
        base_url = getattr(settings, 'ZKAUTH_BASE_URL', 'https://zkauth-engine.vercel.app')
        sdk = ZKAuthSDK(api_key, base_url)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            result = loop.run_until_complete(sdk.sign_up(email, password, metadata))

            if result.success:
                # Store user session
                request.session['zkauth_token'] = result.token
                request.session['zkauth_user'] = {
                    'id': result.user.id,
                    'email': result.user.email
                }

                return JsonResponse({
                    'success': True,
                    'user': {
                        'id': result.user.id,
                        'email': result.user.email
                    }
                })
            else:
                return JsonResponse({'error': result.error}, status=400)

        finally:
            loop.run_until_complete(sdk.close())
            loop.close()

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def zkauth_logout(request):
    """Handle ZKAuth logout"""
    try:
        token = request.session.get('zkauth_token')
        if token:
            # Use ZKAuth SDK to sign out
            api_key = getattr(settings, 'ZKAUTH_API_KEY')
            base_url = getattr(settings, 'ZKAUTH_BASE_URL', 'https://zkauth-engine.vercel.app')
            sdk = ZKAuthSDK(api_key, base_url)

            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

            try:
                loop.run_until_complete(sdk.sign_out())
            finally:
                loop.run_until_complete(sdk.close())
                loop.close()

        # Clear session
        request.session.flush()

        return JsonResponse({'success': True})

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def zkauth_required(view_func):
    """Decorator to require ZKAuth authentication"""
    def wrapper(request, *args, **kwargs):
        token = request.session.get('zkauth_token')
        if not token:
            return JsonResponse({'error': 'Authentication required'}, status=401)

        # Verify token
        api_key = getattr(settings, 'ZKAUTH_API_KEY')
        base_url = getattr(settings, 'ZKAUTH_BASE_URL', 'https://zkauth-engine.vercel.app')
        sdk = ZKAuthSDK(api_key, base_url)

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        try:
            is_valid = loop.run_until_complete(sdk.verify_token(token))
            if not is_valid:
                return JsonResponse({'error': 'Invalid token'}, status=401)
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=500)
        finally:
            loop.run_until_complete(sdk.close())
            loop.close()

        return view_func(request, *args, **kwargs)

    return wrapper
