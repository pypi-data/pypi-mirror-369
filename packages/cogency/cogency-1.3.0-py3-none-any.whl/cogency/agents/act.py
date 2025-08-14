"""Tool execution logic."""

from typing import Any

from resilient_result import Result

from cogency.events import emit


async def act(tool_calls: list[dict], tools, state, user_id: str = "default") -> dict[str, Any]:
    """Act on reasoning decisions - execute tool calls."""

    if not tool_calls:
        return Result.ok(
            {
                "results": [],
                "errors": [],
                "summary": "No tools to execute",
                "total_executed": 0,
                "successful_count": 0,
                "failed_count": 0,
            }
        )

    successes = []
    failures = []

    for call in tool_calls:
        tool_name = call.get("name")  # Canonical format
        tool_args = call.get("args", {})

        # Find tool instance
        tool_instance = next((t for t in tools if t.name == tool_name), None)
        if not tool_instance:
            failures.append(
                {
                    "name": tool_name,
                    "args": tool_args,
                    "success": False,
                    "error": f"Tool '{tool_name}' not found",
                }
            )
            continue

        try:
            # Inject user_id for tools that need user context
            if tool_name == "recall":
                tool_args["user_id"] = user_id

            # Emit tool execution start
            emit("tool", name=tool_name, status="start", operation="execute")

            # Execute tool with unpacked args
            result = await tool_instance.execute(**tool_args)

            # Emit tool execution complete
            emit(
                "tool",
                name=tool_name,
                status="complete",
                operation="execute",
                success=result.success,
            )

            if result.success:
                successes.append(
                    {
                        "name": tool_name,
                        "args": tool_args,
                        "success": True,
                        "result": result,
                        "error": None,
                    }
                )

                # Update state for LLM feedback
                if state and hasattr(state, "execution"):
                    if not hasattr(state.execution, "completed_calls"):
                        state.execution.completed_calls = []
                    state.execution.completed_calls.append(
                        {
                            "tool": tool_name,
                            "args": tool_args,
                            "result": result.unwrap(),
                            "success": True,
                        }
                    )

            else:
                failures.append(
                    {
                        "name": tool_name,
                        "args": tool_args,
                        "success": False,
                        "result": result,
                        "error": str(result.error),
                    }
                )

                # CRITICAL: Update state with failures too for constitutional reasoning
                if state and hasattr(state, "execution"):
                    if not hasattr(state.execution, "completed_calls"):
                        state.execution.completed_calls = []
                    state.execution.completed_calls.append(
                        {
                            "tool": tool_name,
                            "args": tool_args,
                            "result": result,  # Keep full Result object for error details
                            "success": False,
                        }
                    )

        except Exception as e:
            # Emit tool execution error
            emit("tool", name=tool_name, status="error", operation="execute", error=str(e))

            exception_result = Result.fail(str(e))
            failures.append(
                {
                    "name": tool_name,
                    "args": tool_args,
                    "success": False,
                    "result": exception_result,
                    "error": str(e),
                }
            )

            # CRITICAL: Update state with exceptions too for constitutional reasoning
            if state and hasattr(state, "execution"):
                if not hasattr(state.execution, "completed_calls"):
                    state.execution.completed_calls = []
                state.execution.completed_calls.append(
                    {
                        "tool": tool_name,
                        "args": tool_args,
                        "result": exception_result,
                        "success": False,
                    }
                )

    # Generate summary
    summary_parts = []
    if successes:
        summary_parts.append(f"{len(successes)} tools executed successfully")
    if failures:
        summary_parts.append(f"{len(failures)} tools failed")
    summary = "; ".join(summary_parts) if summary_parts else "No tools executed"

    return Result.ok(
        {
            "results": successes,
            "errors": failures,
            "summary": summary,
            "total_executed": len(tool_calls),
            "successful_count": len(successes),
            "failed_count": len(failures),
        }
    )


def _find_tool(tool_name: str, tools) -> Any:
    """Find tool by name."""
    return next((t for t in tools if t.name == tool_name), None)
