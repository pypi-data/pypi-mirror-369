"""
Planning Tools - Specialized tools for project planning and technical specification creation.
Supports comprehensive planning, requirement analysis, and architecture design.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from utils.anthropic_client import get_anthropic_client, call_claude
import json
from datetime import datetime

logger = logging.getLogger(__name__)

class PlanningTools:
    """
    Specialized tools for project planning and technical specification creation.
    Handles plan creation, requirement analysis, and architecture design.
    """
    
    def __init__(self, settings=None):
        """
        Initialize planning tools.
        
        Args:
            settings: Optional settings configuration
        """
        self.anthropic_client = get_anthropic_client()
        self.settings = settings
        self.output_dir = Path("output")
        self.plans_dir = self.output_dir / "plans"
        self.plans_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info("[P] Planning tools initialized")
    
    def create_plan(self, goal: str, requirements: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a comprehensive project plan.
        
        Args:
            goal: The project goal/objective
            requirements: Optional list of specific requirements
            
        Returns:
            Dictionary containing plan details
        """
        try:
            requirements_text = ""
            if requirements:
                requirements_text = f"\n\nSpecific Requirements:\n" + "\n".join(f"- {req}" for req in requirements)
            
            prompt = f"""
            Create a comprehensive project plan for the following goal:
            
            Goal: {goal}{requirements_text}
            
            Provide a structured plan with:
            1. Project overview and objectives
            2. Key deliverables and milestones
            3. Implementation phases
            4. Resource requirements
            5. Success criteria
            6. Risk assessment
            
            Format the response as a detailed, actionable plan.
            """
            
            plan_content = call_claude(
                self.anthropic_client,
                prompt,
                "You are an expert project planner. Create comprehensive, actionable plans that can be immediately implemented."
            )
            
            # Save plan to file
            plan_data = {
                "goal": goal,
                "requirements": requirements or [],
                "content": plan_content,
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            
            plan_file = self.plans_dir / f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(plan_file, 'w') as f:
                json.dump(plan_data, f, indent=2)
            
            logger.info(f"[P] Plan created and saved to {plan_file}")
            
            return {
                "success": True,
                "plan": plan_data,
                "file_path": str(plan_file)
            }
            
        except Exception as e:
            logger.error(f"Error creating plan: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def create_tech_spec(self, goal: str, architecture_type: str = "modular") -> Dict[str, Any]:
        """
        Create a technical specification.
        
        Args:
            goal: The project goal/objective
            architecture_type: Type of architecture (modular, microservices, monolithic)
            
        Returns:
            Dictionary containing tech spec details
        """
        try:
            prompt = f"""
            Create a comprehensive technical specification for the following goal:
            
            Goal: {goal}
            Architecture Type: {architecture_type}
            
            Provide a detailed technical specification including:
            1. System architecture overview
            2. Technology stack recommendations
            3. Component design and responsibilities
            4. Data models and APIs
            5. Performance requirements
            6. Security considerations
            7. Testing strategy
            8. Deployment architecture
            
            Make it specific enough that developers can start implementation immediately.
            """
            
            spec_content = call_claude(
                self.anthropic_client,
                prompt,
                "You are an expert technical architect. Create detailed, implementable technical specifications."
            )
            
            # Save tech spec to file
            spec_data = {
                "goal": goal,
                "architecture_type": architecture_type,
                "content": spec_content,
                "created_at": datetime.now().isoformat(),
                "status": "draft"
            }
            
            spec_file = self.plans_dir / f"tech_spec_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(spec_file, 'w') as f:
                json.dump(spec_data, f, indent=2)
            
            logger.info(f"[P] Tech spec created and saved to {spec_file}")
            
            return {
                "success": True,
                "spec": spec_data,
                "file_path": str(spec_file)
            }
            
        except Exception as e:
            logger.error(f"Error creating tech spec: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def analyze_requirements(self, goal: str) -> Dict[str, Any]:
        """
        Analyze and extract requirements from a goal.
        
        Args:
            goal: The project goal/objective
            
        Returns:
            Dictionary containing requirement analysis
        """
        try:
            prompt = f"""
            Analyze the following goal and extract detailed requirements:
            
            Goal: {goal}
            
            Provide a comprehensive requirements analysis including:
            1. Functional requirements (what the system must do)
            2. Non-functional requirements (performance, security, usability)
            3. Technical requirements (infrastructure, integrations)
            4. User requirements (user stories, personas)
            5. Business requirements (objectives, constraints)
            
            Format as a structured requirements document.
            """
            
            analysis_content = call_claude(
                self.anthropic_client,
                prompt,
                "You are an expert business analyst. Extract comprehensive, actionable requirements from project goals."
            )
            
            analysis_data = {
                "goal": goal,
                "content": analysis_content,
                "analyzed_at": datetime.now().isoformat()
            }
            
            logger.info("[P] Requirements analysis completed")
            
            return {
                "success": True,
                "analysis": analysis_data
            }
            
        except Exception as e:
            logger.error(f"Error analyzing requirements: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def estimate_timeline(self, plan_content: str) -> Dict[str, Any]:
        """
        Estimate project timeline based on plan content.
        
        Args:
            plan_content: The project plan content
            
        Returns:
            Dictionary containing timeline estimation
        """
        try:
            prompt = f"""
            Based on the following project plan, provide a realistic timeline estimation:
            
            Plan: {plan_content}
            
            Provide:
            1. Overall project duration
            2. Phase-by-phase timeline
            3. Critical path analysis
            4. Resource allocation timeline
            5. Risk-adjusted estimates
            6. Milestone dates
            
            Consider realistic development timelines and potential blockers.
            """
            
            timeline_content = call_claude(
                self.anthropic_client,
                prompt,
                "You are an expert project manager. Provide realistic, well-reasoned timeline estimates."
            )
            
            timeline_data = {
                "content": timeline_content,
                "estimated_at": datetime.now().isoformat()
            }
            
            logger.info("[P] Timeline estimation completed")
            
            return {
                "success": True,
                "timeline": timeline_data
            }
            
        except Exception as e:
            logger.error(f"Error estimating timeline: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def assess_risks(self, plan_content: str) -> Dict[str, Any]:
        """
        Assess project risks based on plan content.
        
        Args:
            plan_content: The project plan content
            
        Returns:
            Dictionary containing risk assessment
        """
        try:
            prompt = f"""
            Conduct a comprehensive risk assessment for the following project plan:
            
            Plan: {plan_content}
            
            Provide:
            1. Technical risks and mitigation strategies
            2. Resource risks and contingency plans
            3. Timeline risks and buffer recommendations
            4. External dependency risks
            5. Business risks and impact assessment
            6. Risk probability and impact matrix
            
            Prioritize risks by severity and likelihood.
            """
            
            risk_content = call_claude(
                self.anthropic_client,
                prompt,
                "You are an expert risk management consultant. Identify and assess project risks comprehensively."
            )
            
            risk_data = {
                "content": risk_content,
                "assessed_at": datetime.now().isoformat()
            }
            
            logger.info("[P] Risk assessment completed")
            
            return {
                "success": True,
                "assessment": risk_data
            }
            
        except Exception as e:
            logger.error(f"Error assessing risks: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def generate_architecture(self, goal: str, tech_stack: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate system architecture based on goal and tech stack.
        
        Args:
            goal: The project goal/objective
            tech_stack: Optional preferred technology stack
            
        Returns:
            Dictionary containing architecture design
        """
        try:
            tech_stack_text = f"\n\nPreferred Tech Stack: {tech_stack}" if tech_stack else ""
            
            prompt = f"""
            Design a comprehensive system architecture for the following goal:
            
            Goal: {goal}{tech_stack_text}
            
            Provide:
            1. High-level architecture diagram (described in text)
            2. Component breakdown and responsibilities
            3. Data flow and communication patterns
            4. Technology stack recommendations
            5. Scalability considerations
            6. Security architecture
            7. Deployment architecture
            8. Integration points
            
            Make it detailed enough for implementation.
            """
            
            architecture_content = call_claude(
                self.anthropic_client,
                prompt,
                "You are an expert system architect. Design comprehensive, scalable, and secure system architectures."
            )
            
            architecture_data = {
                "goal": goal,
                "tech_stack": tech_stack,
                "content": architecture_content,
                "designed_at": datetime.now().isoformat()
            }
            
            # Save architecture to file
            arch_file = self.plans_dir / f"architecture_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            with open(arch_file, 'w') as f:
                json.dump(architecture_data, f, indent=2)
            
            logger.info(f"[P] Architecture design completed and saved to {arch_file}")
            
            return {
                "success": True,
                "architecture": architecture_data,
                "file_path": str(arch_file)
            }
            
        except Exception as e:
            logger.error(f"Error generating architecture: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    def get_saved_plans(self) -> List[Dict[str, Any]]:
        """
        Get all saved plans.
        
        Returns:
            List of saved plan summaries
        """
        try:
            plans = []
            for plan_file in self.plans_dir.glob("plan_*.json"):
                with open(plan_file, 'r') as f:
                    plan_data = json.load(f)
                    plans.append({
                        "file": plan_file.name,
                        "goal": plan_data.get("goal", "Unknown"),
                        "created_at": plan_data.get("created_at", "Unknown"),
                        "status": plan_data.get("status", "Unknown")
                    })
            
            return plans
            
        except Exception as e:
            logger.error(f"Error getting saved plans: {e}")
            return []