"""
Browser-based authentication for ivybloom CLI
Similar to GitHub CLI and Supabase CLI authentication flows
"""

import webbrowser
import http.server
import socketserver
import urllib.parse
import threading
import time
import secrets
import hashlib
import base64
from typing import Optional, Dict, Any
from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from .colors import get_console, print_success, print_error, print_info
from .config import Config

console = get_console()

class AuthCallbackHandler(http.server.SimpleHTTPRequestHandler):
    """Handle OAuth callback from browser"""
    
    def __init__(self, *args, auth_server=None, **kwargs):
        self.auth_server = auth_server
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET request from OAuth callback"""
        if self.path.startswith('/auth/callback'):
            # Parse query parameters
            parsed_url = urllib.parse.urlparse(self.path)
            params = urllib.parse.parse_qs(parsed_url.query)
            
            # Extract authorization code or error
            if 'code' in params:
                self.auth_server.auth_code = params['code'][0]
                self.send_success_response()
            elif 'error' in params:
                self.auth_server.auth_error = params['error'][0]
                self.send_error_response(params.get('error_description', ['Unknown error'])[0])
            else:
                self.send_error_response("No authorization code received")
        else:
            self.send_error_response("Invalid callback path")
    
    def send_success_response(self):
        """Send success response to browser"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        success_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>ivybloom CLI - Authentication Successful</title>
            <style>
                body { 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    min-height: 100vh; 
                    margin: 0; 
                    background: linear-gradient(135deg, #8B7355, #A0956B, #6B8E23);
                }
                .container { 
                    background: white; 
                    padding: 2rem; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    text-align: center; 
                    max-width: 400px;
                }
                .success-icon { 
                    font-size: 3rem; 
                    color: #6B8E23; 
                    margin-bottom: 1rem; 
                }
                .title { 
                    color: #8B7355; 
                    font-size: 1.5rem; 
                    margin-bottom: 1rem; 
                }
                .message { 
                    color: #666; 
                    margin-bottom: 2rem; 
                }
                .ivy-leaf { 
                    color: #6B8E23; 
                    font-size: 2rem; 
                    margin: 1rem 0; 
                }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="success-icon">✅</div>
                <div class="ivy-leaf">🌿</div>
                <h1 class="title">Authentication Successful!</h1>
                <p class="message">You have successfully authenticated with ivybloom CLI. You can now close this window and return to your terminal.</p>
                <p style="color: #A0956B; font-size: 0.9rem;">ivybloom CLI - Computational Biology & Drug Discovery</p>
            </div>
            <script>
                // Auto-close window after 3 seconds
                setTimeout(() => {
                    window.close();
                }, 3000);
            </script>
        </body>
        </html>
        """
        self.wfile.write(success_html.encode())
    
    def send_error_response(self, error_message):
        """Send error response to browser"""
        self.send_response(400)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        error_html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>ivybloom CLI - Authentication Error</title>
            <style>
                body {{ 
                    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
                    display: flex; 
                    align-items: center; 
                    justify-content: center; 
                    min-height: 100vh; 
                    margin: 0; 
                    background: linear-gradient(135deg, #8B7355, #A0956B, #CD853F);
                }}
                .container {{ 
                    background: white; 
                    padding: 2rem; 
                    border-radius: 12px; 
                    box-shadow: 0 4px 20px rgba(0,0,0,0.1);
                    text-align: center; 
                    max-width: 400px;
                }}
                .error-icon {{ 
                    font-size: 3rem; 
                    color: #CD853F; 
                    margin-bottom: 1rem; 
                }}
                .title {{ 
                    color: #8B7355; 
                    font-size: 1.5rem; 
                    margin-bottom: 1rem; 
                }}
                .message {{ 
                    color: #666; 
                    margin-bottom: 2rem; 
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="error-icon">❌</div>
                <h1 class="title">Authentication Failed</h1>
                <p class="message">{error_message}</p>
                <p style="color: #A0956B; font-size: 0.9rem;">Please try again in your terminal.</p>
            </div>
        </body>
        </html>
        """
        self.wfile.write(error_html.encode())
    
    def log_message(self, format, *args):
        """Suppress HTTP server logs"""
        pass

class BrowserAuthServer:
    """Local HTTP server for handling OAuth callbacks"""
    
    def __init__(self, port: int = 8080):
        self.port = port
        self.auth_code: Optional[str] = None
        self.auth_error: Optional[str] = None
        self.server: Optional[socketserver.TCPServer] = None
        self.server_thread: Optional[threading.Thread] = None
    
    def start(self):
        """Start the callback server"""
        def handler(*args, **kwargs):
            return AuthCallbackHandler(*args, auth_server=self, **kwargs)
        
        self.server = socketserver.TCPServer(("localhost", self.port), handler)
        self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.server_thread.start()
    
    def stop(self):
        """Stop the callback server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
        if self.server_thread:
            self.server_thread.join(timeout=1)
    
    def wait_for_callback(self, timeout: int = 300) -> tuple[Optional[str], Optional[str]]:
        """Wait for OAuth callback with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            if self.auth_code:
                return self.auth_code, None
            elif self.auth_error:
                return None, self.auth_error
            time.sleep(0.5)
        
        return None, "Authentication timeout"

def generate_pkce_pair() -> tuple[str, str]:
    """Generate PKCE code verifier and challenge"""
    # Generate code verifier
    code_verifier = base64.urlsafe_b64encode(secrets.token_bytes(32)).decode('utf-8')
    code_verifier = code_verifier.rstrip('=')
    
    # Generate code challenge
    code_challenge = hashlib.sha256(code_verifier.encode('utf-8')).digest()
    code_challenge = base64.urlsafe_b64encode(code_challenge).decode('utf-8')
    code_challenge = code_challenge.rstrip('=')
    
    return code_verifier, code_challenge

def browser_login(api_url: str, port: int = 8080) -> Dict[str, Any]:
    """
    Initiate browser-based OAuth login flow
    
    Returns:
        Dict containing auth tokens or error information
    """
    
    # Generate PKCE parameters
    state = secrets.token_urlsafe(32)
    code_verifier, code_challenge = generate_pkce_pair()
    
    # Start local callback server
    auth_server = BrowserAuthServer(port)
    
    try:
        auth_server.start()
        
        # Build OAuth URL
        callback_url = f"http://localhost:{port}/auth/callback"
        
        oauth_params = {
            'response_type': 'code',
            'client_id': 'ivybloom-cli',
            'redirect_uri': callback_url,
            'scope': 'read write',
            'state': state,
            'code_challenge': code_challenge,
            'code_challenge_method': 'S256'
        }
        
        # Normalize base URL to avoid double slashes
        base_url = api_url.rstrip("/")
        auth_url = f"{base_url}/auth/oauth/authorize?" + urllib.parse.urlencode(oauth_params)
        
        # Display authentication instructions
        console.print()
        panel = Panel(
            Text.assemble(
                "🌿 ", ("ivybloom CLI Authentication", "welcome.text"), "\n\n",
                "We'll open your browser to authenticate with ivybloom.\n",
                "If the browser doesn't open automatically, visit:\n\n",
                (auth_url, "cli.accent"), "\n\n",
                "Press ", ("Ctrl+C", "cli.bright"), " to cancel authentication."
            ),
            title="🔐 Browser Authentication",
            title_align="center",
            border_style="welcome.border",
            padding=(1, 2)
        )
        console.print(panel)
        console.print()
        
        # Open browser
        print_info("Opening browser for authentication...")
        try:
            webbrowser.open(auth_url)
            print_success("Browser opened successfully")
        except Exception as e:
            print_error(f"Failed to open browser: {e}")
            console.print(f"Please manually visit: {auth_url}")
        
        console.print()
        print_info("Waiting for authentication in browser...")
        
        # Wait for callback
        auth_code, error = auth_server.wait_for_callback()
        
        if error:
            return {"error": error}
        
        if not auth_code:
            return {"error": "No authorization code received"}
        
        # Exchange code for tokens
        token_data = exchange_code_for_tokens(
            base_url, auth_code, code_verifier, callback_url
        )
        
        return token_data
        
    except KeyboardInterrupt:
        print_error("Authentication cancelled by user")
        return {"error": "Authentication cancelled"}
    
    except Exception as e:
        print_error(f"Authentication error: {e}")
        return {"error": str(e)}
    
    finally:
        auth_server.stop()

def exchange_code_for_tokens(
    api_url: str, 
    auth_code: str, 
    code_verifier: str, 
    redirect_uri: str
) -> Dict[str, Any]:
    """Exchange authorization code for access tokens"""
    
    import httpx
    
    token_url = f"{api_url.rstrip('/')}/auth/oauth/token"
    
    token_data = {
        'grant_type': 'authorization_code',
        'client_id': 'ivybloom-cli',
        'code': auth_code,
        'redirect_uri': redirect_uri,
        'code_verifier': code_verifier
    }
    
    try:
        with httpx.Client() as client:
            response = client.post(token_url, data=token_data)
            
            if response.status_code == 200:
                tokens = response.json()
                return {
                    "access_token": tokens.get("access_token"),
                    "refresh_token": tokens.get("refresh_token"),
                    "expires_in": tokens.get("expires_in"),
                    "token_type": tokens.get("token_type", "Bearer")
                }
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                return {
                    "error": error_data.get("error", f"HTTP {response.status_code}"),
                    "error_description": error_data.get("error_description", response.text)
                }
                
    except Exception as e:
        return {"error": f"Token exchange failed: {e}"}

def device_flow_login(api_url: str) -> Dict[str, Any]:
    """
    Alternative device flow authentication (like GitHub CLI)
    For environments where browser opening isn't possible
    """
    
    import httpx
    
    try:
        # Start device flow
        device_url = f"{api_url.rstrip('/')}/auth/device/code"
        
        with httpx.Client() as client:
            response = client.post(device_url, data={
                'client_id': 'ivybloom-cli',
                'scope': 'read write'
            })
            
            if response.status_code != 200:
                return {"error": "Failed to start device flow"}
            
            device_data = response.json()
            
            # Display user code
            console.print()
            panel = Panel(
                Text.assemble(
                    "🌿 ", ("IvyBloom CLI Authentication", "welcome.text"), "\n\n",
                    "Visit: ", (device_data['verification_uri'], "cli.bright"), "\n",
                    "Enter code: ", (device_data['user_code'], "cli.accent"), "\n\n",
                    f"Code expires in {device_data.get('expires_in', 900)} seconds"
                ),
                title="🔐 Device Authentication",
                title_align="center", 
                border_style="welcome.border",
                padding=(1, 2)
            )
            console.print(panel)
            console.print()
            
            # Poll for completion
            return poll_device_flow(api_url, device_data)
            
    except Exception as e:
        return {"error": f"Device flow failed: {e}"}

def poll_device_flow(api_url: str, device_data: Dict[str, Any]) -> Dict[str, Any]:
    """Poll device flow until completion"""
    
    import httpx
    
    token_url = f"{api_url.rstrip('/')}/auth/oauth/token"
    interval = device_data.get('interval', 5)
    expires_in = device_data.get('expires_in', 900)
    
    start_time = time.time()
    
    with httpx.Client() as client:
        while time.time() - start_time < expires_in:
            try:
                response = client.post(token_url, data={
                    'grant_type': 'urn:ietf:params:oauth:grant-type:device_code',
                    'client_id': 'ivybloom-cli',
                    'device_code': device_data['device_code']
                })
                
                if response.status_code == 200:
                    tokens = response.json()
                    return {
                        "access_token": tokens.get("access_token"),
                        "refresh_token": tokens.get("refresh_token"),
                        "expires_in": tokens.get("expires_in"),
                        "token_type": tokens.get("token_type", "Bearer")
                    }
                
                elif response.status_code == 400:
                    error_data = response.json()
                    error = error_data.get("error")
                    
                    if error == "authorization_pending":
                        # Still waiting for user authorization
                        print(".", end="", flush=True)
                    elif error == "slow_down":
                        # Increase polling interval
                        interval += 5
                    elif error in ["access_denied", "expired_token"]:
                        return {"error": error_data.get("error_description", error)}
                
                time.sleep(interval)
                
            except KeyboardInterrupt:
                return {"error": "Authentication cancelled"}
            except Exception as e:
                return {"error": f"Polling failed: {e}"}
    
    return {"error": "Device flow timeout"}