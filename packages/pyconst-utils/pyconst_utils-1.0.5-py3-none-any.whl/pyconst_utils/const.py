"""
    @file const.py
    @brief A module to define a constant class.
    @details This module provides a `Const` class that allows you to create immutable constant values.
    @author kronus-lx
    Enforce constant values in the python.
"""
from typing import Any

class ConstError(TypeError):
    """Custom exception for constant enforcement."""
    pass

class Const:
    """A class to represent an immutable constant value.

    Args:
        value: The immutable value to store.

    Raises:
        ConstError: If attempting to reassign the value or set new attributes.
    """
    def __init__(self, value: Any):
        super().__setattr__('_value', value)
        super().__setattr__('_frozen', True)

    @property
    def value(self) -> Any:
        """Get the stored constant value."""
        return self._value

    def __setattr__(self, name: str, value: Any) -> None:
        """Prevent attribute reassignment after initialization.

        Args:
            name: The attribute name.
            value: The value to set.

        Raises:
            ConstError: If attempting to set an attribute after initialization.
        """
        if hasattr(self, '_frozen') and self._frozen:
            raise ConstError(f"Cannot set attribute '{name}' on a constant.")
        super().__setattr__(name, value)

    def __repr__(self) -> str:
        """Return a string representation of the constant."""
        return f"Const({self._value!r})"