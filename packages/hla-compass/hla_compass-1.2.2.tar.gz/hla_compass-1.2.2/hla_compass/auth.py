"""Authentication management for HLA-Compass SDK"""

import json
import os
import requests
import logging
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from .config import Config


logger = logging.getLogger(__name__)


class AuthError(Exception):
    """Authentication error"""
    pass


class Auth:
    """Handle authentication with HLA-Compass API"""
    
    def __init__(self):
        """Initialize auth manager"""
        self.config = Config()
        self.credentials_path = self.config.get_credentials_path()
    
    def login(self, email: str, password: str, environment: str = None) -> Dict[str, Any]:
        """
        Login to HLA-Compass API
        
        Args:
            email: User email
            password: User password
            environment: Target environment (dev/staging/prod)
            
        Returns:
            Authentication response with tokens
            
        Raises:
            AuthError: If login fails
        """
        # Set environment if provided
        if environment:
            os.environ['HLA_ENV'] = environment
            self.config = Config()  # Reload config with new environment
        
        endpoint = f"{self.config.get_api_endpoint()}/v1/auth/login"
        
        try:
            response = requests.post(
                endpoint,
                json={'email': email, 'password': password},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                # Handle both response formats:
                # 1. Direct token response (new format)
                # 2. Wrapped response with success/data fields (legacy format)
                if 'access_token' in data:
                    # Direct token response
                    self._save_credentials(data)
                    return data
                elif data.get('success') and 'data' in data:
                    # Legacy wrapped response
                    self._save_credentials(data['data'])
                    return data['data']
                else:
                    raise AuthError(data.get('error', {}).get('message', 'Login failed'))
            else:
                # Handle non-JSON error responses gracefully
                try:
                    error_data = response.json() if response.text else {}
                    msg = error_data.get('error', {}).get('message', f'Login failed with status {response.status_code}')
                except (json.JSONDecodeError, ValueError):
                    msg = response.text or f'Login failed with status {response.status_code}'
                raise AuthError(msg)
                
        except requests.RequestException as e:
            raise AuthError(f"Network error during login: {str(e)}")
    
    def developer_register(self, email: str, name: str) -> Dict[str, Any]:
        """
        Register as a developer
        
        Args:
            email: Developer email
            name: Developer name
            
        Returns:
            Registration response with temporary credentials
            
        Raises:
            AuthError: If registration fails
        """
        endpoint = f"{self.config.get_api_endpoint()}/v1/auth/developer-register"
        
        try:
            response = requests.post(
                endpoint,
                json={'email': email, 'name': name},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    return data['data']
                else:
                    raise AuthError(data.get('error', {}).get('message', 'Registration failed'))
            else:
                # Handle non-JSON error responses gracefully
                try:
                    error_data = response.json() if response.text else {}
                    msg = error_data.get('error', {}).get('message', f'Registration failed with status {response.status_code}')
                except (json.JSONDecodeError, ValueError):
                    msg = response.text or f'Registration failed with status {response.status_code}'
                raise AuthError(msg)
                
        except requests.RequestException as e:
            raise AuthError(f"Network error during registration: {str(e)}")
    
    def register(self, email: str, password: str, name: str, organization: str = None, environment: str = None) -> bool:
        """
        Register a new user account
        
        Args:
            email: User email
            password: User password
            name: User's full name
            organization: Organization name (optional)
            environment: Target environment (dev/staging/prod)
            
        Returns:
            True if registration successful
            
        Raises:
            AuthError: If registration fails
        """
        # Set environment if provided
        if environment:
            os.environ['HLA_ENV'] = environment
            self.config = Config()
        
        # For now, use developer registration endpoint
        # TODO: Implement full user registration when available
        try:
            result = self.developer_register(email, name)
            if result:
                return True
            return False
        except AuthError:
            raise
        except Exception as e:
            raise AuthError(f"Registration failed: {str(e)}")
    
    def is_authenticated(self) -> bool:
        """Check if user is currently authenticated"""
        return self.get_access_token() is not None
    
    def logout(self):
        """Logout and clear stored credentials"""
        if self.credentials_path.exists():
            self.credentials_path.unlink()
    
    def refresh_token(self) -> Optional[str]:
        """
        Refresh access token using refresh token
        
        Returns:
            New access token or None if refresh fails
        """
        if not self.credentials_path.exists():
            return None
        
        try:
            with open(self.credentials_path) as f:
                creds = json.load(f)
            
            refresh_token = creds.get('refresh_token')
            if not refresh_token:
                return None
            
            endpoint = f"{self.config.get_api_endpoint()}/v1/auth/refresh"
            response = requests.post(
                endpoint,
                json={'refresh_token': refresh_token},
                headers={'Content-Type': 'application/json'}
            )
            
            if response.status_code == 200:
                data = response.json()
                if data.get('success') and 'data' in data:
                    self._save_credentials(data['data'])
                    return data['data'].get('access_token')
        except (json.JSONDecodeError, KeyError, ValueError):
            # Token file corrupted or invalid format
            pass
        
        return None
    
    def get_access_token(self) -> Optional[str]:
        """
        Get current access token, refreshing if needed
        
        Returns:
            Valid access token or None
        """
        if not self.credentials_path.exists():
            return None
        
        try:
            with open(self.credentials_path) as f:
                creds = json.load(f)
            
            # Check if token is expired
            expires_at = creds.get('expires_at')
            if expires_at:
                expires = datetime.fromisoformat(expires_at)
                if expires <= datetime.now():
                    # Token expired, try to refresh
                    return self.refresh_token()
            
            return creds.get('access_token')
        except (json.JSONDecodeError, KeyError, ValueError) as e:
            # Credential file is corrupted, remove it and return None
            logger.warning(f"Credential file corrupted: {e}. Removing corrupted file.")
            try:
                self.credentials_path.unlink()
            except:
                pass
            return None
        except FileNotFoundError:
            return None
    
    def get_headers(self) -> Dict[str, str]:
        """
        Get authorization headers for API requests
        
        Returns:
            Headers dict with authorization token
        """
        token = self.get_access_token()
        headers = {'Content-Type': 'application/json'}
        
        if token:
            headers['Authorization'] = f'Bearer {token}'
        
        return headers
    
    def _save_credentials(self, data: Dict[str, Any]):
        """Save credentials to file"""
        # Calculate expiration time
        expires_in = data.get('expires_in', 3600)
        expires_at = datetime.now() + timedelta(seconds=expires_in)
        
        credentials = {
            'access_token': data.get('access_token'),
            'refresh_token': data.get('refresh_token'),
            'expires_at': expires_at.isoformat(),
            'environment': self.config.get_environment()
        }
        
        # Ensure directory exists
        self.credentials_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Save credentials
        with open(self.credentials_path, 'w') as f:
            json.dump(credentials, f, indent=2)
        
        # Secure the file
        self.credentials_path.chmod(0o600)