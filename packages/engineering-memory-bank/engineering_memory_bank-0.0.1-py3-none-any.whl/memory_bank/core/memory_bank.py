"""
Core Memory Bank system for engineering decision documentation.

This module provides the main MemoryBank class that orchestrates automatic decision
capture, analysis, and knowledge management for engineering projects.
"""

import json
import logging
import os
import shutil
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Union

from ..git.integration import GitIntegration
from ..ai.analyzer import DecisionAnalyzer
from ..templates.manager import TemplateManager
from .decision import Decision, DecisionCategory, DecisionImpact
from .context import ContextManager, ProjectContext
from ..utils.exceptions import MemoryBankError

logger = logging.getLogger(__name__)


class MemoryBank:
    """
    Main Memory Bank system for engineering decision documentation.
    
    Features:
    - Automatic decision capture via git hooks
    - AI-powered decision analysis and insights
    - Cross-project knowledge sharing
    - Professional documentation templates
    - Timeline reconstruction and milestone tracking
    """

    def __init__(self, project_path: Union[str, Path] = None):
        """
        Initialize MemoryBank for a project.
        
        Args:
            project_path: Path to project directory (defaults to current directory)
        """
        self.project_path = Path(project_path) if project_path else Path.cwd()
        self.memory_bank_dir = self.project_path / "memory-bank"
        self.config_file = self.project_path / ".memory-bank-config.json"
        
        # Initialize components
        self.git_integration = GitIntegration(self.project_path)
        self.context_manager = ContextManager(self.project_path)
        self.template_manager = TemplateManager()
        self.ai_analyzer = DecisionAnalyzer()
        
        # Load configuration if exists
        self.config = self._load_config()
        
        logger.debug(f"MemoryBank initialized for project: {self.project_path}")

    @classmethod
    def init_project(cls, project_path: Union[str, Path] = None, 
                     project_name: str = None) -> 'MemoryBank':
        """
        Initialize memory-bank system in a project.
        
        Args:
            project_path: Path to project directory
            project_name: Name of the project
            
        Returns:
            Configured MemoryBank instance
        """
        project_path = Path(project_path) if project_path else Path.cwd()
        project_name = project_name or project_path.name
        
        logger.info(f"Initializing memory-bank for project: {project_name}")
        
        # Create MemoryBank instance
        bank = cls(project_path)
        
        # Create directory structure
        bank._create_project_structure(project_name)
        
        # Setup git hooks
        bank.setup_git_hooks()
        
        # Create initial configuration
        bank._save_config({
            'project_name': project_name,
            'initialized': datetime.now().isoformat(),
            'version': '0.0.1',
            'git_hooks_enabled': True
        })
        
        logger.info(f"Memory-bank initialized successfully")
        return bank

    @classmethod
    def current_project(cls) -> 'MemoryBank':
        """
        Get MemoryBank for current directory.
        
        Returns:
            MemoryBank instance for current project
            
        Raises:
            MemoryBankError: If no memory-bank found in current or parent directories
        """
        current_path = Path.cwd()
        
        # Search up directory tree for memory-bank
        for path in [current_path] + list(current_path.parents):
            config_file = path / ".memory-bank-config.json"
            if config_file.exists():
                return cls(path)
        
        raise MemoryBankError("No memory-bank found in current directory or parents")

    def log_decision(self, 
                    category: Union[str, DecisionCategory],
                    decision: str,
                    rationale: str = "",
                    alternatives: List[str] = None,
                    impact: Union[str, DecisionImpact] = DecisionImpact.MEDIUM,
                    tags: List[str] = None,
                    context: Dict[str, Any] = None) -> Decision:
        """
        Manually log an engineering decision.
        
        Args:
            category: Decision category (e.g., 'component_selection')
            decision: The decision made
            rationale: Why this decision was made
            alternatives: Other options considered
            impact: Impact level of the decision
            tags: Tags for categorization
            context: Additional context data
            
        Returns:
            Created Decision object
        """
        # Create decision object
        decision_obj = Decision(
            category=category,
            decision=decision,
            rationale=rationale,
            alternatives=alternatives or [],
            impact=impact,
            tags=tags or [],
            context=context or {},
            timestamp=datetime.now()
        )
        
        # Save to appropriate template file
        self._save_decision_to_file(decision_obj)
        
        logger.info(f"Logged decision: {category} - {decision}")
        return decision_obj

    def log_test_result(self,
                       test_name: str,
                       result: Dict[str, Any],
                       meets_spec: bool,
                       notes: str = "") -> Decision:
        """
        Log test results as a decision.
        
        Args:
            test_name: Name of the test
            result: Test result data
            meets_spec: Whether result meets specifications
            notes: Additional notes
            
        Returns:
            Created Decision object for test result
        """
        decision_text = f"{test_name}: {'PASS' if meets_spec else 'FAIL'}"
        rationale = f"Test results: {result}. {notes}".strip()
        
        return self.log_decision(
            category=DecisionCategory.TESTING,
            decision=decision_text,
            rationale=rationale,
            impact=DecisionImpact.HIGH if not meets_spec else DecisionImpact.MEDIUM,
            tags=['testing', 'validation'],
            context={
                'test_name': test_name,
                'result': result,
                'meets_spec': meets_spec,
                'notes': notes
            }
        )

    def search_decisions(self, 
                        query: str,
                        category: Optional[str] = None,
                        tags: Optional[List[str]] = None,
                        date_range: Optional[tuple] = None) -> List[Decision]:
        """
        Search decision history.
        
        Args:
            query: Search query string
            category: Filter by category
            tags: Filter by tags
            date_range: (start_date, end_date) tuple
            
        Returns:
            List of matching decisions
        """
        # Load all decisions from files
        decisions = self._load_all_decisions()
        
        # Apply filters
        results = []
        query_lower = query.lower()
        
        for decision in decisions:
            # Text search
            searchable_text = f"{decision.decision} {decision.rationale}".lower()
            if query_lower not in searchable_text:
                continue
                
            # Category filter
            if category and decision.category.value != category:
                continue
                
            # Tag filter
            if tags and not any(tag in decision.tags for tag in tags):
                continue
                
            # Date range filter
            if date_range:
                start_date, end_date = date_range
                if not (start_date <= decision.timestamp <= end_date):
                    continue
                    
            results.append(decision)
        
        return results

    def analyze_decisions(self) -> 'AIInsights':
        """
        Get AI-powered analysis of project decisions.
        
        Returns:
            AI insights and recommendations
        """
        decisions = self._load_all_decisions()
        return self.ai_analyzer.analyze_decisions(decisions)

    def get_ai_recommendations(self) -> List[Dict[str, Any]]:
        """
        Get AI recommendations based on decision history.
        
        Returns:
            List of AI-generated recommendations
        """
        insights = self.analyze_decisions()
        return insights.recommendations

    def find_similar_decisions(self, 
                              query: str,
                              across_projects: bool = False) -> List[Decision]:
        """
        Find similar decisions using AI similarity matching.
        
        Args:
            query: Description of decision type to find
            across_projects: Whether to search across multiple projects
            
        Returns:
            List of similar decisions
        """
        if across_projects:
            # TODO: Implement cross-project search
            logger.warning("Cross-project search not yet implemented")
            return []
        
        return self.ai_analyzer.find_similar_decisions(query, self._load_all_decisions())

    def get_decision_timeline(self) -> List[Dict[str, Any]]:
        """
        Get chronological timeline of all decisions.
        
        Returns:
            Timeline data with decisions and milestones
        """
        decisions = self._load_all_decisions()
        
        # Sort by timestamp
        decisions.sort(key=lambda d: d.timestamp)
        
        timeline = []
        for decision in decisions:
            timeline.append({
                'timestamp': decision.timestamp,
                'type': 'decision',
                'category': decision.category.value,
                'decision': decision.decision,
                'impact': decision.impact.value,
                'tags': decision.tags
            })
        
        return timeline

    def get_project_milestones(self) -> List[Dict[str, Any]]:
        """
        Extract major project milestones from decision history.
        
        Returns:
            List of identified milestones
        """
        decisions = self._load_all_decisions()
        
        # Identify milestone decisions (high impact, certain categories)
        milestone_categories = {
            DecisionCategory.ARCHITECTURE,
            DecisionCategory.COMPONENT_SELECTION,
            DecisionCategory.FABRICATION
        }
        
        milestones = []
        for decision in decisions:
            if (decision.category in milestone_categories and 
                decision.impact == DecisionImpact.HIGH):
                milestones.append({
                    'timestamp': decision.timestamp,
                    'milestone': decision.decision,
                    'category': decision.category.value,
                    'rationale': decision.rationale
                })
        
        return sorted(milestones, key=lambda m: m['timestamp'])

    def setup_git_hooks(self) -> bool:
        """
        Setup git hooks for automatic decision capture.
        
        Returns:
            True if hooks were setup successfully
        """
        try:
            return self.git_integration.setup_hooks()
        except Exception as e:
            logger.error(f"Failed to setup git hooks: {e}")
            return False

    def export_decisions(self, output_path: Union[str, Path]) -> bool:
        """
        Export all decisions to JSON file.
        
        Args:
            output_path: Path to export file
            
        Returns:
            True if export successful
        """
        try:
            decisions = self._load_all_decisions()
            decision_data = [decision.to_dict() for decision in decisions]
            
            with open(output_path, 'w') as f:
                json.dump({
                    'project': self.config.get('project_name', 'Unknown'),
                    'exported': datetime.now().isoformat(),
                    'decisions': decision_data
                }, f, indent=2, default=str)
            
            logger.info(f"Exported {len(decisions)} decisions to {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to export decisions: {e}")
            return False

    def generate_decision_report(self) -> str:
        """
        Generate comprehensive decision report.
        
        Returns:
            Markdown report of all decisions and analysis
        """
        decisions = self._load_all_decisions()
        insights = self.analyze_decisions()
        timeline = self.get_decision_timeline()
        milestones = self.get_project_milestones()
        
        # Generate report using template
        report = self.template_manager.generate_decision_report(
            project_name=self.config.get('project_name', 'Project'),
            decisions=decisions,
            insights=insights,
            timeline=timeline,
            milestones=milestones
        )
        
        return report

    def _create_project_structure(self, project_name: str):
        """Create the memory-bank directory structure."""
        # Create memory-bank directory
        self.memory_bank_dir.mkdir(exist_ok=True)
        
        # Create template files
        for template_name, template_content in self.template_manager.get_templates().items():
            template_path = self.memory_bank_dir / f"{template_name}.md"
            if not template_path.exists():
                with open(template_path, 'w') as f:
                    f.write(template_content)
        
        logger.info(f"Created memory-bank structure in {self.memory_bank_dir}")

    def _save_decision_to_file(self, decision: Decision):
        """Save decision to appropriate template file."""
        # Determine target file based on category
        file_mapping = {
            DecisionCategory.COMPONENT_SELECTION: 'decisions.md',
            DecisionCategory.ARCHITECTURE: 'decisions.md', 
            DecisionCategory.FABRICATION: 'fabrication.md',
            DecisionCategory.TESTING: 'testing.md',
            DecisionCategory.ISSUE: 'issues.md',
            DecisionCategory.MILESTONE: 'timeline.md'
        }
        
        target_file = file_mapping.get(decision.category, 'decisions.md')
        file_path = self.memory_bank_dir / target_file
        
        # Append decision to file
        decision_entry = f"""
## {decision.timestamp.strftime('%Y-%m-%d %H:%M')}: {decision.decision}

**Category**: {decision.category.value}  
**Impact**: {decision.impact.value}  
**Tags**: {', '.join(decision.tags)}

**Rationale**: {decision.rationale}

**Alternatives Considered**: {', '.join(decision.alternatives) if decision.alternatives else 'None'}

**Context**: {json.dumps(decision.context, indent=2) if decision.context else 'None'}

---
"""
        
        with open(file_path, 'a') as f:
            f.write(decision_entry)

    def _load_all_decisions(self) -> List[Decision]:
        """Load all decisions from memory-bank files."""
        decisions = []
        
        # Parse markdown files to extract decisions
        # This would implement markdown parsing to extract decision entries
        # For now, return empty list
        
        return decisions

    def _load_config(self) -> Dict[str, Any]:
        """Load memory-bank configuration."""
        if not self.config_file.exists():
            return {}
        
        try:
            with open(self.config_file, 'r') as f:
                return json.load(f)
        except Exception as e:
            logger.warning(f"Failed to load config: {e}")
            return {}

    def _save_config(self, config: Dict[str, Any]):
        """Save memory-bank configuration."""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(config, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    @property
    def is_initialized(self) -> bool:
        """Check if memory-bank is initialized in current project."""
        return self.memory_bank_dir.exists() and self.config_file.exists()

    @property
    def project_name(self) -> str:
        """Get project name from configuration."""
        return self.config.get('project_name', self.project_path.name)

    def get_statistics(self) -> Dict[str, Any]:
        """Get memory-bank statistics."""
        decisions = self._load_all_decisions()
        
        # Count by category
        category_counts = {}
        for decision in decisions:
            cat = decision.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        # Count by impact
        impact_counts = {}
        for decision in decisions:
            imp = decision.impact.value
            impact_counts[imp] = impact_counts.get(imp, 0) + 1
        
        return {
            'total_decisions': len(decisions),
            'by_category': category_counts,
            'by_impact': impact_counts,
            'project_name': self.project_name,
            'initialized': self.config.get('initialized'),
            'git_hooks_enabled': self.config.get('git_hooks_enabled', False)
        }