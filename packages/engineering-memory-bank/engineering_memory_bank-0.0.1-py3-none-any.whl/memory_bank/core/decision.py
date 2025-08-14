"""
Decision data structures for memory-bank system.

This module defines the core data structures for representing and managing
engineering decisions with comprehensive metadata and context.
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional


class DecisionCategory(Enum):
    """Categories of engineering decisions."""
    
    COMPONENT_SELECTION = "component_selection"
    ARCHITECTURE = "architecture"
    POWER_SUPPLY = "power_supply"
    FABRICATION = "fabrication"
    TESTING = "testing"
    VALIDATION = "validation"
    ISSUE = "issue"
    MILESTONE = "milestone"
    PERFORMANCE = "performance"
    COST_OPTIMIZATION = "cost_optimization"
    RELIABILITY = "reliability"
    COMPLIANCE = "compliance"
    MANUFACTURING = "manufacturing"
    DESIGN_REVIEW = "design_review"
    SUPPLIER = "supplier"
    OTHER = "other"


class DecisionImpact(Enum):
    """Impact levels for engineering decisions."""
    
    LOW = "low"          # Minor changes, local impact
    MEDIUM = "medium"    # Moderate changes, module impact
    HIGH = "high"        # Major changes, system impact
    CRITICAL = "critical" # Critical changes, project impact


class DecisionStatus(Enum):
    """Status of engineering decisions."""
    
    PROPOSED = "proposed"      # Decision proposed but not implemented
    APPROVED = "approved"      # Decision approved but not implemented
    IMPLEMENTED = "implemented" # Decision implemented
    VALIDATED = "validated"    # Decision implemented and validated
    SUPERSEDED = "superseded"  # Decision replaced by newer decision
    REJECTED = "rejected"      # Decision rejected


@dataclass
class Decision:
    """
    Engineering decision with comprehensive metadata.
    
    Represents a single engineering decision with full context,
    rationale, alternatives, and impact assessment.
    """
    
    # Core decision data
    category: DecisionCategory
    decision: str
    rationale: str = ""
    
    # Decision context
    alternatives: List[str] = field(default_factory=list)
    impact: DecisionImpact = DecisionImpact.MEDIUM
    status: DecisionStatus = DecisionStatus.IMPLEMENTED
    tags: List[str] = field(default_factory=list)
    context: Dict[str, Any] = field(default_factory=dict)
    
    # Metadata
    timestamp: datetime = field(default_factory=datetime.now)
    author: Optional[str] = None
    uuid: str = field(default_factory=lambda: str(uuid.uuid4()))
    
    # Tracking
    implementation_date: Optional[datetime] = None
    validation_date: Optional[datetime] = None
    superseded_by: Optional[str] = None  # UUID of superseding decision
    
    def __post_init__(self):
        """Post-initialization processing."""
        # Ensure enums are correct type
        if isinstance(self.category, str):
            self.category = DecisionCategory(self.category)
        if isinstance(self.impact, str):
            self.impact = DecisionImpact(self.impact)
        if isinstance(self.status, str):
            self.status = DecisionStatus(self.status)
    
    @property
    def age_days(self) -> int:
        """Get age of decision in days."""
        return (datetime.now() - self.timestamp).days
    
    @property
    def is_recent(self) -> bool:
        """Check if decision is recent (within 30 days)."""
        return self.age_days <= 30
    
    @property
    def is_high_impact(self) -> bool:
        """Check if decision has high or critical impact."""
        return self.impact in (DecisionImpact.HIGH, DecisionImpact.CRITICAL)
    
    def add_tag(self, tag: str):
        """Add a tag to the decision."""
        if tag not in self.tags:
            self.tags.append(tag)
    
    def remove_tag(self, tag: str) -> bool:
        """Remove a tag from the decision."""
        if tag in self.tags:
            self.tags.remove(tag)
            return True
        return False
    
    def add_context(self, key: str, value: Any):
        """Add context data to the decision."""
        self.context[key] = value
    
    def get_context(self, key: str, default: Any = None) -> Any:
        """Get context data from the decision."""
        return self.context.get(key, default)
    
    def supersede(self, new_decision_uuid: str):
        """Mark this decision as superseded by a newer one."""
        self.status = DecisionStatus.SUPERSEDED
        self.superseded_by = new_decision_uuid
    
    def validate(self, validation_notes: str = ""):
        """Mark decision as validated."""
        self.status = DecisionStatus.VALIDATED
        self.validation_date = datetime.now()
        if validation_notes:
            self.add_context('validation_notes', validation_notes)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert decision to dictionary representation."""
        return {
            'uuid': self.uuid,
            'category': self.category.value,
            'decision': self.decision,
            'rationale': self.rationale,
            'alternatives': self.alternatives,
            'impact': self.impact.value,
            'status': self.status.value,
            'tags': self.tags,
            'context': self.context,
            'timestamp': self.timestamp.isoformat(),
            'author': self.author,
            'implementation_date': self.implementation_date.isoformat() if self.implementation_date else None,
            'validation_date': self.validation_date.isoformat() if self.validation_date else None,
            'superseded_by': self.superseded_by,
            'age_days': self.age_days,
            'is_recent': self.is_recent,
            'is_high_impact': self.is_high_impact
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Decision':
        """Create Decision from dictionary representation."""
        # Parse datetime fields
        timestamp = datetime.fromisoformat(data['timestamp'])
        implementation_date = None
        if data.get('implementation_date'):
            implementation_date = datetime.fromisoformat(data['implementation_date'])
        validation_date = None
        if data.get('validation_date'):
            validation_date = datetime.fromisoformat(data['validation_date'])
        
        return cls(
            uuid=data['uuid'],
            category=DecisionCategory(data['category']),
            decision=data['decision'],
            rationale=data['rationale'],
            alternatives=data['alternatives'],
            impact=DecisionImpact(data['impact']),
            status=DecisionStatus(data['status']),
            tags=data['tags'],
            context=data['context'],
            timestamp=timestamp,
            author=data.get('author'),
            implementation_date=implementation_date,
            validation_date=validation_date,
            superseded_by=data.get('superseded_by')
        )
    
    def __str__(self) -> str:
        """String representation of decision."""
        return f"<Decision {self.category.value}: {self.decision[:50]}{'...' if len(self.decision) > 50 else ''}>"
    
    def __repr__(self) -> str:
        """Detailed representation of decision."""
        return (f"Decision(category={self.category.value}, "
                f"impact={self.impact.value}, "
                f"status={self.status.value}, "
                f"age_days={self.age_days})")


@dataclass
class DecisionTemplate:
    """Template for common decision types."""
    
    name: str
    category: DecisionCategory
    description: str
    required_fields: List[str] = field(default_factory=list)
    suggested_tags: List[str] = field(default_factory=list)
    example_rationale: str = ""
    
    def create_decision(self, **kwargs) -> Decision:
        """Create a decision from this template."""
        # Validate required fields
        for field in self.required_fields:
            if field not in kwargs:
                raise ValueError(f"Required field missing: {field}")
        
        # Extract decision data
        decision_text = kwargs.get('decision', '')
        rationale = kwargs.get('rationale', self.example_rationale)
        tags = kwargs.get('tags', []) + self.suggested_tags
        
        return Decision(
            category=self.category,
            decision=decision_text,
            rationale=rationale,
            tags=list(set(tags)),  # Remove duplicates
            context=kwargs.get('context', {}),
            alternatives=kwargs.get('alternatives', []),
            impact=kwargs.get('impact', DecisionImpact.MEDIUM)
        )


# Common decision templates
DECISION_TEMPLATES = {
    'component_selection': DecisionTemplate(
        name='Component Selection',
        category=DecisionCategory.COMPONENT_SELECTION,
        description='Selection of electronic components',
        required_fields=['component', 'selected_part'],
        suggested_tags=['component', 'selection', 'parts'],
        example_rationale='Selected based on specifications, availability, and cost'
    ),
    
    'power_supply': DecisionTemplate(
        name='Power Supply Design',
        category=DecisionCategory.POWER_SUPPLY,
        description='Power supply architecture and component decisions',
        required_fields=['topology', 'output_voltage'],
        suggested_tags=['power', 'regulation', 'efficiency'],
        example_rationale='Chosen topology based on efficiency and size requirements'
    ),
    
    'test_result': DecisionTemplate(
        name='Test Result',
        category=DecisionCategory.TESTING,
        description='Test execution results and validation',
        required_fields=['test_name', 'result'],
        suggested_tags=['testing', 'validation', 'verification'],
        example_rationale='Test executed according to test plan'
    ),
    
    'issue_resolution': DecisionTemplate(
        name='Issue Resolution',
        category=DecisionCategory.ISSUE,
        description='Problem identification and resolution',
        required_fields=['issue', 'resolution'],
        suggested_tags=['issue', 'problem', 'fix'],
        example_rationale='Issue identified and resolved with root cause analysis'
    )
}