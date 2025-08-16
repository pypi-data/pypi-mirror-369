"""
Schema loader utility for IvyBloom CLI tools.

This module provides functionality to load tool schemas from the authenticated API,
ensuring all schema access is properly gated through user authentication.
"""

from typing import Dict, Any, Optional, List

# Tool aliases mapping for UI compatibility
TOOL_ALIASES = {
    'proteinfolding': 'esmfold',
    'moleculardocking': 'diffdock', 
    'denovodesign': 'reinvent',
    'fragmentsearch': 'fragment_library',
    'aianalysis': 'biobert',
    'csp': 'xtalnet_csp',
    'polymorphscreening': 'xtalnet_csp'
}

class SchemaLoader:
    """Schema loader that retrieves tool schemas from authenticated API."""
    
    def __init__(self):
        self._schema_cache: Dict[str, Dict[str, Any]] = {}
    
    def resolve_tool_name(self, tool_name: str) -> str:
        """Resolve tool aliases to actual tool names."""
        return TOOL_ALIASES.get(tool_name.lower(), tool_name)
    
    def get_tool_schema(self, tool_name: str, api_client) -> Optional[Dict[str, Any]]:
        """Get schema information for a tool from the authenticated API.
        
        Args:
            tool_name: Name of the tool to get schema for
            api_client: Authenticated API client instance
            
        Returns:
            Schema data dictionary or None if not found
        """
        # Resolve aliases
        resolved_name = self.resolve_tool_name(tool_name)
        
        # Check cache
        cache_key = f"{resolved_name}"
        if cache_key in self._schema_cache:
            return self._schema_cache[cache_key]
        
        try:
            # Load schema from API
            schema_data = api_client.get_tool_schema(resolved_name)
            
            # Cache the result
            if schema_data:
                self._schema_cache[cache_key] = schema_data
            
            return schema_data
            
        except Exception as e:
            print(f"Warning: Could not load schema for {tool_name}: {e}")
            return None
    
    def get_available_tools(self, api_client, verbose: bool = False) -> List[Any]:
        """Get list of all available tools from the authenticated API.
        
        Args:
            api_client: Authenticated API client instance
            
        Returns:
            List of available tool names
        """
        try:
            tools_data = api_client.list_tools(verbose=verbose)
            if isinstance(tools_data, list):
                return tools_data
            elif isinstance(tools_data, dict) and 'tools' in tools_data:
                return tools_data['tools']
            else:
                return []
        except Exception as e:
            print(f"Warning: Could not load available tools: {e}")
            return []
    
    def clear_cache(self):
        """Clear the schema cache."""
        self._schema_cache.clear()

# Global schema loader instance
_schema_loader = SchemaLoader()

def get_tool_schema(tool_name: str, api_client) -> Optional[Dict[str, Any]]:
    """Get schema information for a tool using authenticated API.
    
    Args:
        tool_name: Name of the tool
        api_client: Authenticated API client instance
        
    Returns:
        Schema data dictionary or None if not found
    """
    return _schema_loader.get_tool_schema(tool_name, api_client)

def get_available_tools(api_client) -> List[str]:
    """Get list of available tools using authenticated API.
    
    Args:
        api_client: Authenticated API client instance
        
    Returns:
        List of available tool names
    """
    return _schema_loader.get_available_tools(api_client)

def resolve_tool_name(tool_name: str) -> str:
    """Resolve tool name aliases."""
    return _schema_loader.resolve_tool_name(tool_name)