# Sample Data Overview

This document provides an overview of the sample data loaded in the system and how to use it for testing the customer support agent.

## Data Summary

### Zendesk Tickets (10 tickets)
- **Order delivery issues** (3 tickets)
- **Product defects** (2 tickets)
- **Refund requests** (1 ticket)
- **Account access issues** (1 ticket)
- **Billing questions** (1 ticket)
- **Wrong items received** (1 ticket)
- **Subscription issues** (1 ticket)
- **Damaged products** (1 ticket)
- **Shipping address changes** (1 ticket)
- **Quality/warranty issues** (1 ticket)

### Orders (7 orders)
- Various order statuses: `in_transit`, `delivered`, `cancelled`, `processing`
- Order IDs: ORD-2024-001234, ORD-2024-001567, ORD-2024-000891, ORD-2024-002345, ORD-2024-001890, ORD-2024-002678, ORD-2023-009876
- Customers: 7 different customers with emails and names
- Price range: $49.99 - $3899.99
- Products: Electronics, cameras, laptops, phones, accessories

### Salesforce Cases (5 cases)
- Linked to customer contacts
- Various priorities: High, Medium
- Statuses: New, In Progress
- Types: Problem, Question

### Slack Messages (12 messages)
- Channels: `customer-support`, `billing-support`, `quality-issues`
- Mix of customer messages and agent responses
- Covers various support scenarios

## Customer Information

### Customers in the System

1. **John Doe** (john.doe@example.com)
   - Order: ORD-2024-001234 (Wireless Keyboard, in_transit)
   - Ticket: Order delivery delay

2. **Jane Smith** (jane.smith@example.com)
   - Order: ORD-2024-001567 (Canon EOS R5 Camera, delivered, defective)
   - Ticket: Product defect - camera won't turn on

3. **Mike Johnson** (mike.johnson@example.com)
   - Order: ORD-2024-000891 (Smart Watch, cancelled)
   - Ticket: Refund not processed

4. **Sarah Williams** (sarah.williams@example.com)
   - Ticket: Account access issue

5. **David Brown** (david.brown@example.com)
   - Ticket: Unexpected charge $149.99

6. **Emily Chen** (emily.chen@example.com)
   - Order: ORD-2024-002345 (iPhone 15 Pro, delivered, wrong item)
   - Ticket: Wrong item received

7. **Lisa Anderson** (lisa.anderson@example.com)
   - Order: ORD-2024-001890 (MacBook Pro, delivered, damaged)
   - Ticket: Product arrived damaged

8. **Alex Martinez** (alex.martinez@example.com)
   - Order: ORD-2024-002678 (Gaming Monitor, processing)
   - Ticket: Need to change shipping address

9. **Robert Taylor** (robert.taylor@example.com)
   - Ticket: Subscription billing issue

10. **Jennifer Wilson** (jennifer.wilson@example.com)
    - Order: ORD-2023-009876 (Wireless Headphones, delivered)
    - Ticket: Quality issue - stopped working after 2 weeks

## Order Details

### Order Statuses

- **in_transit**: ORD-2024-001234 (delayed delivery)
- **delivered**: ORD-2024-001567, ORD-2024-002345, ORD-2024-001890, ORD-2023-009876
- **cancelled**: ORD-2024-000891 (refund pending)
- **processing**: ORD-2024-002678 (address change requested)

### Product Categories

- **Electronics**: Keyboards, headphones, monitors
- **Cameras**: Canon EOS R5
- **Computers**: MacBook Pro 16-inch
- **Phones**: iPhone 15 Pro
- **Wearables**: Smart Watch

## Testing Scenarios

### Scenario 1: Order Status Query
**Customer**: John Doe (john.doe@example.com)  
**Question**: "What's the status of my order #ORD-2024-001234?"  
**Expected**: Agent should query database, find order is "in_transit", check tracking, provide delivery information

### Scenario 2: Product Defect
**Customer**: Jane Smith (jane.smith@example.com)  
**Question**: "The camera I received (order #ORD-2024-001567) won't turn on. What should I do?"  
**Expected**: Agent should check order, find Zendesk ticket, provide replacement/return options

### Scenario 3: Refund Status
**Customer**: Mike Johnson (mike.johnson@example.com)  
**Question**: "I cancelled order #ORD-2024-000891 but haven't received my refund. When will it be processed?"  
**Expected**: Agent should check order status (cancelled), refund status (pending), provide timeline

### Scenario 4: Wrong Item
**Customer**: Emily Chen (emily.chen@example.com)  
**Question**: "I ordered iPhone 15 Pro but received iPhone 15 (order #ORD-2024-002345). Can you send the correct one?"  
**Expected**: Agent should verify order, acknowledge error, initiate exchange

### Scenario 5: Damaged Product
**Customer**: Lisa Anderson (lisa.anderson@example.com)  
**Question**: "My MacBook Pro (order #ORD-2024-001890) arrived with a cracked screen. How do I get a replacement?"  
**Expected**: Agent should check order, create/update ticket, process replacement

### Scenario 6: Billing Question
**Customer**: David Brown (david.brown@example.com)  
**Question**: "I see a charge of $149.99 on my credit card. What is this for?"  
**Expected**: Agent should search orders, Slack messages, provide explanation or escalate

### Scenario 7: Account Access
**Customer**: Sarah Williams (sarah.williams@example.com)  
**Question**: "I can't log into my account. Password reset emails aren't arriving."  
**Expected**: Agent should check tickets, verify identity, provide account recovery steps

### Scenario 8: Address Change
**Customer**: Alex Martinez (alex.martinez@example.com)  
**Question**: "I need to change the shipping address for order #ORD-2024-002678. It hasn't shipped yet."  
**Expected**: Agent should check order status, update address if possible

### Scenario 9: Quality/Warranty
**Customer**: Jennifer Wilson (jennifer.wilson@example.com)  
**Question**: "My headphones from order #ORD-2023-009876 stopped working after 2 weeks. Can I return them?"  
**Expected**: Agent should check order date, verify warranty coverage, process return if eligible

### Scenario 10: Cross-Platform Query
**Customer**: Any customer  
**Question**: "I reported an issue yesterday. What's the status of my ticket?"  
**Expected**: Agent should search Zendesk tickets, Slack messages, provide status update

## Data Relationships

```
Customer Email → Orders (by customer_email)
Order ID → Tickets (by order reference in ticket description)
Customer Email → Salesforce Cases (by contact_email)
Customer Email → Slack Messages (by user email)
Order ID → Tracking Information
Ticket → Order (referenced in ticket subject/description)
```

## Query Patterns

### By Order ID
- Orders: `order_id = "ORD-2024-001234"`
- Tickets: Search description/subject for order ID
- Slack: Search messages for order ID

### By Customer Email
- Orders: `customer_email = "john.doe@example.com"`
- Tickets: `requester_email = "john.doe@example.com"`
- Salesforce Cases: `contact_email = "john.doe@example.com"`
- Slack: `user = "john.doe@example.com"`

### By Status
- Orders: `status IN ("in_transit", "delivered", "cancelled", "processing")`
- Tickets: `status IN ("open", "pending", "solved", "closed")`
- Salesforce Cases: `status IN ("New", "In Progress", "Closed")`

## Data Files

- **sample_data.json**: Complete dataset with all tickets, orders, cases, and messages
- **customer_questions.md**: Pre-written questions to test the agent
- **populate_zendesk.py**: Script to load tickets into Zendesk
- **populate_salesforce.py**: Script to load cases into Salesforce
- **populate_slack.py**: Script to post messages to Slack
- **populate_database.py**: Script to load orders into database

## Loading Data

To load all sample data into the systems:

```bash
# Load all data at once
python demo_data/populate_all.py

# Or load individually
python demo_data/populate_database.py
python demo_data/populate_zendesk.py
python demo_data/populate_salesforce.py
python demo_data/populate_slack.py
```

## Testing the Agent

After loading the data, test the agent with questions from `customer_questions.md`:

```bash
# Interactive mode
python -m examples.interactive_chat

# Or via API
python -m agent.api
```

Example queries:
- "What's the status of order #ORD-2024-001234?"
- "I have an issue with my camera order #ORD-2024-001567"
- "When will I get my refund for order #ORD-2024-000891?"
- "I see a charge for $149.99. What is this for?"

## Data Statistics

- **Total Customers**: 10 unique customers
- **Total Orders**: 7 orders
- **Total Tickets**: 10 Zendesk tickets
- **Total Cases**: 5 Salesforce cases
- **Total Messages**: 12 Slack messages
- **Date Range**: December 2023 - January 2024
- **Price Range**: $49.99 - $3,899.99

## Notes

- All email addresses use the `@example.com` domain (safe for testing)
- Order IDs follow pattern: `ORD-YYYY-######`
- Dates are in ISO format: `YYYY-MM-DD`
- All data is realistic but fictional
- Data is designed to test cross-platform integration scenarios

