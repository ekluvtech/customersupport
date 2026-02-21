# Sample Customer Questions for Testing

This document contains realistic customer questions based on the sample data that can be used to test the customer support agent.

## Order Status Questions

1. **Basic Order Status**
   - "What's the status of my order #ORD-2024-001234?"
   - "I placed an order #ORD-2024-001234 on January 2nd. Has it shipped yet?"
   - "When will my order #ORD-2024-001234 arrive?"

2. **Delayed Order**
   - "My order #ORD-2024-001234 was supposed to arrive on January 5th but it's now January 8th and I still haven't received it. What's going on?"
   - "The tracking for order #ORD-2024-001234 hasn't updated in 2 days. Can you check what's happening?"

3. **Order Details**
   - "Can you tell me what items are in order #ORD-2024-001234?"
   - "What's the total amount for order #ORD-2024-001567?"
   - "Where is order #ORD-2024-001890 being shipped to?"

## Product Issues

4. **Defective Products**
   - "The camera I received (order #ORD-2024-001567) won't turn on. What should I do?"
   - "I got a defective product. How do I get a replacement?"
   - "The headphones from order #ORD-2023-009876 stopped working after 2 weeks. Can I return them?"

5. **Wrong Item Received**
   - "I ordered an iPhone 15 Pro but received a regular iPhone 15 instead (order #ORD-2024-002345). Can you send me the correct one?"
   - "The item I received doesn't match what I ordered. What's the process for an exchange?"

6. **Damaged Products**
   - "My MacBook Pro (order #ORD-2024-001890) arrived with a cracked screen. How do I get a replacement?"
   - "The product I received was damaged in shipping. What are my options?"

## Billing & Refunds

7. **Refund Status**
   - "I cancelled order #ORD-2024-000891 on January 3rd but haven't received my refund yet. When will it be processed?"
   - "How long does it take to get a refund after cancelling an order?"
   - "Can you check the status of my refund for order #ORD-2024-000891?"

8. **Billing Questions**
   - "I see a charge of $149.99 on my credit card that I don't recognize. What is this for?"
   - "I was charged twice this month for my subscription. Can you refund the duplicate charge?"
   - "Can you explain the $149.99 charge from January 4th?"

9. **Payment Issues**
   - "What payment method was used for order #ORD-2024-001234?"
   - "I want to dispute a charge. Who should I contact?"

## Account & Access

10. **Login Issues**
    - "I can't log into my account. I've tried resetting my password but I'm not receiving the reset emails."
    - "My email is sarah.williams@example.com. Can you help me regain access to my account?"
    - "Password reset emails aren't arriving. What should I do?"

11. **Account Information**
    - "Can you send me my order history?"
    - "What's my recent order history?"
    - "I need an invoice for order #ORD-2024-001567 for tax purposes."

## Shipping & Delivery

12. **Address Changes**
    - "I need to change the shipping address for order #ORD-2024-002678. It hasn't shipped yet."
    - "Can I update my delivery address before my order ships?"
    - "I entered the wrong address for order #ORD-2024-002678. Can you fix it?"

13. **Tracking & Delivery**
    - "What's the tracking number for order #ORD-2024-001567?"
    - "When will order #ORD-2024-002678 be delivered?"
    - "Which carrier is delivering my order #ORD-2024-001234?"

## Subscription & Services

14. **Subscription Issues**
    - "I was charged twice for my subscription this month. Can you refund one of the charges?"
    - "How do I cancel my subscription?"
    - "What's included in my premium subscription?"

## Multi-System Queries (Complex Scenarios)

15. **Cross-Platform Questions**
    - "I reported an issue with order #ORD-2024-001234 yesterday. What's the status of my ticket?"
    - "I saw a discussion about order #ORD-2024-001567 in your support channel. Can you update me on the resolution?"
    - "I sent an email about a billing issue. Has anyone looked into it yet?"

16. **Historical Context**
    - "I had an issue with order #ORD-2024-001567 last week. What was the resolution?"
    - "What's the history of all my support requests?"
    - "Can you check if there are any open tickets for my account?"

## Urgent/Escalation Scenarios

17. **Time-Sensitive Issues**
    - "URGENT: I need order #ORD-2024-001234 for work tomorrow. Can you expedite delivery?"
    - "I have a photography assignment next week and my camera (order #ORD-2024-001567) doesn't work. Can you send a replacement ASAP?"
    - "My laptop for business arrived damaged (order #ORD-2024-001890). I need a replacement immediately."

18. **Follow-up Questions**
    - "I reported an issue 2 days ago. What's the update?"
    - "Has my replacement order shipped yet?"
    - "Is my refund being processed?"

## Product Information

19. **Product Details**
    - "What model iPhone did I receive in order #ORD-2024-002345?"
    - "Can you tell me the specifications of the camera from order #ORD-2024-001567?"
    - "What's the SKU for the item in order #ORD-2024-001234?"

## Customer Service Actions

20. **Request Actions**
    - "Can you create a ticket for my delayed order #ORD-2024-001234?"
    - "I need to return the defective camera from order #ORD-2024-001567. How do I do that?"
    - "Can you escalate my refund request for order #ORD-2024-000891?"

---

## Testing Scenarios by Complexity

### Simple Queries (Single System)
- Order status questions (#1-3)
- Product information (#19)
- Basic billing questions (#8)

### Medium Complexity (Single System, Multiple Steps)
- Product issues (#4-6)
- Refund status (#7)
- Account access (#10)
- Shipping changes (#12)

### Complex Queries (Cross-System Integration)
- Multi-system queries (#15)
- Historical context (#16)
- Follow-up questions (#18)

### Urgent Scenarios (Time-Sensitive)
- Time-sensitive issues (#17)
- Escalation scenarios (#20)

---

## Expected Agent Behaviors to Test

1. **Data Retrieval**: Can the agent retrieve information from multiple systems?
2. **Context Awareness**: Does the agent remember previous interactions?
3. **Action Taking**: Can the agent create tickets, update orders, etc.?
4. **Cross-Platform Integration**: Can the agent correlate data from Zendesk, database, and Slack?
5. **Error Handling**: How does the agent handle missing or incorrect order numbers?
6. **Identity Verification**: Does the agent verify customer identity before accessing sensitive data?
7. **Proactive Suggestions**: Does the agent suggest solutions or next steps?

---

## Usage

Use these questions to test the customer support agent:

```bash
# Interactive mode
python -m examples.interactive_chat

# Then ask any of the questions above
```

Or test via API:

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "message": "What is the status of my order #ORD-2024-001234?",
    "user_id": "john.doe@example.com",
    "metadata": {"email": "john.doe@example.com", "order_number": "ORD-2024-001234"}
  }'
```

