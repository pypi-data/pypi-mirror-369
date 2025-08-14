"""Useful enums for research projects."""

from enum import StrEnum


class OptionsEnum(StrEnum):
    """
    Enum to store different string configuration options for a method.
    Can also be used  when defining command line arguments.
    """

    def __str__(self) -> str:
        """Just the string value."""
        return str.__str__(self)

    @classmethod
    def options(cls) -> str:
        """Return a string of all options."""
        return ", ".join([type.value for type in cls])

    @classmethod
    def list(cls) -> list[str]:
        """Return a list of all options."""
        return [type.value for type in cls]

    @staticmethod
    def _generate_next_value_(name: str, start, count, last_values) -> str:
        """Auto-generate string values based on the member name."""
        return name.lower()

    def __eq__(self, other) -> bool:
        """Case-insensitive equality checks."""
        return (
            self.value.lower() == other.lower()
            if isinstance(other, str)
            else super().__eq__(other)
        )

    def __ne__(self, other) -> bool:
        """Mirror the __eq__ method for inequality."""
        return not self.__eq__(other)

    def __hash__(self) -> int:
        """Ensure that hashing is consistent with __eq__."""
        return hash(self.value.lower())
