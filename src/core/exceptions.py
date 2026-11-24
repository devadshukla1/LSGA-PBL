"""Custom domain-specific exceptions for MetroGraph Analytics."""


class MetroGraphError(Exception):
    """Base exception for all MetroGraph application errors."""

    pass


class DatasetError(MetroGraphError):
    """Raised when dataset loading, parsing, or integrity validation fails."""

    pass


class DatasetNotFoundError(DatasetError):
    """Raised when one or more expected dataset files do not exist."""

    pass


class SchemaValidationError(DatasetError):
    """Raised when CSV structure, missing columns, or data types are invalid."""

    pass


class GraphConstructionError(MetroGraphError):
    """Raised when building the NetworkX graph from validated data fails."""

    pass


class GraphValidationError(MetroGraphError):
    """Raised when graph invariants (connectivity, edge weights, node attributes) are violated."""

    pass


class ConfigurationError(MetroGraphError):
    """Raised when application paths or configuration constants are invalid."""

    pass
