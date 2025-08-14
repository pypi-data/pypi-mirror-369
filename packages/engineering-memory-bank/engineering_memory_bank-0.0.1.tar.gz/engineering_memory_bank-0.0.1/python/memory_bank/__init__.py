"""
engineering-memory-bank: AI-Powered Engineering Decision Documentation System

An intelligent system for automatically capturing, organizing, and analyzing engineering 
design decisions with git integration and AI-powered insights.

Key Features:
- Automatic decision capture via git hooks
- AI-powered decision analysis and recommendations
- Cross-project knowledge sharing and learning
- Professional documentation templates
- Timeline reconstruction of design decisions
- Intelligent search and filtering

Basic Usage:
    import memory_bank as mb
    
    # Initialize in project
    bank = mb.MemoryBank.init_project('/path/to/project')
    
    # Manual decision logging
    bank.log_decision(
        category='component_selection',
        decision='Selected STM32F407 over STM32F405',
        rationale='Need USB OTG and Ethernet capabilities'
    )
    
    # Get AI insights
    insights = bank.analyze_decisions()
    
    # Search decision history
    power_decisions = bank.search_decisions('power supply')

Advanced Usage:
    # Cross-project learning
    similar = bank.find_similar_decisions(
        'microcontroller selection',
        across_projects=True
    )
    
    # AI recommendations
    recommendations = bank.get_ai_recommendations()
    
    # Timeline analysis
    timeline = bank.get_decision_timeline()
    milestones = bank.get_project_milestones()
"""

__version__ = "0.0.1"
__author__ = "Circuit-Synth"
__email__ = "info@circuit-synth.com"

# Core imports for public API
from .core.memory_bank import MemoryBank
from .core.decision import Decision, DecisionCategory, DecisionImpact
from .core.context import ContextManager, ProjectContext
from .git.integration import GitIntegration, GitHooks
from .ai.analyzer import DecisionAnalyzer, AIInsights
from .utils.exceptions import MemoryBankError, DecisionError

# Version info
VERSION_INFO = (0, 0, 1)

# Public API
__all__ = [
    # Core classes
    'MemoryBank',
    'Decision',
    'DecisionCategory', 
    'DecisionImpact',
    'ContextManager',
    'ProjectContext',
    'GitIntegration',
    'GitHooks',
    'DecisionAnalyzer',
    'AIInsights',
    
    # Exceptions
    'MemoryBankError',
    'DecisionError',
    
    # Version info
    '__version__',
    'VERSION_INFO',
]

# Convenience functions
def init_project(project_path: str = '.') -> 'MemoryBank':
    """
    Initialize memory-bank in a project directory.
    
    Args:
        project_path: Path to project directory
        
    Returns:
        Initialized MemoryBank instance
        
    Example:
        >>> bank = mb.init_project('/path/to/my_project')
        >>> bank.setup_git_hooks()
    """
    return MemoryBank.init_project(project_path)

def current_project() -> 'MemoryBank':
    """
    Get memory-bank for current directory.
    
    Returns:
        MemoryBank instance for current project
        
    Example:
        >>> bank = mb.current_project()
        >>> bank.log_decision('component_choice', 'Selected STM32F407')
    """
    return MemoryBank.current_project()

# Add convenience functions to __all__
__all__.extend(['init_project', 'current_project'])