"""
Secure logging utilities to prevent sensitive information exposure
"""
import os
import logging
from typing import Any, Optional

def secure_log(level: str, message: str, sensitive_data: Optional[Any] = None, environment: Optional[str] = None) -> None:
    """
    Log messages securely, hiding sensitive information in production
    
    Args:
        level: Log level (DEBUG, INFO, WARNING, ERROR)
        message: Log message
        sensitive_data: Optional sensitive data to log (only in development)
        environment: Environment override (defaults to ENVIRONMENT env var)
    """
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')
    
    # In production, never log sensitive data
    if environment == 'production':
        if sensitive_data is not None:
            # Replace sensitive data with placeholder
            message = message.replace(str(sensitive_data), '[REDACTED]')
        print(f"[{level}] {message}")
    else:
        # In development, log everything
        if sensitive_data is not None:
            print(f"[{level}] {message}: {sensitive_data}")
        else:
            print(f"[{level}] {message}")

def secure_print_api_key_status(key_name: str, key_value: Optional[str], environment: Optional[str] = None) -> None:
    """
    Securely print API key status without exposing the actual key
    
    Args:
        key_name: Name of the API key
        key_value: The actual API key value
        environment: Environment override
    """
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')
    
    if key_value:
        print(f"✅ {key_name}: Set")
    else:
        print(f"❌ {key_name}: Missing")

def secure_print_database_url(db_url: str, environment: Optional[str] = None) -> None:
    """
    Securely print database URL without exposing credentials
    
    Args:
        db_url: Database connection URL
        environment: Environment override
    """
    if environment is None:
        environment = os.getenv('ENVIRONMENT', 'development')
    
    # Always show minimal information regardless of environment
    print("✅ Database: Connected")
