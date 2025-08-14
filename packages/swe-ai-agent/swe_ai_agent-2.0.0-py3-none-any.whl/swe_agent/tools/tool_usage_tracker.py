"""
Tool Usage Tracker - Tracks which tools are used by which agents
Provides insights into agent behavior and tool utilization patterns.
"""

import logging
import time
from typing import Dict, List, Any, Optional
from collections import defaultdict, Counter
from dataclasses import dataclass, field
from datetime import datetime

logger = logging.getLogger(__name__)

@dataclass
class ToolUsage:
    """Represents a single tool usage event."""
    agent_name: str
    tool_name: str
    timestamp: float
    duration: Optional[float] = None
    success: bool = True
    error_message: Optional[str] = None
    parameters: Dict[str, Any] = field(default_factory=dict)
    result_summary: Optional[str] = None

class ToolUsageTracker:
    """Tracks tool usage across all agents in the system."""
    
    def __init__(self):
        self.usage_history: List[ToolUsage] = []
        self.active_calls: Dict[str, float] = {}  # call_id -> start_time
        self.agent_stats: Dict[str, Dict[str, Any]] = defaultdict(lambda: {
            'total_calls': 0,
            'successful_calls': 0,
            'failed_calls': 0,
            'tools_used': Counter(),
            'total_duration': 0.0,
            'last_activity': None
        })
    
    def start_tool_call(self, agent_name: str, tool_name: str, parameters: Dict[str, Any] = None) -> str:
        """Start tracking a tool call."""
        call_id = f"{agent_name}_{tool_name}_{time.time()}"
        self.active_calls[call_id] = time.time()
        
        logger.debug(f"[*] {agent_name} starting tool: {tool_name}")
        return call_id
    
    def end_tool_call(self, call_id: str, agent_name: str, tool_name: str, 
                      success: bool = True, error_message: str = None, 
                      result_summary: str = None, parameters: Dict[str, Any] = None) -> None:
        """End tracking a tool call."""
        start_time = self.active_calls.pop(call_id, time.time())
        duration = time.time() - start_time
        
        # Record the usage
        usage = ToolUsage(
            agent_name=agent_name,
            tool_name=tool_name,
            timestamp=start_time,
            duration=duration,
            success=success,
            error_message=error_message,
            parameters=parameters or {},
            result_summary=result_summary
        )
        
        self.usage_history.append(usage)
        
        # Update agent stats
        stats = self.agent_stats[agent_name]
        stats['total_calls'] += 1
        stats['tools_used'][tool_name] += 1
        stats['total_duration'] += duration
        
        # Notify real-time interface directly (independent of logging)
        try:
            from swe_agent.utils.progress_tracker import get_realtime_interface
            realtime_interface = get_realtime_interface()
            realtime_interface.log_tool_usage(tool_name, "executed", success, duration)
        except:
            pass
        stats['last_activity'] = datetime.now()
        
        if success:
            stats['successful_calls'] += 1
        else:
            stats['failed_calls'] += 1
            
        logger.info(f"[OK] {agent_name} completed {tool_name} in {duration:.2f}s (success: {success})")
    
    def get_agent_usage_summary(self, agent_name: str) -> Dict[str, Any]:
        """Get usage summary for a specific agent."""
        stats = self.agent_stats[agent_name]
        
        # Get recent tool usage
        recent_usage = [u for u in self.usage_history[-20:] if u.agent_name == agent_name]
        
        return {
            'agent_name': agent_name,
            'total_calls': stats['total_calls'],
            'success_rate': stats['successful_calls'] / max(stats['total_calls'], 1) * 100,
            'total_duration': stats['total_duration'],
            'avg_duration': stats['total_duration'] / max(stats['total_calls'], 1),
            'most_used_tools': dict(stats['tools_used'].most_common(5)),
            'recent_usage': [
                {
                    'tool': u.tool_name,
                    'time': datetime.fromtimestamp(u.timestamp).strftime('%H:%M:%S'),
                    'duration': f"{u.duration:.2f}s" if u.duration else "N/A",
                    'success': u.success
                }
                for u in recent_usage[-5:]
            ]
        }
    
    def get_overall_usage_summary(self) -> Dict[str, Any]:
        """Get overall usage summary across all agents."""
        total_calls = sum(stats['total_calls'] for stats in self.agent_stats.values())
        total_duration = sum(stats['total_duration'] for stats in self.agent_stats.values())
        
        # Tool popularity across all agents
        all_tools = Counter()
        for stats in self.agent_stats.values():
            all_tools.update(stats['tools_used'])
        
        # Agent activity
        agent_activity = {
            agent: stats['total_calls'] 
            for agent, stats in self.agent_stats.items()
        }
        
        return {
            'total_calls': total_calls,
            'total_duration': total_duration,
            'avg_duration': total_duration / max(total_calls, 1),
            'most_popular_tools': dict(all_tools.most_common(10)),
            'agent_activity': agent_activity,
            'active_agents': len(self.agent_stats)
        }
    
    def get_tool_usage_details(self, tool_name: str) -> Dict[str, Any]:
        """Get detailed usage information for a specific tool."""
        tool_usage = [u for u in self.usage_history if u.tool_name == tool_name]
        
        if not tool_usage:
            return {'tool_name': tool_name, 'usage_count': 0}
        
        success_count = sum(1 for u in tool_usage if u.success)
        total_duration = sum(u.duration for u in tool_usage if u.duration)
        
        agents_using = Counter(u.agent_name for u in tool_usage)
        
        return {
            'tool_name': tool_name,
            'usage_count': len(tool_usage),
            'success_rate': success_count / len(tool_usage) * 100,
            'total_duration': total_duration,
            'avg_duration': total_duration / len(tool_usage),
            'agents_using': dict(agents_using),
            'recent_usage': [
                {
                    'agent': u.agent_name,
                    'time': datetime.fromtimestamp(u.timestamp).strftime('%H:%M:%S'),
                    'success': u.success,
                    'duration': f"{u.duration:.2f}s" if u.duration else "N/A"
                }
                for u in tool_usage[-5:]
            ]
        }
    
    def format_usage_report(self) -> str:
        """Format a comprehensive usage report."""
        overall = self.get_overall_usage_summary()
        
        report = f"""
[*] Tool Usage Report
{'='*50}

📊 Overall Statistics:
• Total tool calls: {overall['total_calls']}
• Total duration: {overall['total_duration']:.2f}s
• Average call duration: {overall['avg_duration']:.2f}s
• Active agents: {overall['active_agents']}

🏆 Most Popular Tools:
"""
        
        for tool, count in overall['most_popular_tools'].items():
            report += f"• {tool}: {count} calls\n"
        
        report += f"""
👥 Agent Activity:
"""
        
        for agent, calls in overall['agent_activity'].items():
            agent_summary = self.get_agent_usage_summary(agent)
            report += f"• {agent}: {calls} calls ({agent_summary['success_rate']:.1f}% success)\n"
        
        return report
    
    def clear_history(self) -> None:
        """Clear all usage history."""
        self.usage_history.clear()
        self.active_calls.clear()
        self.agent_stats.clear()
        logger.info("🧹 Tool usage history cleared")

# Global tracker instance
_global_tracker = ToolUsageTracker()

def get_tool_tracker() -> ToolUsageTracker:
    """Get the global tool usage tracker."""
    return _global_tracker

def track_tool_usage(agent_name: str, tool_name: str):
    """Decorator to track tool usage."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            tracker = get_tool_tracker()
            call_id = tracker.start_tool_call(agent_name, tool_name, kwargs)
            
            try:
                result = func(*args, **kwargs)
                tracker.end_tool_call(
                    call_id, agent_name, tool_name, 
                    success=True, 
                    result_summary=str(result)[:100] if result else None,
                    parameters=kwargs
                )
                return result
            except Exception as e:
                tracker.end_tool_call(
                    call_id, agent_name, tool_name, 
                    success=False, 
                    error_message=str(e),
                    parameters=kwargs
                )
                raise
        return wrapper
    return decorator