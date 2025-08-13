"""
Models specific to REST API tool generation from OpenAPI specs.
"""
from dataclasses import dataclass
from typing import List, Dict, Any, Optional
import os
import json
from opal_tools_sdk.models import Parameter, AuthRequirement, Function, ParameterType


@dataclass
class ParsedOperation:
    """Parsed operation from OpenAPI specification."""
    name: str
    description: str
    method: str
    path: str
    base_url: str
    parameters: List[Parameter]
    auth_requirements: Optional[List[AuthRequirement]] = None
    operation_id: Optional[str] = None
    request_body_schema: Optional[Dict[str, Any]] = None
    response_schema: Optional[Dict[str, Any]] = None
    tags: Optional[List[str]] = None
    use_api_key_param: bool = False  # NEW: Flag to indicate if using api_key parameter
    
    def to_function(self) -> Function:
        """Convert to Function object for tool registration."""
        endpoint = f"/rest-tools/{self.name}"
        
        # HACK: When using api_key_as_required_param, don't include auth_requirements
        auth_reqs = None if self.use_api_key_param else self.auth_requirements
        
        return Function(
            name=self.name,
            description=self.description,
            parameters=self.parameters,
            endpoint=endpoint,
            auth_requirements=auth_reqs,
            http_method="POST"  # All tools use POST to receive parameters
        )


def get_auth_mapping() -> Dict[str, str]:
    """Load auth mapping from AUTH_MAPPING environment variable."""
    auth_mapping_json = os.getenv("AUTH_MAPPING", "{}")
    try:
        return json.loads(auth_mapping_json)
    except json.JSONDecodeError:
        return {}


def get_auth_value(api_key: str) -> Optional[str]:
    """Get auth value for given API key from environment mapping."""
    mapping = get_auth_mapping()
    return mapping.get(api_key)


@dataclass
class OpenAPIConfig:
    """Configuration for OpenAPI spec parsing."""
    base_url: Optional[str] = None
    auth_config: Optional[Dict[str, Any]] = None #TODO
    filter_operations: Optional[List[str]] = None 
    exclude_operations: Optional[List[str]] = None
    api_key_as_required_param: bool = False  # NEW: Simplified auth approach