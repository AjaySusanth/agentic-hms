"""
Pydantic schemas for validating integration YAML configs
and template definitions.
"""

from typing import Dict, List, Optional, Literal
from pydantic import BaseModel, Field


class AuthConfig(BaseModel):
    """Authentication configuration for an external service."""
    type: Literal["api_key", "bearer", "none"] = "none"
    header: Optional[str] = None
    value_env: Optional[str] = None  # Environment variable name holding the secret


class IntegrationConfig(BaseModel):
    """
    Schema for per-client YAML integration configs.
    Validated on load to catch bad configs early.
    """
    service_name: str = Field(..., description="Display name, e.g. 'Tasty Bites Restaurant'")
    service_type: str = Field(..., description="Template to use, e.g. 'restaurant_reservation'")
    base_url: str = Field(..., description="Base URL of the external API")
    auth: AuthConfig = Field(default_factory=lambda: AuthConfig(type="none"))
    field_mappings: Dict[str, str] = Field(
        default_factory=dict,
        description="Maps our standard field names to the external API's field names",
    )
    endpoints: Dict[str, str] = Field(
        ...,
        description="Named actions mapped to HTTP specs, e.g. {'search_tables': 'GET /tables/available'}",
    )
    rag_documents: List[str] = Field(
        default_factory=list,
        description="Paths to documents for RAG-powered FAQ answers",
    )


class TemplateStepDefinition(BaseModel):
    """A single step in a workflow template."""
    id: str
    type: Literal["collect_input", "api_call"]
    prompt: Optional[str] = None
    fields: List[str] = Field(default_factory=list)
    action: Optional[str] = None           # for api_call steps: maps to config endpoint key
    display_results: bool = False          # for api_call steps: show API response to user
    next: Optional[str] = None             # next step id, None means completed


class TemplateDefinition(BaseModel):
    """
    A reusable workflow template.
    Defines the steps for a specific service type.
    """
    name: str
    description: str
    steps: List[TemplateStepDefinition]

    def get_step(self, step_id: str) -> Optional[TemplateStepDefinition]:
        """Get a step by its ID."""
        for step in self.steps:
            if step.id == step_id:
                return step
        return None

    def get_first_step(self) -> TemplateStepDefinition:
        """Get the first step of the workflow."""
        return self.steps[0]
