"""
Git integration for memory-bank system.

This module provides automatic decision capture via git hooks and commit analysis,
enabling seamless integration with existing development workflows.
"""

import logging
import os
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import git
from git import Repo

from ..core.decision import Decision, DecisionCategory, DecisionImpact
from ..utils.exceptions import MemoryBankError

logger = logging.getLogger(__name__)


class GitIntegration:
    """
    Git integration for automatic decision capture and analysis.
    
    Features:
    - Automatic git hook installation
    - Commit message analysis for decision extraction
    - Change analysis and impact assessment
    - Timeline reconstruction from git history
    """

    def __init__(self, project_path: Union[str, Path]):
        """
        Initialize git integration.
        
        Args:
            project_path: Path to project directory
        """
        self.project_path = Path(project_path)
        self.git_dir = self.project_path / ".git"
        self.hooks_dir = self.git_dir / "hooks"
        
        # Initialize git repository
        try:
            self.repo = Repo(self.project_path)
        except Exception as e:
            raise MemoryBankError(f"Not a git repository: {e}")
        
        logger.debug(f"Git integration initialized for: {self.project_path}")

    def setup_hooks(self) -> bool:
        """
        Setup git hooks for automatic memory-bank updates.
        
        Returns:
            True if hooks were setup successfully
        """
        try:
            self.hooks_dir.mkdir(exist_ok=True)
            
            # Install post-commit hook
            success = self._install_post_commit_hook()
            
            if success:
                logger.info("Git hooks installed successfully")
            else:
                logger.error("Failed to install git hooks")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to setup git hooks: {e}")
            return False

    def remove_hooks(self) -> bool:
        """
        Remove memory-bank git hooks.
        
        Returns:
            True if hooks were removed successfully
        """
        try:
            hook_file = self.hooks_dir / "post-commit"
            
            if hook_file.exists():
                # Check if it's our hook
                with open(hook_file, 'r') as f:
                    content = f.read()
                
                if "memory-bank system" in content:
                    hook_file.unlink()
                    logger.info("Removed memory-bank post-commit hook")
                    return True
                else:
                    logger.warning("Post-commit hook exists but not created by memory-bank")
                    return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to remove git hooks: {e}")
            return False

    def analyze_commit(self, commit_hash: str) -> Optional[Decision]:
        """
        Analyze a commit for decision content.
        
        Args:
            commit_hash: Git commit hash to analyze
            
        Returns:
            Decision object if decision found in commit, None otherwise
        """
        try:
            commit = self.repo.commit(commit_hash)
            
            # Analyze commit message for decision indicators
            decision_data = self._extract_decision_from_commit(commit)
            
            if decision_data:
                return Decision(**decision_data)
            
            return None
            
        except Exception as e:
            logger.error(f"Failed to analyze commit {commit_hash}: {e}")
            return None

    def get_commit_history(self, since: Optional[datetime] = None, 
                          max_count: int = 100) -> List[git.Commit]:
        """
        Get commit history for analysis.
        
        Args:
            since: Only commits after this date
            max_count: Maximum number of commits to return
            
        Returns:
            List of git commits
        """
        try:
            commits = list(self.repo.iter_commits(max_count=max_count))
            
            if since:
                commits = [c for c in commits if c.committed_datetime >= since]
            
            return commits
            
        except Exception as e:
            logger.error(f"Failed to get commit history: {e}")
            return []

    def extract_decisions_from_history(self, 
                                     since: Optional[datetime] = None,
                                     max_commits: int = 100) -> List[Decision]:
        """
        Extract decisions from git commit history.
        
        Args:
            since: Only analyze commits after this date
            max_commits: Maximum commits to analyze
            
        Returns:
            List of decisions extracted from commits
        """
        commits = self.get_commit_history(since, max_commits)
        decisions = []
        
        for commit in commits:
            decision = self.analyze_commit(commit.hexsha)
            if decision:
                decisions.append(decision)
        
        logger.info(f"Extracted {len(decisions)} decisions from {len(commits)} commits")
        return decisions

    def _install_post_commit_hook(self) -> bool:
        """Install post-commit hook for automatic updates."""
        hook_script = '''#!/bin/bash
# Memory-Bank automatic update hook
# Generated by memory-bank system

# Get the latest commit hash
COMMIT_HASH=$(git rev-parse HEAD)

# Check if memory-bank system is enabled
if [ -f ".memory-bank-config.json" ]; then
    echo "🧠 Updating memory-bank for commit $COMMIT_HASH"
    
    # Try to update memory-bank using Python
    python3 -c "
import memory_bank as mb
try:
    bank = mb.current_project()
    decision = bank.git_integration.analyze_commit('$COMMIT_HASH')
    if decision:
        print(f'📝 Captured decision: {decision.decision[:50]}...')
    else:
        print('ℹ️  No decision captured from commit')
except Exception as e:
    print(f'⚠️  Memory-bank update failed: {e}')
" 2>/dev/null || echo "⚠️  Memory-bank update failed (continuing)"
else
    # Memory-bank not enabled, exit silently
    exit 0
fi
'''
        
        try:
            hook_file = self.hooks_dir / "post-commit"
            
            with open(hook_file, 'w') as f:
                f.write(hook_script)
            
            # Make executable
            hook_file.chmod(0o755)
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to install post-commit hook: {e}")
            return False

    def _extract_decision_from_commit(self, commit: git.Commit) -> Optional[Dict[str, Any]]:
        """Extract decision data from commit message and changes."""
        message = commit.message.strip()
        
        # Decision indicators in commit messages
        decision_keywords = {
            'switch to', 'change to', 'selected', 'chose', 'decided',
            'replaced', 'upgraded', 'downgraded', 'optimized'
        }
        
        # Check if commit message contains decision indicators
        message_lower = message.lower()
        has_decision_keyword = any(keyword in message_lower for keyword in decision_keywords)
        
        if not has_decision_keyword:
            return None
        
        # Extract decision category from file changes
        category = self._categorize_commit_changes(commit)
        
        # Extract rationale from commit message
        rationale = self._extract_rationale_from_message(message)
        
        # Determine impact based on files changed
        impact = self._assess_commit_impact(commit)
        
        return {
            'category': category,
            'decision': message.split('\n')[0],  # First line of commit
            'rationale': rationale,
            'impact': impact,
            'tags': ['git-auto', 'commit'],
            'context': {
                'commit_hash': commit.hexsha,
                'author': str(commit.author),
                'files_changed': [item.a_path for item in commit.stats.files.keys()]
            },
            'timestamp': commit.committed_datetime
        }

    def _categorize_commit_changes(self, commit: git.Commit) -> DecisionCategory:
        """Categorize decision based on changed files."""
        try:
            changed_files = list(commit.stats.files.keys())
        except:
            return DecisionCategory.OTHER
        
        # Analyze file patterns
        for file_path in changed_files:
            file_lower = file_path.lower()
            
            if any(pattern in file_lower for pattern in ['power', 'supply', 'regulator']):
                return DecisionCategory.POWER_SUPPLY
            elif any(pattern in file_lower for pattern in ['test', 'spec', 'validation']):
                return DecisionCategory.TESTING
            elif any(pattern in file_lower for pattern in ['component', 'part', 'bom']):
                return DecisionCategory.COMPONENT_SELECTION
            elif any(pattern in file_lower for pattern in ['pcb', 'layout', 'routing']):
                return DecisionCategory.FABRICATION
            elif file_lower.endswith('.md'):
                return DecisionCategory.ARCHITECTURE
        
        return DecisionCategory.OTHER

    def _extract_rationale_from_message(self, message: str) -> str:
        """Extract rationale from commit message."""
        lines = message.split('\n')
        
        # Look for rationale indicators
        rationale_lines = []
        for line in lines[1:]:  # Skip first line (summary)
            line = line.strip()
            if not line:
                continue
            
            # Common rationale patterns
            if any(indicator in line.lower() for indicator in 
                   ['because', 'due to', 'for', 'to improve', 'to fix', 'vs', 'better']):
                rationale_lines.append(line)
        
        return ' '.join(rationale_lines) if rationale_lines else ""

    def _assess_commit_impact(self, commit: git.Commit) -> DecisionImpact:
        """Assess impact level based on commit changes."""
        try:
            stats = commit.stats
            total_changes = stats.total['insertions'] + stats.total['deletions']
            files_changed = len(stats.files)
            
            # High impact: Many files or major changes
            if files_changed > 10 or total_changes > 500:
                return DecisionImpact.HIGH
            elif files_changed > 5 or total_changes > 100:
                return DecisionImpact.MEDIUM
            else:
                return DecisionImpact.LOW
                
        except:
            return DecisionImpact.MEDIUM


class GitHooks:
    """Git hooks management for memory-bank automation."""
    
    def __init__(self, project_path: Union[str, Path]):
        self.integration = GitIntegration(project_path)
    
    def install(self) -> bool:
        """Install all memory-bank git hooks."""
        return self.integration.setup_hooks()
    
    def remove(self) -> bool:
        """Remove all memory-bank git hooks."""
        return self.integration.remove_hooks()
    
    def is_installed(self) -> bool:
        """Check if git hooks are installed."""
        hook_file = self.integration.hooks_dir / "post-commit"
        if not hook_file.exists():
            return False
        
        with open(hook_file, 'r') as f:
            content = f.read()
        
        return "memory-bank system" in content


def update_memory_bank_from_commit(commit_hash: str) -> bool:
    """
    Update memory-bank from a specific commit.
    
    This function is called by git hooks to automatically update
    memory-bank when commits are made.
    
    Args:
        commit_hash: Git commit hash to analyze
        
    Returns:
        True if update was successful
    """
    try:
        from ..core.memory_bank import MemoryBank
        
        # Get current project memory bank
        bank = MemoryBank.current_project()
        
        # Analyze commit for decisions
        decision = bank.git_integration.analyze_commit(commit_hash)
        
        if decision:
            # Decision was extracted, it's already been logged
            logger.info(f"Captured decision from commit {commit_hash[:8]}")
            return True
        else:
            logger.debug(f"No decision found in commit {commit_hash[:8]}")
            return True
            
    except Exception as e:
        logger.error(f"Failed to update memory-bank from commit {commit_hash}: {e}")
        return False