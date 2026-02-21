"""Main entry point for the Customer Support Agent"""

import asyncio
import logging
import sys
from pathlib import Path

from agent.core import SupportAgent
from config.loader import load_config

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[
        logging.FileHandler("logs/agent.log"),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger(__name__)


async def main():
    """Main entry point"""
    try:
        # Load configuration
        config = load_config()
        
        # Initialize agent
        agent = SupportAgent(config)
        
        # Start agent
        await agent.start()
        
        logger.info("Customer Support Agent started successfully")
        
        # Keep running
        await agent.run()
        
    except KeyboardInterrupt:
        logger.info("Shutting down agent...")
    except Exception as e:
        logger.error(f"Error starting agent: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    # Create logs directory if it doesn't exist
    Path("logs").mkdir(exist_ok=True)
    
    asyncio.run(main())

