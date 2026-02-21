"""Script to populate Salesforce with sample cases for demo purposes"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.salesforce import SalesforceIntegration


async def populate_salesforce():
    """Populate Salesforce with sample cases using REST API"""
    
    # Load sample data
    data_file = Path(__file__).parent / "sample_data.json"
    with open(data_file, "r") as f:
        data = json.load(f)
    
    # Initialize Salesforce integration (uses environment variables)
    integration = SalesforceIntegration()
    
    if not integration.client:
        print("Error: Salesforce client not initialized.")
        print("\nRECOMMENDED (OAuth 2.0 Access Token):")
        print("  Set: SALESFORCE_ACCESS_TOKEN and SALESFORCE_INSTANCE_URL")
        print("\n  To get access token:")
        print("    1. Install Salesforce CLI: https://developer.salesforce.com/tools/salesforcecli")
        print("    2. Run: sf org login web --alias myorg")
        print("    3. Run: sf org display --target-org myorg")
        print("    4. Copy the 'accessToken' and 'instanceUrl' values")
        print("\nALTERNATIVE (Username-Password OAuth Flow):")
        print("  Set: SALESFORCE_CLIENT_ID, SALESFORCE_CLIENT_SECRET, SALESFORCE_USERNAME, SALESFORCE_PASSWORD")
        print("\nSee integrations/SALESFORCE_OAUTH_SETUP.md for detailed instructions")
        return
    
    print("=" * 60)
    print("Populating Salesforce with Sample Cases")
    print("=" * 60)
    print()
    
    # Create cases
    created_cases = []
    
    for case_data in data["salesforce_cases"]:
        try:
            print(f"Creating case: {case_data['subject']}")
            
            case = await integration.create_case(
                subject=case_data["subject"],
                description=case_data["description"],
                contact_email=case_data["contact_email"]
            )
            
            case_instance_url = integration.instance_url or ""
            case_url = f"{case_instance_url}/{case['Id']}" if case_instance_url else f"Case {case['Id']}"
            
            created_cases.append({
                "id": case["Id"],
                "subject": case_data["subject"],
                "url": case_url
            })
            
            print(f"  ✓ Created case {case['Id']}")
            
        except Exception as e:
            print(f"  ✗ Error creating case: {e}")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Successfully created {len(created_cases)} cases:")
    print()
    for case in created_cases:
        print(f"  Case {case['id']}: {case['subject']}")
        print(f"    URL: {case['url']}")
        print()
    
    await integration.close()


if __name__ == "__main__":
    asyncio.run(populate_salesforce())
