"""Configuration for darkfield CLI"""

import os
import keyring

# API Configuration
# Default API base (Modal gateway). Override via env for staging/prod domains
DARKFIELD_API_URL = os.getenv(
    "DARKFIELD_API_URL",
    "https://dyllonj96--darkfield-api-gateway-v2-fastapi-app.modal.run",
)
DARKFIELD_WEB_URL = os.getenv("DARKFIELD_WEB_URL", "https://darkfield.ai")

# For local development
if os.getenv("DARKFIELD_ENV") == "development":
    DARKFIELD_API_URL = "http://localhost:8000"
    DARKFIELD_WEB_URL = "http://localhost:3000"

# CLI Configuration
DEFAULT_OUTPUT_FORMAT = os.getenv("DARKFIELD_OUTPUT_FORMAT", "table")
DISABLE_ANALYTICS = os.getenv("DARKFIELD_NO_ANALYTICS", "false").lower() == "true"

# Authentication
def get_api_key():
    """Get API key from environment or saved credentials"""
    # First check environment variable
    api_key = os.environ.get('DARKFIELD_API_KEY')
    if api_key:
        return api_key
    
    # Then check saved credentials
    try:
        return keyring.get_password("darkfield-cli", "api_key")
    except:
        return None

def get_user_email():
    """Get user email from environment or saved credentials"""
    # Check environment variable
    email = os.environ.get('DARKFIELD_USER_EMAIL')
    if email:
        return email
    
    # Check saved credentials
    try:
        return keyring.get_password("darkfield-cli", "user_email")
    except:
        return None