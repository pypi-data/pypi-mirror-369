"""
Authentication management for IvyBloom CLI
"""

import json
import keyring
from pathlib import Path
from typing import Optional, Dict, Any
from rich.console import Console
from rich.prompt import Prompt

from .config import Config
from .colors import get_console, print_success, print_error, print_warning, print_info

console = get_console()

class AuthManager:
    """Manages authentication for IvyBloom CLI"""
    
    def __init__(self, config: Config):
        self.config = config
        self.service_name = "ivybloom-cli"
    
    def store_api_key(self, api_key: str, username: str = "default") -> None:
        """Store API key securely"""
        try:
            keyring.set_password(self.service_name, username, api_key)
            console.print("[green]API key stored securely[/green]")
        except Exception as e:
            # Fallback to file storage if keyring fails
            console.print(f"[yellow]Warning: Could not use secure storage ({e})[/yellow]")
            console.print("[yellow]Falling back to file storage[/yellow]")
            self._store_api_key_file(api_key)
    
    def get_api_key(self, username: str = "default") -> Optional[str]:
        """Retrieve stored API key"""
        try:
            api_key = keyring.get_password(self.service_name, username)
            if api_key:
                return api_key
        except Exception:
            pass
        
        # Fallback to file storage
        return self._get_api_key_file()
    
    def remove_api_key(self, username: str = "default") -> None:
        """Remove stored API key"""
        try:
            keyring.delete_password(self.service_name, username)
        except Exception:
            pass
        
        # Also remove from file storage
        self._remove_api_key_file()
        # Remove OAuth tokens as well
        self._remove_oauth_tokens()
        console.print("[green]Credentials removed[/green]")
    
    def store_oauth_tokens(self, tokens: Dict[str, Any]) -> None:
        """Store OAuth tokens securely"""
        try:
            # Store tokens in keyring
            tokens_json = json.dumps(tokens)
            keyring.set_password(self.service_name, "oauth_tokens", tokens_json)
            console.print("[green]OAuth tokens stored securely[/green]")
        except Exception as e:
            # Fallback to file storage
            console.print(f"[yellow]Warning: Could not use secure storage ({e})[/yellow]")
            console.print("[yellow]Falling back to file storage[/yellow]")
            self._store_oauth_tokens_file(tokens)
    
    def get_oauth_tokens(self) -> Optional[Dict[str, Any]]:
        """Retrieve stored OAuth tokens"""
        try:
            tokens_json = keyring.get_password(self.service_name, "oauth_tokens")
            if tokens_json:
                return json.loads(tokens_json)
        except Exception:
            pass
        
        # Fallback to file storage
        return self._get_oauth_tokens_file()
    
    def _store_oauth_tokens_file(self, tokens: Dict[str, Any]) -> None:
        """Store OAuth tokens in file (fallback)"""
        tokens_path = self.config.config_dir / "oauth_tokens.json"
        tokens_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(tokens_path, 'w') as f:
            json.dump(tokens, f)
        
        # Set restrictive permissions
        tokens_path.chmod(0o600)
    
    def _get_oauth_tokens_file(self) -> Optional[Dict[str, Any]]:
        """Get OAuth tokens from file (fallback)"""
        tokens_path = self.config.config_dir / "oauth_tokens.json"
        
        if tokens_path.exists():
            try:
                with open(tokens_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        
        return None
    
    def _remove_oauth_tokens(self) -> None:
        """Remove OAuth tokens"""
        try:
            keyring.delete_password(self.service_name, "oauth_tokens")
        except Exception:
            pass
        
        # Remove from file storage
        tokens_path = self.config.config_dir / "oauth_tokens.json"
        if tokens_path.exists():
            tokens_path.unlink()
    
    def _store_api_key_file(self, api_key: str) -> None:
        """Store API key in file (fallback)"""
        api_key_path = self.config.get_api_key_path()
        api_key_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Store with restricted permissions
        with open(api_key_path, 'w') as f:
            json.dump({"api_key": api_key}, f)
        
        # Set file permissions (Unix-like systems only)
        try:
            api_key_path.chmod(0o600)
        except Exception:
            pass
    
    def _get_api_key_file(self) -> Optional[str]:
        """Get API key from file (fallback)"""
        api_key_path = self.config.get_api_key_path()
        
        if api_key_path.exists():
            try:
                with open(api_key_path, 'r') as f:
                    data = json.load(f)
                    return data.get("api_key")
            except Exception:
                pass
        
        return None
    
    def _remove_api_key_file(self) -> None:
        """Remove API key file (fallback)"""
        api_key_path = self.config.get_api_key_path()
        
        if api_key_path.exists():
            try:
                api_key_path.unlink()
            except Exception:
                pass
    
    def store_auth_token(self, token: str) -> None:
        """Store authentication token (for Clerk JWT)"""
        auth_token_path = self.config.get_auth_token_path()
        auth_token_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(auth_token_path, 'w') as f:
            json.dump({"token": token, "type": "jwt"}, f)
        
        # Set file permissions
        try:
            auth_token_path.chmod(0o600)
        except Exception:
            pass
    
    def get_auth_token(self) -> Optional[str]:
        """Get stored authentication token"""
        auth_token_path = self.config.get_auth_token_path()
        
        if auth_token_path.exists():
            try:
                with open(auth_token_path, 'r') as f:
                    data = json.load(f)
                    return data.get("token")
            except Exception:
                pass
        
        return None
    
    def remove_auth_token(self) -> None:
        """Remove stored authentication token"""
        auth_token_path = self.config.get_auth_token_path()
        
        if auth_token_path.exists():
            try:
                auth_token_path.unlink()
            except Exception:
                pass
    
    def is_authenticated(self) -> bool:
        """Check if user is authenticated"""
        return self.get_api_key() is not None or self.get_oauth_tokens() is not None or self.get_auth_token() is not None
    
    def get_auth_headers(self) -> Dict[str, str]:
        """Get authentication headers for API requests"""
        headers = {}
        
        # Try OAuth tokens first
        oauth_tokens = self.get_oauth_tokens()
        if oauth_tokens and oauth_tokens.get('access_token'):
            token_type = oauth_tokens.get('token_type', 'Bearer')
            headers["Authorization"] = f"{token_type} {oauth_tokens['access_token']}"
            return headers
        
        # Try API key next
        api_key = self.get_api_key()
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
            return headers
        
        # Fall back to JWT token
        token = self.get_auth_token()
        if token:
            headers["Authorization"] = f"Bearer {token}"
            return headers
        
        return headers
    
    def prompt_for_api_key(self) -> Optional[str]:
        """Prompt user to enter API key"""
        console.print("\n[bold cyan]API Key Setup[/bold cyan]")
        console.print("You can create an API key at: https://platform.ivybiosciences.com/settings/api-keys")
        console.print()
        
        api_key = Prompt.ask(
            "Enter your API key",
            password=True,
            show_default=False
        )
        
        if api_key and api_key.strip():
            return api_key.strip()
        
        return None