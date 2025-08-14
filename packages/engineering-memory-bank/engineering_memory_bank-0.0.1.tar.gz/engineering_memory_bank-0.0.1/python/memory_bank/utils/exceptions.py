"""
Exception classes for memory-bank system.

This module defines custom exceptions for memory-bank operations,
providing clear error handling and debugging information.
"""


class MemoryBankError(Exception):
    """Base exception for memory-bank operations."""
    
    def __init__(self, message: str, context: dict = None):
        super().__init__(message)
        self.context = context or {}
    
    def __str__(self) -> str:
        if self.context:
            context_str = ", ".join(f"{k}={v}" for k, v in self.context.items())
            return f"{super().__str__()} (Context: {context_str})"
        return super().__str__()


class DecisionError(MemoryBankError):
    """Exception for decision-related operations."""
    pass


class GitIntegrationError(MemoryBankError):
    """Exception for git integration issues."""
    pass


class AIAnalysisError(MemoryBankError):
    """Exception for AI analysis operations."""
    pass


class TemplateError(MemoryBankError):
    """Exception for template operations."""
    pass


class ConfigurationError(MemoryBankError):
    """Exception for configuration issues."""
    pass