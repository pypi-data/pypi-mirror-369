"""Common utilities for SFMC API data structures."""

from pydantic import ConfigDict

# Common Pydantic configuration for SFMC models
SFMC_MODEL_CONFIG = ConfigDict(
    # Allow extra fields for forward compatibility with API changes
    extra="ignore",
    # Use enum values instead of enum objects for serialization
    use_enum_values=True,
    # Validate assignment to ensure data integrity
    validate_assignment=True,
    # Use field names only for initialization (not aliases) for better IDE support
    populate_by_name=True,
    # Serialize by alias to match API field names
    serialize_by_alias=True,
)
