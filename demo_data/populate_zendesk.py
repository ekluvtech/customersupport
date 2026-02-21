"""Script to populate Zendesk with sample tickets for demo purposes"""

import os
import sys
import json
import asyncio
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from integrations.zendesk import ZendeskIntegration

async def populate_zendesk():
    """Populate Zendesk with sample tickets"""
    
    # Check for credentials
    if not all([os.getenv("ZENDESK_SUBDOMAIN"), os.getenv("ZENDESK_EMAIL"), os.getenv("ZENDESK_API_KEY")]):
        print("Error: Zendesk credentials not found in environment variables.")
        print("Please set: ZENDESK_SUBDOMAIN, ZENDESK_EMAIL, ZENDESK_API_KEY")
        return
    
    # Load sample data
    data_file = Path(__file__).parent / "sample_data.json"
    with open(data_file, "r") as f:
        data = json.load(f)
    
    # Initialize Zendesk integration
    integration = ZendeskIntegration()
    
    print("=" * 60)
    print("Populating Zendesk with Sample Tickets")
    print("=" * 60)
    print()
    
    created_tickets = []
    
    for ticket_data in data["tickets"]:
        try:
            print(f"Creating ticket: {ticket_data['subject']}")
            
            ticket = await integration.create_ticket(
                subject=ticket_data["subject"],
                description=ticket_data["description"],
                requester_email=ticket_data["requester_email"],
                requester_name=ticket_data["requester_name"],
            )
            
            created_tickets.append({
                "id": ticket["id"],
                "subject": ticket["subject"],
                "url": ticket.get("url", f"https://{os.getenv('ZENDESK_SUBDOMAIN')}.zendesk.com/agent/tickets/{ticket['id']}")
            })
            
            print(f"  ✓ Created ticket #{ticket['id']}")
            
            # Add tags if supported (would need additional API call)
            # await integration.add_tags(ticket["id"], ticket_data.get("tags", []))
            
        except Exception as e:
            print(f"  ✗ Error creating ticket: {e}")
    
    print()
    print("=" * 60)
    print("Summary")
    print("=" * 60)
    print(f"Successfully created {len(created_tickets)} tickets:")
    print()
    for ticket in created_tickets:
        print(f"  Ticket #{ticket['id']}: {ticket['subject']}")
        print(f"    URL: {ticket['url']}")
        print()
    
    await integration.close()


if __name__ == "__main__":
    asyncio.run(populate_zendesk())

