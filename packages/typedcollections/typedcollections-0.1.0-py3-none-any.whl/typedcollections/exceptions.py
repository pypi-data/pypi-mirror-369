class CoercionError(Exception):
    """Raised when a value cannot be coerced to the target type."""
    pass


class ValidationError(Exception):
    """Raised when a value fails validation."""
    pass

class TypedListTypeError(ValidationError):
    """Kept for backward compatibility with tests."""
    pass
#comment