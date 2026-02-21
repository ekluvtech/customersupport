# Integration Guide

This document provides details on how to use the Salesforce and Slack integrations.

## Salesforce Integration

### Setup

1. No additional packages required! Uses `httpx` (already in requirements.txt)

2. Set environment variables (OAuth 2.0 - Recommended):


   Or use username-password OAuth flow:
```bash
export SALESFORCE_CLIENT_ID="your_consumer_key"
export SALESFORCE_CLIENT_SECRET="your_consumer_secret"
export SALESFORCE_USERNAME="your_username"
export SALESFORCE_PASSWORD="your_password"
export SALESFORCE_SECURITY_TOKEN="your_security_token"  # Optional
```

### Usage

```python
from integrations.salesforce import SalesforceIntegration

# Initialize (uses environment variables by default)
integration = SalesforceIntegration()

# Get a case
case = await integration.get_case("500xx0000012345")

# Create a case
new_case = await integration.create_case(
    subject="Order Issue",
    description="Customer reports order #12345 not delivered",
    contact_email="customer@example.com"
)

# Update a case
updated_case = await integration.update_case(
    case_id="500xx0000012345",
    status="In Progress",
    comment="Investigating the issue"
)

# Query cases
cases = await integration.query_cases(
    contact_email="customer@example.com",
    status="New",
    limit=50
)

# Cleanup
await integration.close()
```

### Features

- **Automatic Contact Management**: Contacts are automatically created or retrieved by email
- **Contact Caching**: Email to Contact ID mappings are cached for performance
- **Async Support**: All operations are async and run in thread pools
- **Error Handling**: Comprehensive error handling and logging

### Methods

- `get_case(case_id)`: Get case details by ID
- `create_case(subject, description, contact_email)`: Create a new case
- `update_case(case_id, status=None, comment=None)`: Update case status or add comment
- `query_cases(contact_email=None, status=None, limit=100)`: Query cases with filters

## Slack Integration

### Setup

1. Install the required package:
```bash
pip install slack-sdk
```

2. Create a Slack App and get a Bot Token:
   - Go to https://api.slack.com/apps
   - Create a new app
   - Go to "OAuth & Permissions"
   - Add Bot Token Scopes:
     - `channels:history`
     - `channels:read`
     - `groups:history`
     - `groups:read`
     - `search:read`
     - `chat:write`
   - Install app to workspace
   - Copy the Bot User OAuth Token

3. Set environment variable:
```bash
export SLACK_TOKEN="xoxb-your-bot-token"
```

### Usage

```python
from integrations.slack import SlackIntegration

# Initialize (uses environment variable by default)
integration = SlackIntegration()

# Search messages
messages = await integration.search_messages(
    query="order #12345",
    channel="customer-support"  # Optional
)

# Get channel history
history = await integration.get_channel_history(
    channel="customer-support",
    limit=100
)

# Send a message
response = await integration.send_message(
    channel="customer-support",
    text="I've looked into this issue and here's the update...",
    thread_ts=None  # Optional: reply in thread
)

# Cleanup
await integration.close()
```

### Features

- **Channel Name Resolution**: Automatically resolves channel names to IDs
- **Channel Caching**: Channel name to ID mappings are cached
- **Async Support**: All operations are async and run in thread pools
- **Error Handling**: Comprehensive error handling and logging

### Methods

- `search_messages(query, channel=None)`: Search Slack messages
- `get_channel_history(channel, limit=100)`: Get channel message history
- `send_message(channel, text, thread_ts=None)`: Send a message to a channel

### Required Slack Permissions

The Slack bot needs the following scopes:
- `channels:history` - Read public channel messages
- `channels:read` - View public channel details
- `groups:history` - Read private channel messages
- `groups:read` - View private channel details
- `search:read` - Search messages
- `chat:write` - Send messages

## Error Handling

Both integrations handle errors gracefully:

- **Missing Credentials**: Warning logged, operations will fail with clear error messages
- **API Errors**: Full error details logged, exceptions raised with context
- **Network Issues**: Errors caught and logged with helpful messages

## Thread Safety

Both integrations use `ThreadPoolExecutor` to run synchronous API calls in async contexts, making them thread-safe and non-blocking.

## Cleanup

Always call `await integration.close()` when done to properly shutdown thread pools and clean up resources.

