"""
Reinforcement Learning State Management for SWE Agent
Extends the base agent state to include RL-specific information.
"""

from typing import Dict, Any, List, Optional, TypedDict
from dataclasses import dataclass
from langchain_core.messages import BaseMessage
import time


@dataclass
class ActionReward:
    """Represents a reward for a specific action."""
    action_type: str
    tool_name: str
    reward_value: float
    timestamp: float
    success: bool
    context: Dict[str, Any]


@dataclass
class EpisodeHistory:
    """Tracks the history of actions and rewards in an episode."""
    episode_id: str
    actions: List[ActionReward]
    total_reward: float
    success_rate: float
    completion_time: float
    task_complexity: str


class RLAgentState(TypedDict):
    """
    Enhanced agent state for reinforcement learning mode.
    Includes all base state plus RL-specific tracking.
    """
    # Base agent state
    messages: List[BaseMessage]
    sender: str
    consecutive_visits: Dict[str, int]
    
    # RL-specific state
    rl_enabled: bool
    current_episode_id: str
    action_history: List[ActionReward]
    cumulative_reward: float
    episode_count: int
    success_episodes: int
    
    # Learning parameters
    exploration_rate: float
    learning_rate: float
    reward_decay: float
    
    # Performance tracking
    tool_success_rates: Dict[str, float]
    action_preferences: Dict[str, float]
    recent_episodes: List[EpisodeHistory]
    
    # Context awareness
    task_type: str
    complexity_level: str
    previous_similar_tasks: List[Dict[str, Any]]


def create_rl_state(base_state: Dict[str, Any]) -> RLAgentState:
    """
    Create an RL-enhanced state from a base state.
    
    Args:
        base_state: Basic agent state
        
    Returns:
        Enhanced RL agent state
    """
    return RLAgentState(
        # Base state
        messages=base_state.get('messages', []),
        sender=base_state.get('sender', ''),
        consecutive_visits=base_state.get('consecutive_visits', {}),
        
        # RL-specific initialization
        rl_enabled=True,
        current_episode_id=f"episode_{int(time.time())}",
        action_history=[],
        cumulative_reward=0.0,
        episode_count=0,
        success_episodes=0,
        
        # Learning parameters (hyperparameters)
        exploration_rate=0.3,  # 30% exploration
        learning_rate=0.1,     # Conservative learning
        reward_decay=0.95,     # Slight decay for temporal difference
        
        # Performance tracking
        tool_success_rates={},
        action_preferences={},
        recent_episodes=[],
        
        # Context
        task_type="general",
        complexity_level="medium",
        previous_similar_tasks=[]
    )


def update_rl_state_with_reward(state: RLAgentState, action: ActionReward) -> RLAgentState:
    """
    Update the RL state with a new action and its reward.
    
    Args:
        state: Current RL state
        action: Action with reward information
        
    Returns:
        Updated RL state
    """
    # Add action to history
    state['action_history'].append(action)
    
    # Update cumulative reward
    state['cumulative_reward'] += action.reward_value
    
    # Update tool success rates
    tool_name = action.tool_name
    if tool_name not in state['tool_success_rates']:
        state['tool_success_rates'][tool_name] = 0.5  # Start neutral
    
    # Update success rate using moving average
    current_rate = state['tool_success_rates'][tool_name]
    success_weight = 1.0 if action.success else 0.0
    state['tool_success_rates'][tool_name] = (
        current_rate * 0.8 + success_weight * 0.2
    )
    
    # Update action preferences based on reward
    action_type = action.action_type
    if action_type not in state['action_preferences']:
        state['action_preferences'][action_type] = 0.0
    
    # Positive rewards increase preference, negative decrease
    preference_update = action.reward_value * state['learning_rate']
    state['action_preferences'][action_type] += preference_update
    
    # Apply exploration decay
    if action.success:
        state['exploration_rate'] *= 0.995  # Slight decay on success
    
    return state


def calculate_episode_metrics(state: RLAgentState) -> Dict[str, float]:
    """
    Calculate performance metrics for the current episode.
    
    Args:
        state: Current RL state
        
    Returns:
        Dictionary of calculated metrics
    """
    if not state['action_history']:
        return {}
    
    actions = state['action_history']
    total_actions = len(actions)
    successful_actions = sum(1 for a in actions if a.success)
    
    return {
        'success_rate': successful_actions / total_actions if total_actions > 0 else 0.0,
        'average_reward': state['cumulative_reward'] / total_actions if total_actions > 0 else 0.0,
        'total_reward': state['cumulative_reward'],
        'action_count': total_actions,
        'exploration_rate': state['exploration_rate']
    }