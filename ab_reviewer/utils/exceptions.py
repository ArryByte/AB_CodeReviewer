"""Custom exceptions for AB Code Reviewer."""


class ABReviewerError(Exception):
    """Base exception for AB Code Reviewer."""
    pass


class ConfigurationError(ABReviewerError):
    """Configuration-related errors."""
    pass


class ToolNotFoundError(ABReviewerError):
    """Required tool not found."""
    pass


class ToolExecutionError(ABReviewerError):
    """Tool execution failed."""
    pass


class ProjectDetectionError(ABReviewerError):
    """Project type detection failed."""
    pass


class AIReviewError(ABReviewerError):
    """AI review failed."""
    pass


class ValidationError(ABReviewerError):
    """Input validation failed."""
    pass
