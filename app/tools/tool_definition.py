from enum import Enum
from typing import Any, Dict, List, Optional, Type
from pydantic import BaseModel


class ToolCategory(str, Enum):
    TASKS = "tasks"
    NOTES = "notes"
    MEMORY = "memory"
    KNOWLEDGE = "knowledge"
    SEARCH = "search"
    PRODUCTIVITY = "productivity"
    SYSTEM = "system"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class ToolDefinition:

    name: str = ""
    description: str = ""
    category: ToolCategory = ToolCategory.SYSTEM
    read_only: bool = True
    risk_level: RiskLevel = RiskLevel.LOW
    requires_confirmation: bool = False
    required_permissions: List[str] = []
    enabled: bool = True
    args_model: Optional[Type[BaseModel]] = None

    def __init__(self):
        if not self.name:
            raise ValueError(f"Tool {self.__class__.__name__} must define a name.")

    def to_llm_schema(self) -> Dict[str, Any]:
        """Convert tool definition to standard OpenAI/Gemini compatible function schema."""
        parameters = {"type": "object", "properties": {}, "required": []}

        if self.args_model is not None:
            schema = self.args_model.schema()
            properties = {}
            for prop_name, prop_info in schema.get("properties", {}).items():
                prop_dict = {
                    "type": prop_info.get("type", "string"),
                    "description": prop_info.get("description", prop_info.get("title", ""))
                }
                if "enum" in prop_info:
                    prop_dict["enum"] = prop_info["enum"]
                properties[prop_name] = prop_dict

            parameters = {
                "type": "object",
                "properties": properties,
                "required": schema.get("required", [])
            }

        return {
            "name": self.name,
            "description": self.description,
            "parameters": parameters,
            "category": self.category.value,
            "read_only": self.read_only,
            "risk_level": self.risk_level.value,
            "requires_confirmation": self.requires_confirmation
        }

    def execute(self, arguments: Dict[str, Any], context: Any) -> Dict[str, Any]:
        """Subclasses must implement actual execution logic."""
        raise NotImplementedError("Subclasses must implement execute()")
