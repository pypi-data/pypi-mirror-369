#!/usr/bin/env python3
"""
Python MCP interface for memory-bank.

This script provides the Python side of the MCP bridge, handling commands
from the TypeScript MCP server and executing them using memory-bank.
"""

import json
import logging
import sys
import traceback
from typing import Any, Dict, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(name)s: %(message)s',
    handlers=[logging.StreamHandler(sys.stderr)]
)

logger = logging.getLogger('memory_bank.mcp')

# Import memory-bank components
try:
    from ..core.memory_bank import MemoryBank
    from ..core.decision import Decision, DecisionCategory, DecisionImpact
    from ..ai.analyzer import DecisionAnalyzer
    from ..utils.exceptions import MemoryBankError
except ImportError as e:
    logger.error(f"Failed to import memory-bank modules: {e}")
    sys.exit(1)


class MCPInterface:
    """MCP command interface for memory-bank."""
    
    def __init__(self):
        """Initialize the MCP interface."""
        self.current_bank: Optional[MemoryBank] = None
        
        # Command handlers
        self.handlers = {
            'ping': self.ping,
            'init_memory_bank': self.init_memory_bank,
            'log_decision': self.log_decision,
            'log_test_result': self.log_test_result,
            'search_decisions': self.search_decisions,
            'analyze_decisions': self.analyze_decisions,
            'get_recommendations': self.get_recommendations,
            'get_timeline': self.get_timeline,
            'get_milestones': self.get_milestones,
            'export_decisions': self.export_decisions,
            'get_statistics': self.get_statistics,
            'setup_git_hooks': self.setup_git_hooks,
        }
        
        logger.info("Memory-bank MCP interface initialized")

    def ping(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Health check command."""
        return {
            'success': True,
            'message': 'memory-bank MCP interface is ready',
            'version': '0.0.1'
        }

    def init_memory_bank(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize memory-bank in project."""
        try:
            project_path = params.get('project_path', '.')
            project_name = params.get('project_name')
            
            self.current_bank = MemoryBank.init_project(project_path, project_name)
            
            return {
                'success': True,
                'message': f'Memory-bank initialized for project: {self.current_bank.project_name}',
                'project_path': str(self.current_bank.project_path),
                'project_name': self.current_bank.project_name
            }
        except Exception as e:
            logger.error(f"Error initializing memory-bank: {e}")
            return {'success': False, 'error': str(e)}

    def log_decision(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Log an engineering decision."""
        try:
            if not self.current_bank:
                # Try to get current project
                try:
                    self.current_bank = MemoryBank.current_project()
                except:
                    return {'success': False, 'error': 'No memory-bank initialized'}

            category = params.get('category')
            decision = params.get('decision')
            rationale = params.get('rationale', '')
            
            if not category or not decision:
                return {'success': False, 'error': 'category and decision parameters required'}

            # Create decision
            decision_obj = self.current_bank.log_decision(
                category=category,
                decision=decision,
                rationale=rationale,
                alternatives=params.get('alternatives', []),
                impact=params.get('impact', 'medium'),
                tags=params.get('tags', []),
                context=params.get('context', {})
            )

            return {
                'success': True,
                'message': f'Decision logged: {decision}',
                'decision': decision_obj.to_dict()
            }
        except Exception as e:
            logger.error(f"Error logging decision: {e}")
            return {'success': False, 'error': str(e)}

    def log_test_result(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Log test results as a decision."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            test_name = params.get('test_name')
            result = params.get('result')
            meets_spec = params.get('meets_spec', True)
            notes = params.get('notes', '')

            if not test_name or not result:
                return {'success': False, 'error': 'test_name and result parameters required'}

            decision_obj = self.current_bank.log_test_result(
                test_name=test_name,
                result=result,
                meets_spec=meets_spec,
                notes=notes
            )

            return {
                'success': True,
                'message': f'Test result logged: {test_name}',
                'decision': decision_obj.to_dict()
            }
        except Exception as e:
            logger.error(f"Error logging test result: {e}")
            return {'success': False, 'error': str(e)}

    def search_decisions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Search decision history."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            query = params.get('query')
            if not query:
                return {'success': False, 'error': 'query parameter required'}

            category = params.get('category')
            tags = params.get('tags')
            
            decisions = self.current_bank.search_decisions(
                query=query,
                category=category,
                tags=tags
            )

            return {
                'success': True,
                'count': len(decisions),
                'decisions': [decision.to_dict() for decision in decisions]
            }
        except Exception as e:
            logger.error(f"Error searching decisions: {e}")
            return {'success': False, 'error': str(e)}

    def analyze_decisions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI analysis of decisions."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            insights = self.current_bank.analyze_decisions()

            return {
                'success': True,
                'insights': insights.to_dict()
            }
        except Exception as e:
            logger.error(f"Error analyzing decisions: {e}")
            return {'success': False, 'error': str(e)}

    def get_recommendations(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get AI recommendations."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            recommendations = self.current_bank.get_ai_recommendations()

            return {
                'success': True,
                'count': len(recommendations),
                'recommendations': recommendations
            }
        except Exception as e:
            logger.error(f"Error getting recommendations: {e}")
            return {'success': False, 'error': str(e)}

    def get_timeline(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get decision timeline."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            timeline = self.current_bank.get_decision_timeline()

            return {
                'success': True,
                'timeline': timeline
            }
        except Exception as e:
            logger.error(f"Error getting timeline: {e}")
            return {'success': False, 'error': str(e)}

    def get_milestones(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get project milestones."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            milestones = self.current_bank.get_project_milestones()

            return {
                'success': True,
                'count': len(milestones),
                'milestones': milestones
            }
        except Exception as e:
            logger.error(f"Error getting milestones: {e}")
            return {'success': False, 'error': str(e)}

    def export_decisions(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Export decisions to file."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            output_path = params.get('output_path', 'decisions.json')
            
            success = self.current_bank.export_decisions(output_path)

            return {
                'success': success,
                'message': f'Decisions exported to: {output_path}' if success else 'Export failed'
            }
        except Exception as e:
            logger.error(f"Error exporting decisions: {e}")
            return {'success': False, 'error': str(e)}

    def get_statistics(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Get memory-bank statistics."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            stats = self.current_bank.get_statistics()

            return {
                'success': True,
                'statistics': stats
            }
        except Exception as e:
            logger.error(f"Error getting statistics: {e}")
            return {'success': False, 'error': str(e)}

    def setup_git_hooks(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Setup git hooks for automatic decision capture."""
        try:
            if not self.current_bank:
                self.current_bank = MemoryBank.current_project()

            success = self.current_bank.setup_git_hooks()

            return {
                'success': success,
                'message': 'Git hooks setup successfully' if success else 'Git hooks setup failed'
            }
        except Exception as e:
            logger.error(f"Error setting up git hooks: {e}")
            return {'success': False, 'error': str(e)}

    def process_commands(self):
        """Main command processing loop."""
        logger.info("Starting command processing loop")
        
        try:
            for line in sys.stdin:
                try:
                    # Parse command
                    request = json.loads(line.strip())
                    command = request.get('command')
                    params = request.get('params', {})
                    request_id = request.get('id')

                    # Execute command
                    if command in self.handlers:
                        result = self.handlers[command](params)
                    else:
                        result = {
                            'success': False,
                            'error': f'Unknown command: {command}'
                        }

                    # Send response
                    response = {
                        'id': request_id,
                        'result': result
                    }
                    
                    print(json.dumps(response))
                    sys.stdout.flush()

                except json.JSONDecodeError as e:
                    logger.error(f"Invalid JSON input: {e}")
                    error_response = {
                        'id': None,
                        'error': f'Invalid JSON: {e}'
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

                except Exception as e:
                    logger.error(f"Error processing command: {e}")
                    logger.debug(traceback.format_exc())
                    error_response = {
                        'id': request.get('id') if 'request' in locals() else None,
                        'error': str(e)
                    }
                    print(json.dumps(error_response))
                    sys.stdout.flush()

        except KeyboardInterrupt:
            logger.info("Received interrupt signal")
        except Exception as e:
            logger.error(f"Fatal error in command processing: {e}")
            logger.debug(traceback.format_exc())
        finally:
            logger.info("Command processing stopped")


def main():
    """Main entry point."""
    interface = MCPInterface()
    interface.process_commands()


if __name__ == '__main__':
    main()