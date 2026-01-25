"""
test_simple.py - Test básico sin complicaciones
"""

import logging
from pathlib import Path
from dotenv import load_dotenv

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_basic():
    """Test básico de componentes"""
    
    # Load environment
    load_dotenv()
    logger.info("🔧 Environment loaded")
    
    # Test ArXiv tool first (no dependencies)
    try:
        from src.tools.arxiv_tool import ArxivTool
        
        arxiv_tool = ArxivTool()
        result = arxiv_tool._run("machine learning", max_results=2, categories=["cs.LG"])
        
        import json
        result_data = json.loads(result)
        
        if result_data["status"] == "success":
            logger.info(f"✅ ArXiv tool: {result_data['papers_count']} papers found")
        else:
            logger.error(f"❌ ArXiv tool failed: {result_data.get('message')}")
            return False
            
    except Exception as e:
        logger.error(f"❌ ArXiv tool error: {e}")
        return False
    
    # Test Agent Factory
    try:
        # Verify config files exist
        config_files = ["config/agents.yml", "config/tasks.yml", "config/tools.yml"]
        for config_file in config_files:
            if not Path(config_file).exists():
                logger.error(f"❌ Missing config file: {config_file}")
                return False
        
        from src.agents.agent_factory import AgentFactory
        
        factory = AgentFactory()
        logger.info(f"✅ Agent Factory created")
        logger.info(f"Available agents: {factory.list_available_agents()}")
        
        # Try creating an agent
        agent = factory.create_agent("paper_fetcher")
        logger.info(f"✅ Agent created: {agent.role}")
        
    except Exception as e:
        logger.error(f"❌ Agent Factory error: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    # Test Task Factory
    try:
        from src.tasks.task_factory import TaskFactory
        
        task_factory = TaskFactory()
        logger.info(f"✅ Task Factory created")
        logger.info(f"Available tasks: {task_factory.list_available_tasks()}")
        
    except Exception as e:
        logger.error(f"❌ Task Factory error: {e}")
        return False
    
    logger.info("🎉 All basic tests passed!")
    return True

if __name__ == "__main__":
    if test_basic():
        print("✅ Setup is working correctly!")
    else:
        print("❌ There are issues to fix")