"""
Reward System for RL-enabled SWE Agent
Calculates rewards based on action outcomes and effectiveness.
"""

from typing import Dict, Any, List, Optional
import logging
from dataclasses import dataclass
from enum import Enum
import re


logger = logging.getLogger(__name__)


class RewardType(Enum):
    """Types of rewards in the system."""
    TOOL_SUCCESS = "tool_success"
    TOOL_FAILURE = "tool_failure"
    TASK_COMPLETION = "task_completion"
    CODE_QUALITY = "code_quality"
    EFFICIENCY = "efficiency"
    SECURITY = "security"
    COLLABORATION = "collaboration"


@dataclass
class RewardConfig:
    """Configuration for reward calculation."""
    # Base rewards
    successful_tool_use: float = 1.0
    failed_tool_use: float = -0.5
    task_completion: float = 10.0
    task_failure: float = -5.0
    
    # Quality bonuses
    clean_code_bonus: float = 2.0
    security_compliance_bonus: float = 3.0
    performance_optimization_bonus: float = 1.5
    
    # Efficiency rewards
    minimal_tool_calls_bonus: float = 1.0
    redundant_call_penalty: float = -1.0
    fast_completion_bonus: float = 2.0
    
    # Collaboration rewards
    effective_delegation_bonus: float = 1.5
    agent_coordination_bonus: float = 1.0


class RewardSystem:
    """
    Calculates rewards for agent actions in RL mode.
    """
    
    def __init__(self, config: Optional[RewardConfig] = None):
        self.config = config or RewardConfig()
        self.action_history: List[Dict[str, Any]] = []
        
    def calculate_tool_reward(
        self, 
        tool_name: str, 
        success: bool, 
        execution_time: float,
        tool_output: str,
        context: Dict[str, Any]
    ) -> float:
        """
        Calculate reward for individual tool usage.
        
        Args:
            tool_name: Name of the tool used
            success: Whether the tool execution was successful
            execution_time: Time taken to execute
            tool_output: Output from the tool
            context: Additional context information
            
        Returns:
            Calculated reward value
        """
        base_reward = self.config.successful_tool_use if success else self.config.failed_tool_use
        
        # Time-based efficiency bonus/penalty
        efficiency_modifier = 0.0
        if execution_time < 1.0:  # Fast execution
            efficiency_modifier = self.config.fast_completion_bonus * 0.1
        elif execution_time > 10.0:  # Slow execution
            efficiency_modifier = -0.5
            
        # Tool-specific bonuses
        tool_bonus = self._calculate_tool_specific_bonus(tool_name, tool_output, success)
        
        # Context-based modifiers
        context_modifier = self._calculate_context_modifier(tool_name, context)
        
        total_reward = base_reward + efficiency_modifier + tool_bonus + context_modifier
        
        logger.debug(f"Tool reward for {tool_name}: {total_reward} "
                    f"(base: {base_reward}, efficiency: {efficiency_modifier}, "
                    f"tool_bonus: {tool_bonus}, context: {context_modifier})")
        
        return total_reward
    
    def calculate_task_completion_reward(
        self,
        task_successful: bool,
        task_complexity: str,
        total_time: float,
        tool_calls_made: int,
        code_quality_score: float
    ) -> float:
        """
        Calculate reward for overall task completion.
        
        Args:
            task_successful: Whether the task was completed successfully
            task_complexity: Complexity level (simple, medium, complex)
            total_time: Total time taken
            tool_calls_made: Number of tool calls made
            code_quality_score: Quality score of generated code (0-1)
            
        Returns:
            Task completion reward
        """
        base_reward = self.config.task_completion if task_successful else self.config.task_failure
        
        # Complexity bonus
        complexity_multipliers = {
            'simple': 1.0,
            'medium': 1.5,
            'complex': 2.0,
            'expert': 3.0
        }
        complexity_bonus = base_reward * (complexity_multipliers.get(task_complexity, 1.0) - 1.0)
        
        # Efficiency bonus for minimal tool usage
        efficiency_bonus = 0.0
        if task_successful and tool_calls_made < 10:
            efficiency_bonus = self.config.minimal_tool_calls_bonus * (10 - tool_calls_made) * 0.1
        
        # Code quality bonus
        quality_bonus = code_quality_score * self.config.clean_code_bonus
        
        total_reward = base_reward + complexity_bonus + efficiency_bonus + quality_bonus
        
        logger.info(f"Task completion reward: {total_reward} "
                   f"(base: {base_reward}, complexity: {complexity_bonus}, "
                   f"efficiency: {efficiency_bonus}, quality: {quality_bonus})")
        
        return total_reward
    
    def calculate_collaboration_reward(
        self,
        agent_name: str,
        delegation_effective: bool,
        coordination_score: float
    ) -> float:
        """
        Calculate reward for multi-agent collaboration.
        
        Args:
            agent_name: Name of the agent
            delegation_effective: Whether delegation was effective
            coordination_score: Score for agent coordination (0-1)
            
        Returns:
            Collaboration reward
        """
        delegation_reward = (self.config.effective_delegation_bonus 
                           if delegation_effective else -0.5)
        coordination_reward = coordination_score * self.config.agent_coordination_bonus
        
        return delegation_reward + coordination_reward
    
    def _calculate_tool_specific_bonus(
        self, 
        tool_name: str, 
        tool_output: str, 
        success: bool
    ) -> float:
        """Calculate bonuses specific to certain tools."""
        if not success:
            return 0.0
            
        bonus = 0.0
        
        # Security tool bonuses
        if 'security' in tool_name.lower() or 'scan' in tool_name.lower():
            if 'vulnerability' in tool_output.lower() or 'security' in tool_output.lower():
                bonus += self.config.security_compliance_bonus * 0.5
                
        # Code analysis bonuses
        if 'analyze' in tool_name.lower():
            if len(tool_output) > 100:  # Detailed analysis
                bonus += 0.5
                
        # File operation efficiency
        if tool_name in ['create_file', 'edit_file', 'replace_in_file']:
            if 'error' not in tool_output.lower():
                bonus += 0.3
                
        return bonus
    
    def _calculate_context_modifier(
        self, 
        tool_name: str, 
        context: Dict[str, Any]
    ) -> float:
        """Calculate context-based reward modifiers."""
        modifier = 0.0
        
        # Recent tool usage patterns
        recent_tools = context.get('recent_tools', [])
        if tool_name in recent_tools[-3:]:  # Used in last 3 actions
            modifier -= self.config.redundant_call_penalty * 0.3
            
        # Task urgency
        if context.get('urgent', False):
            modifier += 0.5
            
        # Learning phase
        if context.get('learning_phase', False):
            modifier += 0.2  # Encourage exploration during learning
            
        return modifier
    
    def calculate_code_quality_score(self, code: str, language: str) -> float:
        """
        Analyze code quality and return a score between 0 and 1.
        
        Args:
            code: Code to analyze
            language: Programming language
            
        Returns:
            Quality score between 0 and 1
        """
        if not code:
            return 0.0
            
        score = 0.5  # Start with neutral score
        
        # Basic quality checks
        lines = code.split('\n')
        
        # Check for comments
        comment_ratio = sum(1 for line in lines if line.strip().startswith('#') or 
                           line.strip().startswith('//') or 
                           '"""' in line or "'''" in line) / max(len(lines), 1)
        score += min(comment_ratio * 0.2, 0.1)
        
        # Check for proper naming (no single-letter variables in long code)
        if len(code) > 200:
            single_letter_vars = len(re.findall(r'\b[a-z]\s*=', code))
            if single_letter_vars < 3:
                score += 0.1
                
        # Check for error handling
        if 'try:' in code or 'except' in code or 'catch' in code:
            score += 0.1
            
        # Check for function definitions
        if 'def ' in code or 'function ' in code:
            score += 0.1
            
        # Penalize very long functions
        if len(code) > 1000 and code.count('def ') < 2:
            score -= 0.1
            
        return max(0.0, min(1.0, score))
    
    def get_reward_summary(self) -> Dict[str, Any]:
        """Get a summary of recent rewards and patterns."""
        if not self.action_history:
            return {}
            
        total_actions = len(self.action_history)
        successful_actions = sum(1 for a in self.action_history if getattr(a, 'success', False))
        
        return {
            'total_actions': total_actions,
            'success_rate': successful_actions / total_actions,
            'average_reward': sum(getattr(a, 'reward_value', 0) for a in self.action_history) / total_actions,
            'recent_trend': self._calculate_recent_trend()
        }
    
    def _calculate_recent_trend(self) -> str:
        """Calculate the recent performance trend."""
        if len(self.action_history) < 5:
            return "insufficient_data"
            
        recent_rewards = [getattr(a, 'reward_value', 0) for a in self.action_history[-5:]]
        earlier_rewards = [getattr(a, 'reward_value', 0) for a in self.action_history[-10:-5]]
        
        if not earlier_rewards:
            return "new_session"
            
        recent_avg = sum(recent_rewards) / len(recent_rewards)
        earlier_avg = sum(earlier_rewards) / len(earlier_rewards)
        
        if recent_avg > earlier_avg * 1.1:
            return "improving"
        elif recent_avg < earlier_avg * 0.9:
            return "declining"
        else:
            return "stable"