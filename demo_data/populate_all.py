"""Master script to populate all services with demo data"""

import os
import sys
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


async def populate_all():
    """Populate all services with demo data"""
    
    print("=" * 60)
    print("Populating All Services with Demo Data")
    print("=" * 60)
    print()
    
    services = [
        ("Database", "populate_database.py"),
        ("Zendesk", "populate_zendesk.py"),
        ("Salesforce", "populate_salesforce.py"),
        ("Slack", "populate_slack.py")
    ]
    
    results = {}
    
    for service_name, script_name in services:
        print(f"\n{'=' * 60}")
        print(f"Populating {service_name}")
        print(f"{'=' * 60}\n")
        
        script_path = Path(__file__).parent / script_name
        
        if not script_path.exists():
            print(f"  ⚠ Script not found: {script_name}")
            results[service_name] = "skipped"
            continue
        
        try:
            import importlib.util
            
            if script_name == "populate_slack.py":
                # Slack script is synchronous
                spec = importlib.util.spec_from_file_location("populate_slack", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                module.populate_slack()
                results[service_name] = "success"
            else:
                # Other scripts are async
                spec = importlib.util.spec_from_file_location("populate_script", script_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                
                if script_name == "populate_database.py":
                    await module.populate_database()
                elif script_name == "populate_zendesk.py":
                    await module.populate_zendesk()
                elif script_name == "populate_salesforce.py":
                    await module.populate_salesforce()
                
                results[service_name] = "success"
        
        except Exception as e:
            print(f"  ✗ Error: {e}")
            results[service_name] = f"error: {str(e)}"
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print()
    
    for service_name, result in results.items():
        status_icon = "✓" if result == "success" else "✗" if result.startswith("error") else "⚠"
        print(f"{status_icon} {service_name}: {result}")
    
    print()
    print("=" * 60)
    print("Demo data population complete!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Verify data in each service")
    print("2. Configure the customer support agent")
    print("3. Test queries like: 'What's the status of order #12345?'")
    print()


if __name__ == "__main__":
    asyncio.run(populate_all())

