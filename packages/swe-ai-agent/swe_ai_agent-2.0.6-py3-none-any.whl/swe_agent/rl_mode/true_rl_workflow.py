"""
True Reinforcement Learning Workflow - Iterative Code Improvement
Implements actual reward-based code refinement and learning inspired by o1-like reasoning.
"""

import logging
import time
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass
import tempfile
import os

from rich.console import Console
from rich.panel import Panel
from rich.text import Text

from ..workflows.clean_swe_workflow import CleanSWEWorkflow
from .reward_system import RewardSystem
from dataclasses import dataclass as action_dataclass

console = Console()
# from .rl_state import RLAgentState, create_rl_state  # Not needed for this implementation

@action_dataclass 
class ActionReward:
    """Action reward data structure for learning."""
    action_type: str
    tool_name: str
    reward_value: float
    timestamp: float
    success: bool
    context: Dict[str, Any]

logger = logging.getLogger(__name__)

@dataclass
class CodeAttempt:
    """Represents a code generation attempt with its reward and confidence."""
    code: str
    file_path: str
    reward: float
    confidence: float
    issues: List[str]
    improvements: List[str]
    reasoning: str
    timestamp: float
    attempt_number: int
    
@dataclass
class ReflectionStep:
    """Represents a reflection step in the iterative process."""
    step_number: int
    analysis: str
    identified_issues: List[str]
    proposed_improvements: List[str]
    confidence_score: float
    should_continue: bool

class TrueRLWorkflow:
    """
    True Reinforcement Learning workflow that iteratively improves code based on rewards.
    Uses o1-like reasoning with confidence scoring and adaptive strategy adjustment.
    """
    
    def __init__(self, repo_path: Path, output_dir: Path):
        self.repo_path = repo_path
        self.output_dir = output_dir
        self.reward_system = RewardSystem()
        self.base_workflow = CleanSWEWorkflow(
            str(repo_path), str(output_dir), False, False, False, False
        )
        self.max_iterations = 8
        self.target_reward = 8.0
        self.confidence_threshold = 0.85
        self.min_improvement = 0.3
        self.reflection_frequency = 2  # Reflect every 2 attempts
        
    def execute_iterative_task(self, task_description: str) -> Dict[str, Any]:
        """
        Execute a task with iterative improvement based on rewards and confidence.
        """
        logger.info(f"🎯 RL Mode: Starting iterative reasoning and improvement")
        logger.info(f"📋 Task: {task_description}")
        
        console.print(Panel(
            Text(f"Starting Iterative RL with advanced reasoning\nTask: {task_description}\n\n"
                 f"Quality Target: {self.target_reward:.1f}/10.0 | Confidence Target: {self.confidence_threshold:.2f}\n"
                 f"Max Iterations: {self.max_iterations} | Min Improvement: {self.min_improvement:.2f}", 
                 style="bold blue"),
            title="🧠 Reasoning Mode",
            border_style="blue"
        ))
        
        attempts = []
        reflections = []
        best_attempt = None
        start_time = time.time()
        
        for iteration in range(1, self.max_iterations + 1):
            logger.info(f"🔄 Iteration {iteration}/{self.max_iterations}")
            
            # Perform reflection every N attempts
            if iteration > 1 and (iteration - 1) % self.reflection_frequency == 0:
                reflection = self._perform_deep_reflection(attempts, task_description, iteration)
                reflections.append(reflection)
                logger.info(f"🤔 Reflection: Confidence {reflection.confidence_score:.2f}, Continue: {reflection.should_continue}")
                
                # If reflection suggests we shouldn't continue, break
                if not reflection.should_continue and iteration > 3:
                    logger.info(f"💡 Reflection suggests stopping - confidence sufficient")
                    break
            
            # Generate improved code attempt with reasoning
            attempt = self._generate_reasoning_attempt(task_description, attempts, reflections, iteration)
            attempts.append(attempt)
            
            # Enhanced UI display with rich formatting
            console.print(Panel(
                Text(f"Attempt {iteration} Results:\n\n"
                     f"🎯 Reward: {attempt.reward:.2f}/10.0 {'✓' if attempt.reward >= self.target_reward else '⚠️'}\n"
                     f"🎖️ Confidence: {attempt.confidence:.2f} {'✓' if attempt.confidence >= self.confidence_threshold else '⚠️'}\n"
                     f"📈 Issues Found: {len(attempt.issues)}\n"
                     f"✨ Improvements: {len(attempt.improvements)}\n\n"
                     f"Top Issues: {', '.join(attempt.issues[:2]) if attempt.issues else 'None'}\n"
                     f"Key Improvements: {', '.join(attempt.improvements[:2]) if attempt.improvements else 'None'}",
                     style="cyan"),
                title=f"🔄 Iteration {iteration}/{self.max_iterations}",
                border_style="cyan"
            ))
            
            logger.info(f"📊 Attempt {iteration}: Reward {attempt.reward:.2f}, Confidence {attempt.confidence:.2f}")
            
            # Update best attempt based on both reward and confidence
            if self._is_better_attempt(attempt, best_attempt):
                best_attempt = attempt
                console.print(Panel(
                    Text(f"🏆 NEW BEST ATTEMPT!\n\n"
                         f"Reward: {attempt.reward:.2f}/10.0 ({'+' if attempt.reward > (previous_best_reward := (best_attempt.reward if best_attempt and best_attempt != attempt else 0)) else ''}{attempt.reward - previous_best_reward:.1f})\n"
                         f"Confidence: {attempt.confidence:.2f} ({'+' if attempt.confidence > (previous_best_conf := (best_attempt.confidence if best_attempt and best_attempt != attempt else 0)) else ''}{attempt.confidence - previous_best_conf:.2f})",
                         style="bold green"),
                    title="🎉 Quality Improvement",
                    border_style="green"
                ))
                logger.info(f"🏆 New best! Reward: {attempt.reward:.2f}, Confidence: {attempt.confidence:.2f}")
            
            # Advanced stopping criteria
            should_stop = self._evaluate_stopping_criteria(attempt, attempts, iteration)
            if should_stop:
                reason = self._get_stopping_reason(attempt, attempts, iteration)
                console.print(Panel(
                    Text(f"Stopping Iterative Improvement\n\n"
                         f"Reason: {reason}\n"
                         f"Final Quality: {attempt.reward:.2f}/10.0\n"
                         f"Final Confidence: {attempt.confidence:.2f}\n"
                         f"Iterations Completed: {iteration}",
                         style="bold yellow"),
                    title="🛑 Convergence Achieved",
                    border_style="yellow"
                ))
                logger.info(f"🛑 Stopping: {reason}")
                break
            
            # Adaptive learning from attempt
            self._adaptive_learning(attempt, attempts, reflections)
            
        # Final optimization of best attempt
        if best_attempt:
            console.print(Panel(
                Text("Running final optimization pass...", style="bold magenta"),
                title="⚡ Final Enhancement",
                border_style="magenta"
            ))
            
            optimized_attempt = self._final_optimization(best_attempt, task_description)
            if optimized_attempt and self._is_better_attempt(optimized_attempt, best_attempt):
                improvement = optimized_attempt.reward - best_attempt.reward
                best_attempt = optimized_attempt
                console.print(Panel(
                    Text(f"Final optimization successful!\n\n"
                         f"Quality improved: {improvement:+.1f} → {best_attempt.reward:.2f}/10.0\n"
                         f"Confidence: {best_attempt.confidence:.2f}",
                         style="bold green"),
                    title="✨ Optimization Success",
                    border_style="green"
                ))
                logger.info(f"⚡ Final optimization improved to: {best_attempt.reward:.2f}")
            else:
                console.print(Panel(
                    Text("No significant improvements found in final pass", style="yellow"),
                    title="Final Optimization",
                    border_style="yellow"
                ))
            
            self._save_best_attempt(best_attempt)
            
        execution_time = time.time() - start_time
        
        return {
            "result": best_attempt is not None,
            "best_attempt": best_attempt,
            "all_attempts": attempts,
            "reflections": reflections,
            "final_reward": best_attempt.reward if best_attempt else 0.0,
            "final_confidence": best_attempt.confidence if best_attempt else 0.0,
            "iterations_completed": len(attempts),
            "execution_time": execution_time,
            "reasoning_quality": self._calculate_reasoning_quality(attempts),
            "adaptive_improvements": len([a for i, a in enumerate(attempts[1:], 1) 
                                        if a.reward > max(attempts[:i], key=lambda x: x.reward).reward])
        }
    
    def _generate_reasoning_attempt(self, task_description: str, previous_attempts: List[CodeAttempt], 
                                   reflections: List[ReflectionStep], iteration: int) -> CodeAttempt:
        """Generate a code attempt with advanced reasoning and adaptive improvement."""
        
        # Create reasoning-enhanced prompt with confidence scoring
        reasoning_prompt = self._create_reasoning_prompt(task_description, previous_attempts, reflections, iteration)
        
        # Generate code with explicit reasoning
        reasoning_text = ""
        try:
            result = self.base_workflow.run_workflow(reasoning_prompt)
            code_generated = self._extract_generated_code()
            file_path = self._identify_created_file()
            reasoning_text = f"Iteration {iteration} reasoning: Applied lessons from previous attempts"
            
        except Exception as e:
            logger.error(f"Code generation failed: {e}")
            return CodeAttempt(
                code="", file_path="", reward=-5.0, confidence=0.1,
                issues=[f"Generation failed: {e}"], improvements=[],
                reasoning=f"Failed at iteration {iteration}: {e}",
                timestamp=time.time(), attempt_number=iteration
            )
        
        # Comprehensive evaluation with confidence scoring
        reward, confidence, issues, improvements = self._comprehensive_evaluation(
            code_generated, file_path, previous_attempts, iteration
        )
        
        return CodeAttempt(
            code=code_generated,
            file_path=file_path,
            reward=reward,
            confidence=confidence,
            issues=issues,
            improvements=improvements,
            reasoning=reasoning_text,
            timestamp=time.time(),
            attempt_number=iteration
        )
    
    def _create_reasoning_prompt(self, original_task: str, previous_attempts: List[CodeAttempt], 
                               reflections: List[ReflectionStep], iteration: int) -> str:
        """Create o1-like reasoning prompt with step-by-step thinking and confidence scoring."""
        
        if not previous_attempts and not reflections:
            return f"""
TASK: {original_task}

REASONING APPROACH (Iteration {iteration}):
Think step-by-step with explicit reasoning. Consider multiple approaches and assign confidence scores to your decisions.

1. Analyze the task requirements thoroughly
2. Consider edge cases and potential issues
3. Design a robust solution with proper error handling
4. Include comprehensive testing and documentation
5. Evaluate your solution's quality and assign confidence

Focus on creating high-quality, maintainable, and secure code.
"""
        
        # Advanced reasoning context with historical analysis
        reasoning_context = f"""
TASK: {original_task}

ITERATIVE REASONING (Attempt {iteration}):
You are in an iterative improvement process. Use previous attempts and reflections to guide your reasoning.

PREVIOUS ATTEMPTS ANALYSIS:"""
        
        if previous_attempts:
            # Show trajectory of attempts
            for i, attempt in enumerate(previous_attempts[-3:], max(1, len(previous_attempts)-2)):
                reasoning_context += f"""

Attempt {i}: Reward {attempt.reward:.2f}, Confidence {attempt.confidence:.2f}
Issues identified: {', '.join(attempt.issues[:3])}
Improvements made: {', '.join(attempt.improvements[:2])}"""
        
        if reflections:
            latest_reflection = reflections[-1]
            reasoning_context += f"""

LATEST REFLECTION INSIGHTS:
Analysis: {latest_reflection.analysis[:200]}...
Key Issues: {', '.join(latest_reflection.identified_issues[:3])}
Proposed Improvements: {', '.join(latest_reflection.proposed_improvements[:3])}
Confidence: {latest_reflection.confidence_score:.2f}
"""
        
        # Adaptive strategy based on iteration
        if iteration <= 2:
            strategy = "Focus on core functionality and basic quality"
        elif iteration <= 4:
            strategy = "Enhance robustness, error handling, and edge cases"
        elif iteration <= 6:
            strategy = "Optimize performance, security, and maintainability"
        else:
            strategy = "Fine-tune details and ensure production readiness"
            
        reasoning_context += f"""

CURRENT STRATEGY ({strategy}):
1. Apply lessons learned from previous attempts
2. Address the most critical issues identified
3. Implement suggested improvements with high confidence
4. Maintain or improve upon the best aspects of previous attempts
5. Assign realistic confidence scores to guide future iterations

QUALITY TARGETS:
- Code Functionality: Complete and correct
- Error Handling: Comprehensive and robust
- Documentation: Clear and thorough
- Testing: Adequate coverage
- Security: No obvious vulnerabilities
- Performance: Efficient and scalable

Reason through your solution step by step, explaining your decisions and confidence levels.
"""
        
        return reasoning_context
    
    def _comprehensive_evaluation(self, code: str, file_path: str, previous_attempts: List[CodeAttempt], 
                                 iteration: int) -> Tuple[float, float, List[str], List[str]]:
        """Comprehensive code evaluation with confidence scoring."""
        if not code:
            return -5.0, 0.1, ["No code generated"], []
        
        reward = 0.0
        confidence = 0.5
        issues = []
        improvements = []
        
        # Core functionality check
        if len(code) > 100:
            reward += 1.5
            improvements.append("Substantial code length")
        else:
            issues.append("Code appears incomplete or too brief")
            confidence -= 0.2
        
        # Function and class structure
        func_count = code.count('def ')
        class_count = code.count('class ')
        if func_count > 0:
            reward += 1.0 + (func_count * 0.2)
            improvements.append(f"Contains {func_count} function(s)")
            confidence += 0.1
        if class_count > 0:
            reward += 0.5
            improvements.append(f"Contains {class_count} class(es)")
        
        # Documentation quality
        docstring_count = code.count('"""') + code.count("'''")
        if docstring_count >= 2:
            reward += 2.0
            improvements.append("Comprehensive documentation")
            confidence += 0.15
        elif docstring_count > 0:
            reward += 1.0
            improvements.append("Basic documentation present")
        else:
            issues.append("Missing or insufficient documentation")
            confidence -= 0.1
        
        # Error handling and robustness  
        try_count = code.count('try:')
        except_count = code.count('except')
        if try_count > 0 and except_count > 0:
            reward += 1.5
            improvements.append("Error handling implemented")
            confidence += 0.1
        else:
            issues.append("Missing error handling")
        
        # Type hints and modern Python
        if '->' in code and ':' in code:
            arrow_count = code.count('->')
            if arrow_count >= func_count * 0.8:  # Most functions have return type hints
                reward += 1.0
                improvements.append("Good type hint coverage")
                confidence += 0.1
            else:
                improvements.append("Partial type hints")
                reward += 0.5
        else:
            issues.append("Missing type hints")
        
        # Testing and validation
        test_indicators = ['test', 'assert', 'unittest', 'pytest', '__name__ == "__main__"']
        test_score = sum(1 for indicator in test_indicators if indicator in code.lower())
        if test_score >= 2:
            reward += 1.5
            improvements.append("Testing functionality included")
            confidence += 0.15
        elif test_score > 0:
            reward += 0.8
            improvements.append("Some testing elements present")
        else:
            issues.append("No testing functionality")
        
        # Security assessment
        security_risks = ['eval(', 'exec(', 'input()', 'raw_input()', '__import__']
        dangerous_count = sum(1 for risk in security_risks if risk in code)
        if dangerous_count > 0:
            reward -= 2.0 * dangerous_count
            issues.extend([f"Security risk: {risk}" for risk in security_risks if risk in code])
            confidence -= 0.2
        else:
            reward += 0.5
            improvements.append("No obvious security vulnerabilities")
        
        # Code quality and style
        if code.count('(') == code.count(')') and code.count('{') == code.count('}'):
            reward += 0.5
            confidence += 0.05
        else:
            issues.append("Potential syntax issues with brackets")
            confidence -= 0.15
        
        # Progressive improvement check
        if previous_attempts:
            last_reward = previous_attempts[-1].reward
            if reward > last_reward:
                bonus = min(1.0, (reward - last_reward) * 0.5)
                reward += bonus
                improvements.append(f"Improvement over previous attempt (+{bonus:.1f})")
                confidence += 0.1
        
        # Confidence calibration
        confidence = max(0.1, min(0.95, confidence + (reward / 10.0)))
        
        return max(0.0, reward), confidence, issues, improvements
    
    def _perform_deep_reflection(self, attempts: List[CodeAttempt], task_description: str, 
                               iteration: int) -> ReflectionStep:
        """Perform deep reflection on attempts so far."""
        if not attempts:
            return ReflectionStep(
                step_number=iteration,
                analysis="No attempts yet to analyze",
                identified_issues=[],
                proposed_improvements=["Start with basic implementation"],
                confidence_score=0.5,
                should_continue=True
            )
        
        latest_attempt = attempts[-1]
        recent_attempts = attempts[-3:] if len(attempts) >= 3 else attempts
        
        # Analyze trends
        rewards = [a.reward for a in recent_attempts]
        confidences = [a.confidence for a in recent_attempts]
        
        avg_reward = sum(rewards) / len(rewards)
        avg_confidence = sum(confidences) / len(confidences)
        
        # Check if we're improving
        if len(rewards) > 1:
            reward_trend = rewards[-1] - rewards[0]
            confidence_trend = confidences[-1] - confidences[0]
        else:
            reward_trend = 0
            confidence_trend = 0
        
        # Aggregate issues and improvements
        all_issues = []
        all_improvements = []
        for attempt in recent_attempts:
            all_issues.extend(attempt.issues)
            all_improvements.extend(attempt.improvements)
        
        # Count frequency of issues
        issue_counts = {}
        for issue in all_issues:
            issue_counts[issue] = issue_counts.get(issue, 0) + 1
        
        persistent_issues = [issue for issue, count in issue_counts.items() if count >= 2]
        
        # Generate analysis
        analysis = f"""
Reflection on {len(attempts)} attempts:
- Average reward: {avg_reward:.2f}
- Average confidence: {avg_confidence:.2f}  
- Reward trend: {'+' if reward_trend > 0 else ''}{reward_trend:.2f}
- Most recent reward: {latest_attempt.reward:.2f}
- Persistent issues: {len(persistent_issues)}
"""
        
        # Determine if we should continue
        should_continue = True
        if avg_confidence >= self.confidence_threshold and latest_attempt.reward >= self.target_reward * 0.9:
            should_continue = False
        elif len(attempts) >= 6 and reward_trend <= 0.1:
            should_continue = False
        elif latest_attempt.confidence >= 0.9 and latest_attempt.reward >= self.target_reward:
            should_continue = False
        
        # Propose improvements
        proposed_improvements = []
        if persistent_issues:
            proposed_improvements.append("Address persistent issues: " + ", ".join(persistent_issues[:2]))
        if avg_confidence < 0.7:
            proposed_improvements.append("Focus on increasing solution confidence")
        if latest_attempt.reward < self.target_reward:
            proposed_improvements.append("Enhance code quality and completeness")
        
        return ReflectionStep(
            step_number=iteration,
            analysis=analysis,
            identified_issues=persistent_issues,
            proposed_improvements=proposed_improvements,
            confidence_score=avg_confidence,
            should_continue=should_continue
        )
    
    def _is_better_attempt(self, new_attempt: CodeAttempt, current_best: Optional[CodeAttempt]) -> bool:
        """Determine if new attempt is better than current best."""
        if current_best is None:
            return True
        
        # Weighted scoring: 70% reward, 30% confidence
        new_score = (new_attempt.reward * 0.7) + (new_attempt.confidence * 3.0 * 0.3)
        best_score = (current_best.reward * 0.7) + (current_best.confidence * 3.0 * 0.3)
        
        return new_score > best_score
    
    def _evaluate_stopping_criteria(self, attempt: CodeAttempt, attempts: List[CodeAttempt], 
                                   iteration: int) -> bool:
        """Advanced stopping criteria evaluation."""
        # High quality achieved
        if attempt.reward >= self.target_reward and attempt.confidence >= self.confidence_threshold:
            return True
        
        # Diminishing returns
        if len(attempts) >= 4:
            recent_rewards = [a.reward for a in attempts[-4:]]
            if max(recent_rewards) - min(recent_rewards) < self.min_improvement:
                return True
        
        # Maximum iterations reached
        if iteration >= self.max_iterations:
            return True
        
        return False
    
    def _get_stopping_reason(self, attempt: CodeAttempt, attempts: List[CodeAttempt], 
                           iteration: int) -> str:
        """Get human-readable stopping reason."""
        if attempt.reward >= self.target_reward and attempt.confidence >= self.confidence_threshold:
            return f"High quality achieved (R:{attempt.reward:.2f}, C:{attempt.confidence:.2f})"
        elif len(attempts) >= 4:
            recent_rewards = [a.reward for a in attempts[-4:]]
            if max(recent_rewards) - min(recent_rewards) < self.min_improvement:
                return f"Diminishing returns detected"
        elif iteration >= self.max_iterations:
            return f"Maximum iterations reached"
        return "Unknown stopping condition"
    
    def _adaptive_learning(self, attempt: CodeAttempt, attempts: List[CodeAttempt], 
                          reflections: List[ReflectionStep]):
        """Learn adaptively from the current attempt."""
        # Store learning patterns
        learning_data = {
            "attempt_number": attempt.attempt_number,
            "reward": attempt.reward,
            "confidence": attempt.confidence,
            "issues_count": len(attempt.issues),
            "improvements_count": len(attempt.improvements),
            "timestamp": attempt.timestamp
        }
        
        # Update reward system
        action_reward_dict = {
            "action_type": "iterative_improvement",
            "tool_name": "true_rl_reasoning", 
            "reward_value": attempt.reward,
            "timestamp": attempt.timestamp,
            "success": attempt.reward > 3.0,
            "context": learning_data
        }
        
        self.reward_system.action_history.append(action_reward_dict)
        
        # Adaptive parameter adjustment based on performance
        if len(attempts) >= 3:
            recent_performance = sum(a.reward for a in attempts[-3:]) / 3
            if recent_performance < 3.0:
                # Struggling - increase target diversity
                self.min_improvement *= 0.9
            elif recent_performance > 6.0:
                # Doing well - increase standards
                self.target_reward = min(9.0, self.target_reward + 0.2)
    
    def _final_optimization(self, best_attempt: CodeAttempt, task_description: str) -> Optional[CodeAttempt]:
        """Perform final optimization on the best attempt."""
        optimization_prompt = f"""
FINAL OPTIMIZATION TASK:
Original task: {task_description}

CURRENT BEST SOLUTION (Reward: {best_attempt.reward:.2f}, Confidence: {best_attempt.confidence:.2f}):
{best_attempt.code[:500]}...

IDENTIFIED ISSUES TO FIX:
{chr(10).join(f"- {issue}" for issue in best_attempt.issues[:3])}

FINAL OPTIMIZATION GOALS:
1. Fix any remaining critical issues
2. Enhance code quality and robustness
3. Improve documentation and clarity
4. Ensure production readiness
5. Maintain existing strengths

Make only essential improvements while preserving the working functionality.
"""
        
        try:
            result = self.base_workflow.run_workflow(optimization_prompt)
            code_generated = self._extract_generated_code()
            file_path = self._identify_created_file()
            
            # Evaluate optimization
            reward, confidence, issues, improvements = self._comprehensive_evaluation(
                code_generated, file_path, [best_attempt], 999
            )
            
            return CodeAttempt(
                code=code_generated,
                file_path=file_path,
                reward=reward,
                confidence=confidence,
                issues=issues,
                improvements=improvements + ["Final optimization applied"],
                reasoning="Final optimization pass",
                timestamp=time.time(),
                attempt_number=999  # Special marker for final optimization
            )
            
        except Exception as e:
            logger.error(f"Final optimization failed: {e}")
            return None
    
    def _calculate_reasoning_quality(self, attempts: List[CodeAttempt]) -> float:
        """Calculate overall reasoning quality score."""
        if not attempts:
            return 0.0
        
        # Factors: improvement trajectory, confidence progression, issue resolution
        rewards = [a.reward for a in attempts]
        confidences = [a.confidence for a in attempts]
        
        # Improvement trajectory (30%)
        if len(rewards) > 1:
            improvement_score = min(1.0, (rewards[-1] - rewards[0]) / 5.0)
        else:
            improvement_score = 0.5
        
        # Average confidence (40%)
        confidence_score = sum(confidences) / len(confidences)
        
        # Issue resolution (30%)
        total_issues = sum(len(a.issues) for a in attempts)
        total_improvements = sum(len(a.improvements) for a in attempts)
        if total_issues + total_improvements > 0:
            resolution_score = total_improvements / (total_issues + total_improvements)
        else:
            resolution_score = 0.5
        
        return (improvement_score * 0.3) + (confidence_score * 0.4) + (resolution_score * 0.3)
    
    def _evaluate_code_quality(self, code: str, file_path: str) -> Tuple[float, List[str]]:
        """Evaluate code quality and return reward + issues list."""
        
        if not code:
            return -5.0, ["No code generated"]
            
        reward = 0.0
        issues = []
        
        # Basic code quality checks
        if len(code) > 50:
            reward += 1.0
        else:
            issues.append("Code too short, likely incomplete")
            
        # Documentation check
        if '"""' in code or "'''" in code:
            reward += 1.5
        else:
            issues.append("Missing documentation/docstrings")
            
        # Function definition check
        if 'def ' in code:
            reward += 1.0
            # Count functions
            func_count = code.count('def ')
            if func_count > 1:
                reward += 0.5
        else:
            issues.append("No function definitions found")
            
        # Error handling check
        if 'try:' in code and 'except' in code:
            reward += 1.0
        else:
            issues.append("Missing error handling")
            
        # Type hints check
        if '->' in code and ':' in code:
            reward += 0.5
        else:
            issues.append("Missing type hints")
            
        # Testing check
        if 'test' in code.lower() or 'assert' in code:
            reward += 1.0
        else:
            issues.append("No testing functionality")
            
        # Security check - avoid common issues
        security_issues = []
        if 'eval(' in code:
            security_issues.append("Dangerous eval() usage")
        if 'exec(' in code:
            security_issues.append("Dangerous exec() usage")
            
        if security_issues:
            reward -= 2.0
            issues.extend(security_issues)
        else:
            reward += 0.5  # Bonus for no security issues
            
        # Syntax and structure bonus
        if code.count('(') == code.count(')') and code.count('{') == code.count('}'):
            reward += 0.5
        else:
            issues.append("Potential syntax issues with brackets")
            
        return max(0.0, reward), issues
    
    def _identify_common_issues(self, attempts: List[CodeAttempt]) -> List[str]:
        """Identify issues that appear in multiple attempts."""
        issue_counts = {}
        for attempt in attempts:
            for issue in attempt.issues:
                issue_counts[issue] = issue_counts.get(issue, 0) + 1
                
        return [issue for issue, count in issue_counts.items() if count >= 2]
    
    def _identify_successful_patterns(self, attempts: List[CodeAttempt]) -> List[str]:
        """Identify patterns from high-reward attempts."""
        if not attempts:
            return []
            
        # Find attempts with above-average rewards
        avg_reward = sum(a.reward for a in attempts) / len(attempts)
        good_attempts = [a for a in attempts if a.reward > avg_reward]
        
        patterns = []
        for attempt in good_attempts:
            if 'def ' in attempt.code:
                patterns.append("Include function definitions")
            if '"""' in attempt.code:
                patterns.append("Add comprehensive docstrings")
            if 'try:' in attempt.code:
                patterns.append("Implement error handling")
                
        return list(set(patterns))  # Remove duplicates
    
    def _extract_generated_code(self) -> str:
        """Extract the most recently generated code."""
        # Look for recently created Python files
        python_files = list(self.repo_path.glob("*.py"))
        if not python_files:
            return ""
            
        # Get the most recently modified file
        latest_file = max(python_files, key=lambda f: f.stat().st_mtime)
        try:
            return latest_file.read_text()
        except Exception:
            return ""
    
    def _identify_created_file(self) -> str:
        """Identify the most recently created file."""
        python_files = list(self.repo_path.glob("*.py"))
        if not python_files:
            return ""
            
        latest_file = max(python_files, key=lambda f: f.stat().st_mtime)
        return str(latest_file.name)
    
    def _learn_from_attempt(self, attempt: CodeAttempt, all_attempts: List[CodeAttempt]):
        """Learn from the current attempt to improve future ones."""
        
        # Store learning patterns in reward system
        learning_data = {
            "attempt_number": attempt.attempt_number,
            "reward": attempt.reward,
            "issues": attempt.issues,
            "timestamp": attempt.timestamp
        }
        
        # Create action reward for learning
        action_reward_dict = {
            "action_type": "code_generation", 
            "tool_name": "iterative_improvement",
            "reward_value": attempt.reward,
            "timestamp": attempt.timestamp,
            "success": attempt.reward > 3.0,
            "context": learning_data
        }
        
        self.reward_system.action_history.append(action_reward_dict)
        
        logger.info(f"📚 Learning from attempt {attempt.attempt_number}: {len(attempt.issues)} issues identified")
    
    def _save_best_attempt(self, best_attempt: CodeAttempt):
        """Save the best attempt as the final result."""
        if best_attempt.file_path and best_attempt.code:
            try:
                file_path = self.repo_path / best_attempt.file_path
                file_path.write_text(best_attempt.code)
                logger.info(f"💾 Saved best attempt to {best_attempt.file_path}")
            except Exception as e:
                logger.error(f"Failed to save best attempt: {e}")