"""
Crew Manager - Carga y ejecuta crews desde configuración YAML
"""

import yaml
from pathlib import Path
from typing import Dict, Any
import logging
import datetime
import json
from crewai import Crew
from src.agents.agent_factory import AgentFactory
from src.tasks.task_factory import TaskFactory

class CrewManager:
    def __init__(self, config_path: str = "config"):
        self.config_path = Path(config_path)
        self.settings = self._load_settings()
        self.agent_factory = AgentFactory(config_path)
        self.task_factory = TaskFactory(config_path)
        
    def _load_settings(self) -> Dict[str, Any]:
        """Load general settings"""
        with open(self.config_path / "settings.yml", 'r') as f:
            return yaml.safe_load(f)
    
    def _load_crews_config(self) -> Dict[str, Any]:
        """Load crews configuration"""
        with open(self.config_path / "crews.yml", 'r') as f:
            return yaml.safe_load(f)
    
    def create_crew(self, crew_name: str, **context_vars) -> Crew:
        """Create a crew from YAML configuration"""
        crews_config = self._load_crews_config()
        crew_config = crews_config["crews"][crew_name]
        
        # Create agents
        agents = []
        for agent_name in crew_config["agents"]:
            agent = self.agent_factory.create_agent(agent_name)
            agents.append(agent)
        
        # Create tasks with context
        tasks = []
        for task_name in crew_config["tasks"]:
            task = self.task_factory.create_task(task_name, agents, **context_vars)
            tasks.append(task)
        
        # Create crew
        crew = Crew(
            agents=agents,
            tasks=tasks,
            verbose=crew_config["config"].get("verbose", True),
            memory=crew_config["config"].get("memory", False)
        )
        
        return crew
    
    def execute_crew(self, crew_name: str, **context_vars):
        """Execute a crew by name"""
        logging.info(f"🚀 Executing crew: {crew_name}")
        crew = self.create_crew(crew_name, **context_vars)
        result = crew.kickoff()
        logging.info(f"✅ Crew {crew_name} completed")

        Path("outputs").mkdir(exist_ok=True)

        output_data = {
            "crew_name": crew_name,
            "timestamp": datetime.now().isoformat(),
            "result": str(result)
        }

        with open("outputs/crew_results.json", 'w') as f:
            json.dump(output_data, f, indent=2)
        
        logging.info("💾 Results saved to outputs/crew_results.json")
        
        return result
