import json
import time
import uuid
from typing import Any, Dict, Optional
from pydantic import ValidationError

from app.tools.tool_definition import ToolDefinition
from app.tools.tool_registry import tool_registry, ToolRegistry
from app.tools.tool_context import ToolExecutionContext
from app.tools.tool_result import ToolResult, ToolError, ToolErrorCode


class ToolExecutor:

    def __init__(
        self,
        registry: Optional[ToolRegistry] = None,
        max_output_length: int = 10000,
        timeout_seconds: float = 10.0
    ):
        self.registry = registry or tool_registry
        self.max_output_length = max_output_length
        self.timeout_seconds = timeout_seconds

    def execute(
        self,
        tool_name: str,
        arguments: Dict[str, Any],
        context: ToolExecutionContext,
        bypass_confirmation: bool = False
    ) -> ToolResult:
        start_time = time.time()

        # 1. Resolve Tool
        tool = self.registry.get_tool(tool_name)
        if not tool:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=ToolError(
                    code=ToolErrorCode.TOOL_NOT_FOUND,
                    message=f"Tool '{tool_name}' is not registered."
                )
            )

        # 2. Check Availability / Enabled
        if not tool.enabled:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=ToolError(
                    code=ToolErrorCode.TOOL_DISABLED,
                    message=f"Tool '{tool_name}' is currently disabled."
                )
            )

        # 3. Security & Permission Check
        if tool.required_permissions:
            for perm in tool.required_permissions:
                if not context.has_permission(perm):
                    return ToolResult(
                        success=False,
                        tool_name=tool_name,
                        error=ToolError(
                            code=ToolErrorCode.PERMISSION_DENIED,
                            message=f"User {context.user_id} lacks required permission '{perm}' for tool '{tool_name}'."
                        )
                    )

        # 4. Strict Argument Security Checks (Block shell/sql injection attempts)
        blocked_keywords = ["execute_sql", "run_shell", "drop table", ";--", "../../"]
        arg_str = json.dumps(arguments).lower()
        for kw in blocked_keywords:
            if kw in arg_str:
                return ToolResult(
                    success=False,
                    tool_name=tool_name,
                    error=ToolError(
                        code=ToolErrorCode.INVALID_ARGUMENTS,
                        message=f"Dangerous payload parameter detected ('{kw}'). Execution blocked."
                    )
                )

        # 5. Validate Arguments using Tool Pydantic Model
        validated_args = arguments
        if tool.args_model is not None:
            try:
                validated_model = tool.args_model(**arguments)
                validated_args = validated_model.dict()
            except ValidationError as ve:
                return ToolResult(
                    success=False,
                    tool_name=tool_name,
                    error=ToolError(
                        code=ToolErrorCode.INVALID_ARGUMENTS,
                        message=f"Invalid arguments for tool '{tool_name}': {str(ve)}",
                        details={"errors": ve.errors()}
                    )
                )

        # 6. Check Confirmation Policy
        if tool.requires_confirmation and not bypass_confirmation:
            conf_token = str(uuid.uuid4())
            return ToolResult(
                success=False,
                tool_name=tool_name,
                requires_confirmation=True,
                confirmation_token=conf_token,
                error=ToolError(
                    code=ToolErrorCode.CONFIRMATION_REQUIRED,
                    message=f"Execution of destructive tool '{tool_name}' requires explicit user confirmation.",
                    details={
                        "confirmation_token": conf_token,
                        "tool_name": tool_name,
                        "arguments": validated_args
                    }
                )
            )

        # 7. Execute Tool Safely
        try:
            raw_result = tool.execute(validated_args, context)
            exec_time = round((time.time() - start_time) * 1000, 2)

            # 8. Output Sanitization & Truncation
            sanitized_data = self._sanitize_and_cap_output(raw_result)

            return ToolResult(
                success=True,
                tool_name=tool_name,
                data=sanitized_data,
                execution_time_ms=exec_time
            )

        except ValueError as ve:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=ToolError(
                    code=ToolErrorCode.RESOURCE_NOT_FOUND,
                    message=str(ve)
                ),
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )
        except Exception as ex:
            return ToolResult(
                success=False,
                tool_name=tool_name,
                error=ToolError(
                    code=ToolErrorCode.EXECUTION_FAILED,
                    message=f"Execution error in tool '{tool_name}': {str(ex)}"
                ),
                execution_time_ms=round((time.time() - start_time) * 1000, 2)
            )

    def _sanitize_and_cap_output(self, data: Any) -> Any:
        """Truncate overly large string outputs or arrays to prevent LLM context exhaustion."""
        try:
            dumped = json.dumps(data, default=str)
            if len(dumped) > self.max_output_length:
                if isinstance(data, dict):
                    truncated_dict = {}
                    for k, v in data.items():
                        v_str = str(v)
                        if len(v_str) > 1000:
                            truncated_dict[k] = v_str[:1000] + "... [TRUNCATED]"
                        else:
                            truncated_dict[k] = v
                    return truncated_dict
                elif isinstance(data, list):
                    return data[:10]
            return data
        except Exception:
            return str(data)[:self.max_output_length]


tool_executor = ToolExecutor()
