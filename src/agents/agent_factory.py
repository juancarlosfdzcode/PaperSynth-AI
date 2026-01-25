"""
Agent Factory - Versión completa y funcional con Gemini
"""

import yaml
import os
import logging
import google.generativeai as genai
from pathlib import Path
from typing import Dict, Any, List
from crewai import Agent, LLM
from dotenv import load_dotenv

class AgentFactory:
    def __init__(self, config_path: str = "config"):
        # Load environment FIRST
        load_dotenv()
        
        self.config_path = Path(config_path)
        
        # Load all configurations
        self.agents_config = self._load_agents_config()
        self.tools_config = self._load_tools_config()
        
        # Setup Gemini
        self._setup_gemini()
        self.default_llm = self._create_default_llm()
    
    def _load_agents_config(self) -> Dict[str, Any]:
        """Load agents configuration from YAML"""
        config_file = self.config_path / "agents.yml"
        if not config_file.exists():
            raise FileNotFoundError(f"Agents config file not found: {config_file}")
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        if not config or 'agents' not in config:
            raise ValueError("Invalid agents configuration file")
            
        return config
    
    def _load_tools_config(self) -> Dict[str, Any]:
        """Load tools configuration from YAML"""
        config_file = self.config_path / "tools.yml"
        if not config_file.exists():
            logging.warning(f"Tools config file not found: {config_file}")
            return {"tools": {}}
            
        with open(config_file, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
            
        return config if config else {"tools": {}}
    
    def _setup_gemini(self):
        """Setup Gemini API"""
        api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("❌ GEMINI_API_KEY is required in .env file")
        
        # Configure Gemini
        genai.configure(api_key=api_key)
        
        # Set environment for CrewAI
        os.environ['GOOGLE_API_KEY'] = api_key
        
        logging.info("✅ Gemini configured successfully")
    
    def _create_default_llm(self):
        """Create Gemini LLM or return None for CrewAI default"""
        try:
            # Try different Gemini model formats for CrewAI
            llm_configs = [
                "gemini/gemini-1.5-flash",
                "google/gemini-1.5-flash", 
                "gemini-1.5-flash"
            ]
            
            for model_format in llm_configs:
                try:
                    llm = LLM(
                        model=model_format,
                        temperature=0.1
                    )
                    logging.info(f"✅ LLM created with format: {model_format}")
                    return llm
                except Exception as e:
                    logging.debug(f"Failed with format {model_format}: {e}")
                    continue
            
            logging.warning("Could not create Gemini LLM, using CrewAI default")
            return None
            
        except Exception as e:
            logging.warning(f"LLM creation failed: {e}")
            return None
    
    def _create_tool_instances(self, tool_names: List[str]) -> List[Any]:
        """Create tool instances from tool names"""
        tools = []
        
        for tool_name in tool_names:
            try:
                if tool_name == "arxiv_fetcher":
                    from src.tools.arxiv_tool import ArxivTool
                    tools.append(ArxivTool())
                elif tool_name == "gemini_analyzer":
                    from src.tools.gemini_tool import GeminiTool
                    tools.append(GeminiTool())
                elif tool_name == "trend_detector":
                    from src.tools.trend_tool import TrendTool
                    tools.append(TrendTool())
                else:
                    logging.warning(f"Unknown tool: {tool_name}")
                    
            except Exception as e:
                logging.error(f"Error creating tool {tool_name}: {e}")
        
        return tools
    
    def create_agent(self, agent_name: str) -> Agent:
        """Create an agent from YAML configuration"""
        if agent_name not in self.agents_config["agents"]:
            available = list(self.agents_config["agents"].keys())
            raise ValueError(f"Agent '{agent_name}' not found. Available: {available}")
        
        agent_config = self.agents_config["agents"][agent_name]
        
        # Create tools
        tool_names = agent_config.get("tools", [])
        tools = self._create_tool_instances(tool_names)
        
        # Prepare agent parameters
        agent_params = {
            "role": agent_config["role"],
            "goal": agent_config["goal"], 
            "backstory": agent_config["backstory"],
            "tools": tools,
            "verbose": agent_config["config"].get("verbose", True),
            "allow_delegation": agent_config["config"].get("allow_delegation", False),
            "max_iter": agent_config["config"].get("max_iter", 3),
            "memory": agent_config["config"].get("memory", True)
        }
        
        # Add LLM if available
        if self.default_llm is not None:
            agent_params["llm"] = self.default_llm
        
        try:
            agent = Agent(**agent_params)
            logging.info(f"✅ Agent '{agent_name}' created successfully")
            return agent
            
        except Exception as e:
            logging.error(f"❌ Error creating agent '{agent_name}': {e}")
            raise
    
    def list_available_agents(self) -> List[str]:
        """Get list of available agent names"""
        return list(self.agents_config["agents"].keys())
    
    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """Get configuration for a specific agent"""
        if agent_name not in self.agents_config["agents"]:
            raise ValueError(f"Agent '{agent_name}' not found")
        return self.agents_config["agents"][agent_name]