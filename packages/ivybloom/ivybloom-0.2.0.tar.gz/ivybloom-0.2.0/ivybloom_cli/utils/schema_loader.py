"""
Schema loader utility for IvyBloom CLI tools.

This module provides functionality to load and parse comprehensive tool schemas
from the schemas/ directory, enabling rich CLI help and validation.
"""

import json
import inspect
from typing import Dict, Any, Optional, List, Type, Union
from pathlib import Path

try:
    from typing import get_origin, get_args
except ImportError:
    # Python < 3.8 compatibility
    def get_origin(tp):
        return getattr(tp, '__origin__', None)
    
    def get_args(tp):
        return getattr(tp, '__args__', ())

try:
    from pydantic import BaseModel, Field
    from pydantic.fields import FieldInfo
except ImportError:
    # Handle case where pydantic is not available
    BaseModel = object
    Field = None
    FieldInfo = object

# Tool name to schema mapping
TOOL_SCHEMA_MAPPING = {
    'esmfold': 'esmfold_schemas.ESMFoldInput',
    'diffdock': 'diffdock_schemas.DiffDockInput', 
    'reinvent': 'reinvent_schemas.ReinventInput',
    'blast': 'blast_schemas.BlastInput',
    'deepsol': 'deepsol_schemas.DeepsolInputSchema',
    'aizynthfinder': 'aizynthfinder_schemas.AizynthfinderInputSchema',
    'frogs': 'frogs_schemas.FrogsInputSchema',
    'graphsol': 'graphsol_schemas.GraphSolInput',
    'protox3': 'protox3_schemas.ProTox3Input',
    'admetlab3': 'admetlab3_schemas.ADMETLab3Input',
    'biobert': 'biobert_schemas.BioBERTInput',
    'zinc': 'zinc_schemas.ZincInput',
    'molport': 'molport_schemas.MolPortInput',
    'deeppurpose': 'deeppurpose_schemas.DeepPurposeInput',
    'fragment_library': 'fragment_library_schemas.FragmentLibraryInput',
    'fragment_growing': 'fragment_growing_schemas.FragmentGrowingInput',
    'pubchem': 'pubchem_schemas.PubChemInput',
    'xtalnet': 'xtalnet_schemas.XtalNetInput',
    'xtalnet_csp': 'xtalnet_schemas.PolymorphScreeningInput',
}

# Fields to exclude from CLI help (internal/system fields)
EXCLUDED_FIELDS = {
    'job_type',           # Internal job type identifier
    'job_title',          # Handled by CLI --job-title option
    'callback_url',       # Internal system field
    'user_id',           # Internal system field
    'task_id',           # Internal system field
    'job_id',            # Internal system field
    'parameters',        # Nested parameter container
    'config',            # Internal config field
    'result',            # Result field (not input)
    'status',            # Status field (not input)
    'created_at',        # Timestamp field
    'updated_at',        # Timestamp field
    'completed_at',      # Timestamp field
}

# Tool aliases mapping (from tools.py)
TOOL_ALIASES = {
    'proteinfolding': 'esmfold',
    'moleculardocking': 'diffdock', 
    'denovodesign': 'reinvent',
    'fragmentsearch': 'fragment_library',
    'aianalysis': 'biobert'
}

class SchemaFieldInfo:
    """Enhanced field information extracted from Pydantic schemas."""
    
    def __init__(self, name: str, field_info: FieldInfo, field_type: Any):
        self.name = name
        self.field_info = field_info
        self.field_type = field_type
        
    @property
    def description(self) -> str:
        """Get field description."""
        return getattr(self.field_info, 'description', None) or "No description available"
    
    @property
    def type_str(self) -> str:
        """Get human-readable type string."""
        return self._format_type(self.field_type)
    
    @property
    def default(self) -> Any:
        """Get default value."""
        if hasattr(self.field_info, 'default') and self.field_info.default is not ...:
            return self.field_info.default
        elif hasattr(self.field_info, 'default_factory') and self.field_info.default_factory is not None:
            return f"<factory: {self.field_info.default_factory.__name__}>"
        return None
    
    @property
    def is_required(self) -> bool:
        """Check if field is required."""
        has_default = hasattr(self.field_info, 'default') and self.field_info.default is not ...
        has_factory = hasattr(self.field_info, 'default_factory') and self.field_info.default_factory is not None
        return not (has_default or has_factory)
    
    @property
    def constraints(self) -> Dict[str, Any]:
        """Get field constraints (min, max, etc.)."""
        constraints = {}
        
        # Extract constraints from field_info - handle both v1 and v2
        constraint_attrs = ['ge', 'gt', 'le', 'lt', 'min_length', 'max_length', 'regex', 'pattern']
        
        for attr in constraint_attrs:
            if hasattr(self.field_info, attr):
                value = getattr(self.field_info, attr)
                if value is not None:
                    constraints[attr] = value
        
        # For Pydantic v2, also check constraints dict if it exists
        if hasattr(self.field_info, 'constraints') and self.field_info.constraints:
            constraints.update(self.field_info.constraints)
        
        return constraints
    
    def _format_type(self, type_hint: Any) -> str:
        """Format type hint as human-readable string."""
        if type_hint is None:
            return "Any"
        
        # Handle basic types
        if type_hint in (str, int, float, bool):
            return type_hint.__name__
        
        # Handle Optional[X] -> Union[X, None]
        origin = get_origin(type_hint)
        args = get_args(type_hint)
        
        if origin is type(None):
            return "None"
        elif origin in (list, List):
            if args:
                return f"List[{self._format_type(args[0])}]"
            return "List"
        elif origin is dict or origin is Dict:
            if len(args) == 2:
                return f"Dict[{self._format_type(args[0])}, {self._format_type(args[1])}]"
            return "Dict"
        elif origin is tuple:
            if args:
                return f"Tuple[{', '.join(self._format_type(arg) for arg in args)}]"
            return "Tuple"
        elif origin is Union or str(origin) == 'typing.Union':
            # Handle Union types (including Optional)
            if len(args) == 2 and type(None) in args:
                # This is Optional[X]
                non_none_type = args[0] if args[1] == type(None) else args[1]
                return f"Optional[{self._format_type(non_none_type)}]"
            else:
                return f"Union[{', '.join(self._format_type(arg) for arg in args)}]"
        elif hasattr(type_hint, '__name__'):
            return type_hint.__name__
        else:
            return str(type_hint)

class ToolSchemaInfo:
    """Complete schema information for a tool."""
    
    def __init__(self, tool_name: str, schema_class: Type[BaseModel]):
        self.tool_name = tool_name
        self.schema_class = schema_class
        self.fields = self._extract_fields()
        
    def _extract_fields(self) -> Dict[str, SchemaFieldInfo]:
        """Extract field information from schema class, filtering out internal fields."""
        fields = {}
        
        if hasattr(self.schema_class, '__fields__'):
            # Pydantic v1
            for name, field in self.schema_class.__fields__.items():
                if name not in EXCLUDED_FIELDS:
                    fields[name] = SchemaFieldInfo(name, field, field.type_)
        elif hasattr(self.schema_class, 'model_fields'):
            # Pydantic v2
            for name, field_info in self.schema_class.model_fields.items():
                if name not in EXCLUDED_FIELDS:
                    # Get field type from annotation
                    field_type = getattr(field_info, 'annotation', str)
                    fields[name] = SchemaFieldInfo(name, field_info, field_type)
        
        return fields
    
    @property
    def description(self) -> str:
        """Get schema description."""
        return getattr(self.schema_class, '__doc__', 'No description available') or 'No description available'
    
    @property
    def required_fields(self) -> List[str]:
        """Get list of required field names."""
        return [name for name, field in self.fields.items() if field.is_required]
    
    @property
    def optional_fields(self) -> List[str]:
        """Get list of optional field names."""
        return [name for name, field in self.fields.items() if not field.is_required]
    
    def get_field(self, name: str) -> Optional[SchemaFieldInfo]:
        """Get field information by name."""
        return self.fields.get(name)
    
    def to_json_schema(self) -> Dict[str, Any]:
        """Convert to JSON Schema format."""
        properties = {}
        required = []
        
        for name, field in self.fields.items():
            prop = {
                "type": self._json_schema_type(field.field_type),
                "description": field.description
            }
            
            # Add constraints
            constraints = field.constraints
            if constraints:
                prop.update(constraints)
            
            # Add default
            if field.default is not None:
                prop["default"] = field.default
            
            properties[name] = prop
            
            if field.is_required:
                required.append(name)
        
        return {
            "type": "object",
            "properties": properties,
            "required": required,
            "description": self.description
        }
    
    def _json_schema_type(self, python_type: Any) -> str:
        """Convert Python type to JSON Schema type."""
        if python_type in (str, type(str)):
            return "string"
        elif python_type in (int, type(int)):
            return "integer"
        elif python_type in (float, type(float)):
            return "number"
        elif python_type in (bool, type(bool)):
            return "boolean"
        elif get_origin(python_type) in (list, List):
            return "array"
        elif get_origin(python_type) in (dict, Dict):
            return "object"
        else:
            return "string"  # Default fallback

class SchemaLoader:
    """Schema loader for CLI tools."""
    
    def __init__(self):
        self._schema_cache: Dict[str, ToolSchemaInfo] = {}
        self._schemas_dir = Path(__file__).parent.parent.parent / "schemas"
    
    def resolve_tool_name(self, tool_name: str) -> str:
        """Resolve tool aliases to actual tool names."""
        return TOOL_ALIASES.get(tool_name.lower(), tool_name)
    
    def get_tool_schema(self, tool_name: str) -> Optional[ToolSchemaInfo]:
        """Get comprehensive schema information for a tool."""
        # Resolve aliases
        resolved_name = self.resolve_tool_name(tool_name)
        
        # Check cache
        if resolved_name in self._schema_cache:
            return self._schema_cache[resolved_name]
        
        # Load schema
        schema_info = self._load_schema(resolved_name)
        if schema_info:
            self._schema_cache[resolved_name] = schema_info
        
        return schema_info
    
    def _load_schema(self, tool_name: str) -> Optional[ToolSchemaInfo]:
        """Load schema class for a tool."""
        schema_path = TOOL_SCHEMA_MAPPING.get(tool_name)
        if not schema_path:
            return None
        
        try:
            # Import the schema module and class
            module_name, class_name = schema_path.rsplit('.', 1)
            
            # Dynamic import
            import importlib
            import sys
            
            # Add schemas directory to path temporarily
            schemas_path = str(self._schemas_dir)
            if schemas_path not in sys.path:
                sys.path.insert(0, schemas_path)
            
            try:
                module = importlib.import_module(module_name)
                schema_class = getattr(module, class_name)
                
                # Verify it's a Pydantic model
                if not issubclass(schema_class, BaseModel):
                    return None
                
                return ToolSchemaInfo(tool_name, schema_class)
                
            finally:
                # Remove from path
                if schemas_path in sys.path:
                    sys.path.remove(schemas_path)
                
        except (ImportError, AttributeError, TypeError) as e:
            print(f"Warning: Could not load schema for {tool_name}: {e}")
            return None
    
    def get_available_tools(self) -> List[str]:
        """Get list of all available tools with schemas."""
        return list(TOOL_SCHEMA_MAPPING.keys())
    
    def get_tool_examples(self, tool_name: str) -> List[Dict[str, Any]]:
        """Get usage examples for a tool (placeholder for future implementation)."""
        # This could be extended to load examples from schema docstrings,
        # separate example files, or generate examples from schema
        return []

# Global schema loader instance
_schema_loader = SchemaLoader()

def get_tool_schema(tool_name: str) -> Optional[ToolSchemaInfo]:
    """Get schema information for a tool."""
    return _schema_loader.get_tool_schema(tool_name)

def get_available_tools() -> List[str]:
    """Get list of available tools."""
    return _schema_loader.get_available_tools()

def resolve_tool_name(tool_name: str) -> str:
    """Resolve tool name aliases."""
    return _schema_loader.resolve_tool_name(tool_name)
