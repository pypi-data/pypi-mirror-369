"""
AI-powered decision analysis for memory-bank system.

This module provides intelligent analysis of engineering decisions using AI models
to generate insights, recommendations, and pattern recognition.
"""

import json
import logging
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..core.decision import Decision, DecisionCategory, DecisionImpact
from ..utils.exceptions import MemoryBankError

logger = logging.getLogger(__name__)


@dataclass
class AIInsights:
    """AI-generated insights about engineering decisions."""
    
    confidence_score: float  # 0-10 overall confidence in decisions
    risk_factors: List[str]  # Identified risk factors
    recommendations: List[Dict[str, Any]]  # AI recommendations
    patterns: List[Dict[str, Any]]  # Decision patterns identified
    success_indicators: List[str]  # Positive patterns
    improvement_areas: List[str]  # Areas for improvement
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert insights to dictionary."""
        return {
            'confidence_score': self.confidence_score,
            'risk_factors': self.risk_factors,
            'recommendations': self.recommendations,
            'patterns': self.patterns,
            'success_indicators': self.success_indicators,
            'improvement_areas': self.improvement_areas,
            'generated_at': datetime.now().isoformat()
        }


class DecisionAnalyzer:
    """
    AI-powered analysis engine for engineering decisions.
    
    Features:
    - Decision confidence scoring
    - Risk factor identification
    - Pattern recognition across decisions
    - Recommendation generation
    - Cross-project learning
    """
    
    def __init__(self, ai_provider: str = "mock"):
        """
        Initialize decision analyzer.
        
        Args:
            ai_provider: AI provider to use ('claude', 'openai', or 'mock')
        """
        self.ai_provider = ai_provider
        self._setup_ai_client()
        
        logger.debug(f"DecisionAnalyzer initialized with provider: {ai_provider}")
    
    def analyze_decisions(self, decisions: List[Decision]) -> AIInsights:
        """
        Analyze a collection of decisions for insights.
        
        Args:
            decisions: List of decisions to analyze
            
        Returns:
            AI insights about the decisions
        """
        if not decisions:
            return AIInsights(
                confidence_score=0.0,
                risk_factors=["No decisions to analyze"],
                recommendations=[],
                patterns=[],
                success_indicators=[],
                improvement_areas=["Start documenting decisions"]
            )
        
        logger.info(f"Analyzing {len(decisions)} decisions")
        
        # Basic analysis (mock implementation)
        confidence = self._calculate_confidence_score(decisions)
        risks = self._identify_risk_factors(decisions)
        patterns = self._find_decision_patterns(decisions)
        recommendations = self._generate_recommendations(decisions)
        success_indicators = self._find_success_indicators(decisions)
        improvements = self._identify_improvement_areas(decisions)
        
        return AIInsights(
            confidence_score=confidence,
            risk_factors=risks,
            recommendations=recommendations,
            patterns=patterns,
            success_indicators=success_indicators,
            improvement_areas=improvements
        )
    
    def find_similar_decisions(self, query: str, decisions: List[Decision]) -> List[Decision]:
        """
        Find decisions similar to the query using AI similarity matching.
        
        Args:
            query: Description of decision type to find
            decisions: List of decisions to search
            
        Returns:
            List of similar decisions
        """
        # Simple text-based similarity for mock implementation
        query_lower = query.lower()
        similar = []
        
        for decision in decisions:
            decision_text = f"{decision.decision} {decision.rationale}".lower()
            
            # Basic keyword matching (would use AI embeddings in real implementation)
            if any(word in decision_text for word in query_lower.split()):
                similar.append(decision)
        
        # Sort by relevance (mock scoring)
        similar.sort(key=lambda d: len([w for w in query_lower.split() 
                                      if w in f"{d.decision} {d.rationale}".lower()]), 
                    reverse=True)
        
        return similar[:10]  # Top 10 matches
    
    def get_decision_recommendations(self, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Get AI recommendations for a specific decision context.
        
        Args:
            context: Context information for recommendation generation
            
        Returns:
            List of AI-generated recommendations
        """
        recommendations = []
        
        # Mock recommendations based on context
        decision_type = context.get('category', 'unknown')
        
        if decision_type == 'component_selection':
            recommendations.extend([
                {
                    'type': 'process_improvement',
                    'suggestion': 'Consider documenting supply chain alternatives',
                    'confidence': 0.8,
                    'rationale': 'Supply chain resilience is critical for component decisions'
                },
                {
                    'type': 'validation',
                    'suggestion': 'Add cost analysis to component selection rationale',
                    'confidence': 0.7,
                    'rationale': 'Cost tracking helps with future similar decisions'
                }
            ])
        
        return recommendations
    
    def _setup_ai_client(self):
        """Setup AI client based on provider."""
        if self.ai_provider == "claude":
            try:
                import anthropic
                api_key = os.getenv("ANTHROPIC_API_KEY")
                if api_key:
                    self.client = anthropic.Anthropic(api_key=api_key)
                else:
                    logger.warning("ANTHROPIC_API_KEY not found, using mock analysis")
                    self.client = None
            except ImportError:
                logger.warning("anthropic package not installed, using mock analysis")
                self.client = None
        
        elif self.ai_provider == "openai":
            try:
                import openai
                api_key = os.getenv("OPENAI_API_KEY")
                if api_key:
                    self.client = openai.OpenAI(api_key=api_key)
                else:
                    logger.warning("OPENAI_API_KEY not found, using mock analysis")
                    self.client = None
            except ImportError:
                logger.warning("openai package not installed, using mock analysis")
                self.client = None
        
        else:
            # Mock provider
            self.client = None
    
    def _calculate_confidence_score(self, decisions: List[Decision]) -> float:
        """Calculate overall confidence score for decisions."""
        if not decisions:
            return 0.0
        
        # Mock confidence scoring based on decision characteristics
        total_score = 0.0
        
        for decision in decisions:
            score = 5.0  # Base score
            
            # Boost for detailed rationale
            if len(decision.rationale) > 50:
                score += 1.5
            
            # Boost for alternatives considered
            if decision.alternatives:
                score += 1.0
            
            # Boost for validation
            if decision.status.value == "validated":
                score += 1.0
            
            # Boost for appropriate impact assessment
            if decision.is_high_impact and len(decision.rationale) > 100:
                score += 0.5
            
            total_score += min(score, 10.0)
        
        return round(total_score / len(decisions), 1)
    
    def _identify_risk_factors(self, decisions: List[Decision]) -> List[str]:
        """Identify risk factors in decision set."""
        risks = []
        
        # Check for high-impact decisions without validation
        unvalidated_high_impact = [d for d in decisions 
                                  if d.is_high_impact and d.status.value != "validated"]
        if unvalidated_high_impact:
            risks.append(f"{len(unvalidated_high_impact)} high-impact decisions lack validation")
        
        # Check for decisions without alternatives
        no_alternatives = [d for d in decisions if not d.alternatives]
        if len(no_alternatives) > len(decisions) * 0.5:
            risks.append("Many decisions lack alternative analysis")
        
        # Check for decision clustering (too many decisions too quickly)
        recent_decisions = [d for d in decisions if d.is_recent]
        if len(recent_decisions) > 20:
            risks.append("High decision velocity may indicate rushed decision-making")
        
        return risks
    
    def _find_decision_patterns(self, decisions: List[Decision]) -> List[Dict[str, Any]]:
        """Find patterns in decision history."""
        patterns = []
        
        # Category clustering
        category_counts = {}
        for decision in decisions:
            cat = decision.category.value
            category_counts[cat] = category_counts.get(cat, 0) + 1
        
        if category_counts:
            most_common = max(category_counts.items(), key=lambda x: x[1])
            patterns.append({
                'type': 'category_focus',
                'pattern': f"Heavy focus on {most_common[0]} decisions",
                'data': category_counts
            })
        
        return patterns
    
    def _generate_recommendations(self, decisions: List[Decision]) -> List[Dict[str, Any]]:
        """Generate AI recommendations based on decision analysis."""
        recommendations = []
        
        # Process improvement recommendations
        decisions_without_rationale = [d for d in decisions if len(d.rationale) < 20]
        if len(decisions_without_rationale) > 5:
            recommendations.append({
                'type': 'process_improvement',
                'suggestion': 'Improve decision documentation with detailed rationale',
                'confidence': 0.9,
                'affected_decisions': len(decisions_without_rationale)
            })
        
        # Validation recommendations
        unvalidated = [d for d in decisions if d.status.value in ('proposed', 'approved')]
        if unvalidated:
            recommendations.append({
                'type': 'validation',
                'suggestion': 'Implement validation tracking for pending decisions',
                'confidence': 0.8,
                'affected_decisions': len(unvalidated)
            })
        
        return recommendations
    
    def _find_success_indicators(self, decisions: List[Decision]) -> List[str]:
        """Find positive patterns in decisions."""
        indicators = []
        
        validated_decisions = [d for d in decisions if d.status.value == "validated"]
        if len(validated_decisions) > len(decisions) * 0.7:
            indicators.append("High validation rate indicates good decision follow-through")
        
        detailed_decisions = [d for d in decisions if len(d.rationale) > 100]
        if len(detailed_decisions) > len(decisions) * 0.5:
            indicators.append("Detailed rationale documentation shows thorough analysis")
        
        return indicators
    
    def _identify_improvement_areas(self, decisions: List[Decision]) -> List[str]:
        """Identify areas for improvement in decision processes."""
        improvements = []
        
        # Check alternative analysis
        no_alternatives = [d for d in decisions if not d.alternatives]
        if len(no_alternatives) > len(decisions) * 0.3:
            improvements.append("Consider documenting alternatives for more decisions")
        
        # Check impact assessment
        medium_impact_only = [d for d in decisions if d.impact == DecisionImpact.MEDIUM]
        if len(medium_impact_only) > len(decisions) * 0.8:
            improvements.append("Review impact assessment - may need more high/low classifications")
        
        return improvements