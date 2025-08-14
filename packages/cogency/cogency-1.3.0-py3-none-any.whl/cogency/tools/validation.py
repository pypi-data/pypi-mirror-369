"""Tool argument validation."""

from typing import Any, TypeVar

T = TypeVar("T")


def validate(args: dict[str, Any], schema: type[T]) -> T:
    """Validate arguments against dataclass schema.

    Args:
        args: Dictionary of arguments to validate
        schema: Dataclass type to validate against

    Returns:
        Validated dataclass instance

    Raises:
        ValueError: If validation fails
    """
    if not hasattr(schema, "__dataclass_fields__"):
        raise ValueError(f"Schema {schema} is not a dataclass")

    # Filter args to only include fields defined in the dataclass
    valid_fields = set(schema.__dataclass_fields__.keys())
    filtered_args = {k: v for k, v in args.items() if k in valid_fields}

    try:
        return schema(**filtered_args)
    except TypeError as e:
        raise ValueError(f"Argument validation failed: {str(e)}") from e
