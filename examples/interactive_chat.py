"""Interactive Chat Example"""

import asyncio
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from agent.core import SupportAgent
from config.loader import load_config


async def interactive_chat():
    """Interactive chat interface"""
    print("=" * 60)
    print("Customer Support Agent - Interactive Chat")
    print("=" * 60)
    print("Type 'quit' or 'exit' to end the conversation\n")
    
    try:
        # Load configuration
        config = load_config()
        
        # Initialize agent
        agent = SupportAgent(config)
        await agent.start()
        
        print("Agent is ready! How can I help you today?\n")
        
        user_id = input("Enter your user ID (optional, press Enter to skip): ").strip() or None
        channel = input("Enter channel (optional, press Enter to skip): ").strip() or None
        
        print("\n" + "-" * 60 + "\n")
        
        while True:
            # Get user input
            user_message = input("You: ").strip()
            
            if user_message.lower() in ["quit", "exit", "q"]:
                print("\nGoodbye!")
                break
            
            if not user_message:
                continue
            
            # Optional metadata extraction
            metadata = {}
            if user_id:
                metadata["user_id"] = user_id
            
            # Process message
            try:
                response = await agent.process_message(
                    message=user_message,
                    user_id=user_id,
                    channel=channel,
                    metadata=metadata
                )
                
                print(f"Agent: {response}\n")
            
            except KeyboardInterrupt:
                print("\n\nInterrupted. Goodbye!")
                break
            except Exception as e:
                print(f"Error: {e}\n")
        
        # Cleanup
        await agent.stop()
    
    except FileNotFoundError as e:
        print(f"Configuration error: {e}")
        print("Please create config/config.yaml from config/config.example.yaml")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(interactive_chat())

