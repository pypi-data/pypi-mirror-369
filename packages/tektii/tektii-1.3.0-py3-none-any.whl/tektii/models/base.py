"""Type checking protocols for proto conversions.

This module provides protocols that define the interface for proto-convertible models.
These are used for static type checking with mypy/pyright rather than runtime validation.
"""

from enum import IntEnum
from typing import Any, Protocol, Type, TypeVar, Union, cast

from google.protobuf.message import Message

# Type variables for generic proto messages
ProtoT = TypeVar("ProtoT", bound=Message)
ModelT = TypeVar("ModelT")


class ProtoConvertible(Protocol[ProtoT]):
    """Protocol for models that can convert to/from a single proto type.

    This is for static type checking only. Models don't need to inherit from this,
    they just need to implement the methods with matching signatures.

    Example:
        class Order:
            def to_proto(self) -> order_pb2.Order: ...

            @classmethod
            def from_proto(cls, proto: order_pb2.Order) -> "Order": ...
    """

    def to_proto(self) -> ProtoT:
        """Convert model instance to protobuf message."""
        ...

    @classmethod
    def from_proto(cls: Type[ModelT], proto: ProtoT) -> ModelT:
        """Create model instance from protobuf message."""
        ...


T = TypeVar("T", bound="ProtoEnum")


class ProtoEnum(IntEnum):
    """Base class for proto-compatible enums."""

    def to_proto(self) -> Any:
        """Convert to proto-compatible int value.

        Proto stubs incorrectly type enum fields as enum types,
        but they accept int values at runtime. This method provides
        the correct int value while satisfying mypy.

        Returns:
            Proto-compatible int value
        """
        return cast(Any, self.value)

    @classmethod
    def from_proto(cls: type[T], value: int) -> T:
        """Create enum from proto value.

        Args:
            value: Proto enum value

        Returns:
            Enum instance

        Raises:
            ValueError: If value is not valid
        """
        try:
            return cls(value)
        except ValueError:
            raise ValueError(f"Invalid {cls.__name__} proto value: {value}")

    @classmethod
    def from_string(cls: type[T], value: str) -> T:
        """Create enum from string representation.

        Args:
            value: String representation (case-insensitive)

        Returns:
            Enum instance

        Raises:
            ValueError: If string is not valid
        """
        value_upper = value.upper()
        for member in cls:
            if member.name == value_upper:
                return member

        # Handle special cases
        if hasattr(cls, "_aliases"):
            aliases = cls._aliases()  # type: ignore[attr-defined]
            if value_upper in aliases:
                return cast(T, aliases[value_upper])

        raise ValueError(f"Invalid {cls.__name__}: {value}")

    def __str__(self) -> str:
        """Return string representation without enum prefix."""
        return self.name


# Type aliases for convenience
AnyProtoConvertible = Union[ProtoConvertible[Message], ProtoEnum]

# Type variable constrained to proto-convertible types
T_ProtoConvertible = TypeVar("T_ProtoConvertible", bound=AnyProtoConvertible)
