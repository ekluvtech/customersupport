# Demo Data Setup

This directory contains scripts and sample data to populate Zendesk, Salesforce, Slack, and the order database with realistic demo data for testing the customer support agent.

## Sample Data

The `sample_data.json` file contains:
- **5 sample Zendesk tickets** covering various support scenarios (shipping, defects, refunds, account issues, billing)
- **5 sample orders** with different statuses and customer information
- **3 Salesforce cases** linked to customer contacts
- **6 Slack messages** from customer support channels

## Setup Instructions

### Prerequisites

1. Install required dependencies:
```bash
# For Zendesk
pip install httpx  # Already in requirements.txt

# For Salesforce
pip install simple-salesforce

# For Slack
pip install slack-sdk

# For Database
pip install sqlalchemy psycopg2-binary  # or pymongo for MongoDB
```

2. Set up environment variables:

```bash
# Zendesk
export ZENDESK_SUBDOMAIN="your_subdomain"
export ZENDESK_EMAIL="your_email@example.com"
export ZENDESK_API_KEY="your_api_key"

# Salesforce
export SALESFORCE_USERNAME="your_username"
export SALESFORCE_PASSWORD="your_password"
export SALESFORCE_SECURITY_TOKEN="your_security_token"
export SALESFORCE_INSTANCE_URL="https://yourinstance.salesforce.com"

# Slack
export SLACK_TOKEN="xoxp-your-slack-bot-token"

# Database
export DATABASE_URL="postgresql://ordruser:Admin123@localhost/ordrmgmnt"
# or for MongoDB: mongodb://user:password@localhost/dbname
```

### Populating Data

#### 1. Zendesk Tickets

```bash
python demo_data/populate_zendesk.py
```

This will create 5 sample tickets in your Zendesk instance:
- Order delivery issue (Order #12345)
- Product defect (Camera not working)
- Refund request
- Account access issue
- Billing question

**Note**: Make sure your Zendesk API credentials have permissions to create tickets.

#### 2. Salesforce Cases

```bash
python demo_data/populate_salesforce.py
```

This will:
- Create contacts for customers (if they don't exist)
- Create 3 sample cases linked to those contacts

**Note**: Requires `simple-salesforce` library. Your Salesforce user needs permissions to create Contacts and Cases.

#### 3. Slack Messages

```bash
python demo_data/populate_slack.py
```

This will:
- Create or use existing channels (`customer-support`, `billing-support`)
- Post sample messages to those channels

**Note**: 
- The script sends messages as the bot account
- For a more realistic demo, you may want to manually post messages from different user accounts
- Make sure your Slack bot has permissions to post messages and create channels (if needed)

#### 4. Order Database

```bash
python demo_data/populate_database.py
```

This will:
- Create an `orders` table (if it doesn't exist) in PostgreSQL
- Insert 5 sample orders with various statuses

**Database Schema**:
- `order_id` (Primary Key)
- `customer_email`
- `customer_name`
- `order_date`
- `status` (processing, in_transit, delivered, cancelled)
- `shipping_address`
- `total_amount`
- `items` (JSONB)
- `tracking_number`
- `estimated_delivery`
- `delivery_date`
- `cancellation_date`
- `refund_status`

**Note**: The script is designed for PostgreSQL. For MongoDB, you'll need to modify the script to use PyMongo instead.

### Populating All Services

You can run all scripts sequentially:

```bash
python demo_data/populate_database.py
python demo_data/populate_zendesk.py
python demo_data/populate_salesforce.py
python demo_data/populate_slack.py
```

Or create a master script:

```bash
python demo_data/populate_all.py  # (if created)
```

## Sample Scenarios

After populating the data, you can test these scenarios with the customer support agent:

1. **Order Status Query**:
   - Customer: "What's the status of my order #12345?"
   - Agent should query the database and provide order status

2. **Defect Report**:
   - Customer: "My camera (order #12346) is not working"
   - Agent should retrieve ticket from Zendesk, check order details, and provide assistance

3. **Refund Inquiry**:
   - Customer: "I cancelled order #12347, when will I get my refund?"
   - Agent should check order status, refund status, and ticket information

4. **Billing Question**:
   - Customer: "I see a charge for $49.99, what is this for?"
   - Agent should search Slack messages, check orders, and provide clarification

5. **Cross-Platform Context**:
   - Customer mentions an issue
   - Agent should check Zendesk tickets, Slack messages, and order database to provide comprehensive support

## Customizing Sample Data

Edit `sample_data.json` to:
- Add more tickets, orders, cases, or messages
- Modify customer information
- Change order statuses and details
- Add more realistic scenarios for your use case

## Cleanup

To remove demo data:

1. **Zendesk**: Manually delete tickets through the Zendesk UI or API
2. **Salesforce**: Delete cases and contacts through Salesforce UI or API
3. **Slack**: Delete messages manually (Slack API doesn't support bulk deletion easily)
4. **Database**: 
   ```sql
   DELETE FROM orders WHERE order_id IN ('12345', '12346', '12347', '12348', '12349');
   ```

## Troubleshooting

### Zendesk Errors
- Verify API credentials are correct
- Check that your Zendesk plan allows API access
- Ensure the subdomain is correct (without .zendesk.com)

### Salesforce Errors
- Verify username, password, and security token
- Check that your user has API access enabled
- Ensure the instance URL is correct

### Slack Errors
- Verify bot token has necessary scopes: `chat:write`, `channels:read`, `channels:write`
- Check that the bot is added to the workspace
- Ensure channel names don't conflict with existing channels

### Database Errors
- Verify database URL format is correct
- Check database user permissions (CREATE TABLE, INSERT)
- Ensure PostgreSQL is running (if using PostgreSQL)
- For MongoDB, modify the script to use PyMongo syntax

## Next Steps

After populating demo data:
1. Configure the customer support agent (see main README.md)
2. Test queries like "What's the status of order #12345?"
3. Verify the agent can access and use data from all integrated systems
4. Test cross-platform context retrieval

