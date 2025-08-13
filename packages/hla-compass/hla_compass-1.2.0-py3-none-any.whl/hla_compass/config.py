"""Configuration management for HLA-Compass SDK"""

import os
from pathlib import Path
from typing import Optional

class Config:
    """SDK configuration management"""
    
    # API endpoints by environment (base URLs without version prefix)
    API_ENDPOINTS = {
        'dev': 'https://x2eatai82b.execute-api.eu-central-1.amazonaws.com/dev',
        'staging': 'https://api.hla-compass.com/staging',
        'prod': 'https://api.hla-compass.com'  # Fixed: removed /v1 to avoid duplication
    }
    
    @classmethod
    def get_environment(cls) -> str:
        """Get current environment (dev/staging/prod)
        
        Precedence: HLA_COMPASS_ENV > HLA_ENV > 'dev'
        """
        return os.getenv('HLA_COMPASS_ENV') or os.getenv('HLA_ENV', 'dev')
    
    @classmethod
    def get_api_endpoint(cls) -> str:
        """Get API endpoint for current environment"""
        env = cls.get_environment()
        return cls.API_ENDPOINTS.get(env, cls.API_ENDPOINTS['dev'])
    
    @classmethod
    def get_config_dir(cls) -> Path:
        """Get configuration directory path"""
        # Honor HLA_COMPASS_CONFIG_DIR environment variable
        config_dir_str = os.getenv('HLA_COMPASS_CONFIG_DIR')
        if config_dir_str:
            config_dir = Path(config_dir_str)
        else:
            config_dir = Path.home() / '.hla-compass'
        
        config_dir.mkdir(parents=True, exist_ok=True)
        return config_dir
    
    @classmethod
    def get_credentials_path(cls) -> Path:
        """Get path to credentials file"""
        return cls.get_config_dir() / 'credentials.json'
    
    @classmethod
    def get_config_path(cls) -> Path:
        """Get path to config file"""
        return cls.get_config_dir() / 'config.json'
    
    @classmethod
    def get_api_key(cls) -> Optional[str]:
        """Get API key from environment"""
        return os.getenv('HLA_API_KEY')
    
    @classmethod
    def get_access_token(cls) -> Optional[str]:
        """Get access token from credentials file or environment"""
        # First check environment
        token = os.getenv('HLA_ACCESS_TOKEN')
        if token:
            return token
        
        # Then check credentials file
        creds_path = cls.get_credentials_path()
        if creds_path.exists():
            import json
            try:
                with open(creds_path) as f:
                    creds = json.load(f)
                    return creds.get('access_token')
            except:
                pass
        
        return None
    
    @classmethod
    def is_authenticated(cls) -> bool:
        """Check if user is authenticated"""
        return cls.get_access_token() is not None