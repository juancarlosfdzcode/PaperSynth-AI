"""
Task Factory - Crear tareas desde configuración YAML
"""

import yaml
from pathlib import Path
from typing import Dict, Any, List
from crewai import Task, Agent
import logging

class TaskFactory:
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.tasks_config = self._load_tasks_config()
        
    def _load_tasks_config(self) -> Dict[str, Any]:
        """Load tasks configuration from YAML"""
        config_file = self.config_path / "tasks.yml"
        if not config_file.exists():
            raise FileNotFoundError(f"Tasks config file not found: {config_file}")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        if not config or 'tasks' not in config:
            raise ValueError("Invalid tasks configuration file")
            
        return config
    
    def _find_agent_by_name(self, agent_name: str, agents: List[Agent]) -> Agent:
        """Find agent by role name in the agents list"""
        agent_roles = {
            "paper_fetcher": "AI Research Paper Collector",
            "content_analyzer": "AI Research Content Analyst", 
            "trend_detector": "Research Trend Analyst",
            "synthesis_writer": "Research Report Synthesizer"
        }
        
        target_role = agent_roles.get(agent_name, agent_name)
        
        for agent in agents:
            if agent.role == target_role:
                return agent
                
        # If not found by role, try by approximate matching
        for agent in agents:
            if agent_name.lower() in agent.role.lower():
                return agent
                
        raise ValueError(f"Agent with role '{target_role}' not found in agents list")
    
    def create_task(self, task_name: str, agents: List[Agent], **context_vars) -> Task:
        """Create a task from YAML configuration with context variables"""
        if task_name not in self.tasks_config["tasks"]:
            available = list(self.tasks_config["tasks"].keys())
            raise ValueError(f"Task '{task_name}' not found. Available: {available}")
        
        task_config = self.tasks_config["tasks"][task_name]
        
        # Get the agent for this task
        agent_name = task_config["config"]["agent"]
        agent = self._find_agent_by_name(agent_name, agents)
        
        # Format description and expected_output with context variables
        description = task_config["description"]
        expected_output = task_config["expected_output"]
        
        # Safe formatting - only replace if variables exist
        if context_vars:
            try:
                description = description.format(**context_vars)
                expected_output = expected_output.format(**context_vars)
            except KeyError as e:
                logging.warning(f"Missing context variable: {e}")
        
        # Create output file path if specified
        output_file = None
        if "output_file" in task_config["config"]:
            output_file = task_config["config"]["output_file"]
            # Ensure output directory exists
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create task
        task = Task(
            description=description,
            expected_output=expected_output,
            agent=agent,
            output_file=output_file
        )
        
        return task
    
    def list_available_tasks(self) -> List[str]:
        """Get list of available task names"""
        return list(self.tasks_config["tasks"].keys())
    
    def get_task_dependencies(self, task_name: str) -> List[str]:
        """Get dependencies for a task"""
        if task_name not in self.tasks_config["tasks"]:
            return []
        
        task_config = self.tasks_config["tasks"][task_name]
        return task_config["config"].get("depends_on", [])