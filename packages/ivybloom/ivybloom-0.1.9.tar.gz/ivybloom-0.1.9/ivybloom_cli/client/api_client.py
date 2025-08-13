"""
API client for ivybloom CLI
"""

import httpx
import json
from typing import Dict, Any, Optional, List
from rich.console import Console

from ..utils.config import Config
from ..utils.auth import AuthManager
from ..utils.colors import get_console, print_error

console = get_console()

class IvyBloomAPIClient:
    """HTTP client for ivybloom API"""
    
    def __init__(self, config: Config, auth_manager: AuthManager):
        self.config = config
        self.auth_manager = auth_manager
        # Resolve base URL via config with env var overrides
        self.base_url = config.get_api_url()
        self.timeout = config.get('timeout', 30)
        
        # Initialize HTTP client
        self.client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers=self._get_default_headers()
        )
    
    def _ensure_authenticated(self) -> None:
        """Ensure user is authenticated before making requests"""
        if not self.auth_manager.is_authenticated():
            raise Exception(
                "Authentication required. Please run 'ivybloom auth login' first.\n"
                "You can create an API key at: https://ivybiosciences.com/settings/api-keys"
            )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get default headers for requests"""
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "ivybloom-cli/0.1.7"
        }
        
        # Add authentication headers
        auth_headers = self.auth_manager.get_auth_headers()
        headers.update(auth_headers)
        # Include client identifier for backend linking and analytics
        try:
            client_id = self.config.get_or_create_client_id()
            headers["X-IvyBloom-Client"] = client_id
        except Exception:
            pass
        
        return headers
    
    def _make_request(self, method: str, endpoint: str, **kwargs) -> httpx.Response:
        """Make HTTP request with error handling"""
        try:
            # Ensure endpoint joins correctly with base_url
            path = endpoint if endpoint.startswith("/") else f"/{endpoint}"
            response = self.client.request(method, path, **kwargs)
            
            if self.config.get('debug'):
                console.print(f"[dim]{method} {endpoint} -> {response.status_code}[/dim]")
            
            return response
        except httpx.TimeoutException:
            raise Exception("Request timed out. Check your network and try again.")
        except httpx.ConnectError:
            raise Exception("Could not connect to API server. Verify IVY_ORCHESTRATOR_URL and your network.")
        except Exception as e:
            raise Exception(f"Request failed: {e}")
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """Make GET request"""
        self._ensure_authenticated()
        response = self._make_request("GET", endpoint, params=params)
        
        if response.status_code == 401:
            try:
                error_data = response.json()
                detail = error_data.get("code")
            except Exception:
                detail = None
            if detail == "CLI_CLIENT_UNLINKED":
                raise Exception("❌ CLI not linked to your account. Run 'ivybloom auth link' to link this CLI installation.")
            raise Exception("❌ Authentication failed. Please run 'ivybloom auth login' or check your API key.")
        elif response.status_code == 403:
            raise Exception("❌ Access denied. You don't have permission for this resource.")
        elif response.status_code == 404:
            raise Exception("❌ Resource not found.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', error_data.get('message', f'HTTP {response.status_code}'))
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"❌ API error: {error_msg}")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"data": response.text}
    
    def post(self, endpoint: str, data: Optional[Dict] = None, json_data: Optional[Dict] = None) -> Dict[str, Any]:
        """Make POST request"""
        self._ensure_authenticated()
        kwargs = {}
        if data:
            kwargs['data'] = data
        if json_data:
            kwargs['json'] = json_data
        
        response = self._make_request("POST", endpoint, **kwargs)
        
        if response.status_code == 401:
            try:
                detail = response.json().get("code")
            except Exception:
                detail = None
            if detail == "CLI_CLIENT_UNLINKED":
                raise Exception("Authentication required. Run 'ivybloom auth link' to link this CLI and retry.")
            raise Exception("Authentication failed. Please check your API key or login status.")
        elif response.status_code == 403:
            raise Exception("Access denied. You don't have permission for this resource.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"API error: {error_msg}")
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"data": response.text}
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """Make DELETE request"""
        self._ensure_authenticated()
        response = self._make_request("DELETE", endpoint)
        
        if response.status_code == 401:
            try:
                detail = response.json().get("code")
            except Exception:
                detail = None
            if detail == "CLI_CLIENT_UNLINKED":
                raise Exception("Authentication required. Run 'ivybloom auth link' to link this CLI and retry.")
            raise Exception("Authentication failed. Please check your API key or login status.")
        elif response.status_code == 403:
            raise Exception("Access denied. You don't have permission for this resource.")
        elif response.status_code == 404:
            raise Exception("Resource not found.")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_msg = error_data.get('detail', f'HTTP {response.status_code}')
            except:
                error_msg = f'HTTP {response.status_code}'
            raise Exception(f"API error: {error_msg}")
        
        if response.status_code == 204:
            return {"success": True}
        
        try:
            return response.json()
        except json.JSONDecodeError:
            return {"success": True}
    
    # CLI-specific API methods
    def list_tools(self) -> List[str]:
        """List available tools"""
        data = self.get("/cli/tools")
        return data
    
    def get_tool_schema(self, tool_name: str) -> Dict[str, Any]:
        """Get schema for a specific tool"""
        return self.get(f"/cli/tools/{tool_name}/schema")
    
    def create_job(self, job_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new job"""
        # Ensure the request matches the API specification
        payload = {
            "tool_name": job_request.get("tool_name"),  # CLI uses tool_name
            "parameters": job_request.get("parameters", {}),
            "project_id": job_request.get("project_id"),
            "job_title": job_request.get("job_title"),
            "wait_for_completion": job_request.get("wait_for_completion", False)
        }
        
        # Remove None values to keep payload clean
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return self.post("/cli/jobs", json_data=payload)
    
    def get_job_status(self, job_id: str, include_logs: bool = False) -> Dict[str, Any]:
        """Get job status"""
        params = {"include_logs": include_logs} if include_logs else None
        response = self.get(f"/cli/jobs/{job_id}", params=params)
        
        # Map database field names to CLI-expected field names for backward compatibility
        if response and 'id' in response:
            response['job_id'] = response['id']  # Map id -> job_id for CLI compatibility
        if response and 'job_type' in response:
            response['tool_name'] = response['job_type']  # Map job_type -> tool_name for CLI
        if response and 'progress_percent' in response:
            response['progress_percentage'] = response['progress_percent']  # Map progress_percent -> progress_percentage
            
        return response
    
    def get_job_results(self, job_id: str, format: str = "json") -> Dict[str, Any]:
        """Get job results"""
        params = {"format": format}
        response = self.get(f"/cli/jobs/{job_id}/results", params=params)
        
        # Map database field names for consistency
        if response and 'id' in response:
            response['job_id'] = response['id']
        if response and 'job_type' in response:
            response['tool_name'] = response['job_type']
            
        return response
    
    def cancel_job(self, job_id: str) -> Dict[str, Any]:
        """Cancel a job"""
        return self.delete(f"/cli/jobs/{job_id}")
    
    def get_job_download_urls(self, job_id: str, artifact_type: str = None) -> Dict[str, Any]:
        """Get presigned download URLs for job artifacts"""
        params = {'job_id': job_id}
        if artifact_type:
            params['artifact_type'] = artifact_type
        
        return self.get("/cli/download", params=params)
    
    def list_jobs(self, **filters) -> List[Dict[str, Any]]:
        """List jobs with optional filters"""
        # Map CLI parameter names to API parameter names
        params = {}
        if 'project_id' in filters and filters['project_id']:
            params['project_id'] = filters['project_id']
        if 'status' in filters and filters['status']:
            params['status'] = filters['status']
        if 'tool_name' in filters and filters['tool_name']:
            params['job_type'] = filters['tool_name']  # Map tool_name to job_type
        if 'created_after' in filters and filters['created_after']:
            params['created_after'] = filters['created_after']
        if 'created_before' in filters and filters['created_before']:
            params['created_before'] = filters['created_before']
        if 'limit' in filters and filters['limit']:
            params['limit'] = filters['limit']
        if 'offset' in filters and filters['offset']:
            params['offset'] = filters['offset']
        
        return self.get("/cli/jobs", params=params)
    
    def list_projects(self) -> List[Dict[str, Any]]:
        """List user's projects"""
        return self.get("/cli/projects")
    
    def get_project(self, project_id: str) -> Dict[str, Any]:
        """Get project details"""
        return self.get(f"/cli/projects/{project_id}")
    
    def list_project_jobs(self, project_id: str) -> List[Dict[str, Any]]:
        """List jobs for a specific project"""
        return self.get(f"/cli/projects/{project_id}/jobs")
    
    def get_account_info(self) -> Dict[str, Any]:
        """Get account information"""
        return self.get("/cli/account")
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return self.get("/cli/usage")
    
    def close(self):
        """Close the HTTP client"""
        self.client.close()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()