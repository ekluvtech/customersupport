# Salesforce OAuth 2.0 Setup Guide

If you're getting the error "SOAP API login() is disabled by default in this org", you need to use OAuth 2.0 authentication instead.

## Quick Setup (Using Salesforce CLI)

The easiest way to get an access token is using the Salesforce CLI:

```bash
# Install Salesforce CLI if you haven't already
# https://developer.salesforce.com/tools/salesforcecli

# Authenticate to your org
sf org login web --alias myorg

# Get your access token and instance URL
sf org display --target-org myorg
```

This will show you:
- `accessToken`: Use this as `SALESFORCE_ACCESS_TOKEN`
- `instanceUrl`: Use this as `SALESFORCE_INSTANCE_URL`

Then set environment variables:
```bash
export SALESFORCE_ACCESS_TOKEN="your_access_token_here"
export SALESFORCE_INSTANCE_URL="https://yourinstance.salesforce.com"
```

## Manual OAuth 2.0 Setup

### Step 1: Create a Connected App in Salesforce

1. Log in to Salesforce
2. Go to **Setup** (gear icon → Setup)
3. In Quick Find, search for **App Manager**
4. Click **New Connected App**
5. Fill in the required fields:
   - **Connected App Name**: e.g., "Customer Support Agent"
   - **API Name**: Auto-filled
   - **Contact Email**: Your email
6. Enable **OAuth Settings**
7. Set **Callback URL**: `http://localhost:8080/callback` (or your app's callback URL)
8. Select **OAuth Scopes**:
   - Access and manage your data (api)
   - Perform requests on your behalf at any time (refresh_token, offline_access)
9. Click **Save**
10. After saving, you'll see:
    - **Consumer Key** (Client ID)
    - **Consumer Secret** (Client Secret)

### Step 2: Get Access Token

#### Option A: Using OAuth 2.0 Web Server Flow

1. Construct the authorization URL:
```
https://login.salesforce.com/services/oauth2/authorize?
  response_type=code&
  client_id=YOUR_CONSUMER_KEY&
  redirect_uri=http://localhost:8080/callback&
  scope=api refresh_token offline_access
```

2. Open this URL in a browser and authorize
3. You'll be redirected to the callback URL with a `code` parameter
4. Exchange the code for an access token:

```bash
curl https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=authorization_code" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "redirect_uri=http://localhost:8080/callback" \
  -d "code=YOUR_AUTHORIZATION_CODE"
```

5. The response will contain:
   - `access_token`: Use this as `SALESFORCE_ACCESS_TOKEN`
   - `instance_url`: Use this as `SALESFORCE_INSTANCE_URL`

#### Option B: Using Username-Password OAuth Flow

```bash
curl https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=password" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "username=YOUR_USERNAME" \
  -d "password=YOUR_PASSWORD_AND_SECURITY_TOKEN"
```

Note: For password, use: `your_password + your_security_token` (concatenated)

### Step 3: Set Environment Variables

```bash
export SALESFORCE_ACCESS_TOKEN="00D..."
export SALESFORCE_INSTANCE_URL="https://yourinstance.salesforce.com"
```

### Step 4: Refresh Token (Optional but Recommended)

Access tokens expire after a period of time. To get a refresh token:

1. In the OAuth response, you'll get a `refresh_token`
2. Store it securely
3. When the access token expires, refresh it:

```bash
curl https://login.salesforce.com/services/oauth2/token \
  -d "grant_type=refresh_token" \
  -d "client_id=YOUR_CONSUMER_KEY" \
  -d "client_secret=YOUR_CONSUMER_SECRET" \
  -d "refresh_token=YOUR_REFRESH_TOKEN"
```

## Using the Integration

Once you have the access token and instance URL set:

```python
from integrations.salesforce import SalesforceIntegration

# The integration will automatically use OAuth 2.0 if access_token is set
integration = SalesforceIntegration()

# Or explicitly pass credentials
integration = SalesforceIntegration(
    access_token="your_access_token",
    instance_url="https://yourinstance.salesforce.com"
)
```

## Troubleshooting

### "Invalid Session ID" Error
- Your access token has expired
- Get a new access token or use the refresh token

### "Insufficient Access Rights" Error
- Your user profile doesn't have API access enabled
- Go to Setup → Profiles → Your Profile → System Permissions → Enable "API Enabled"

### "IP Restriction" Error
- Your org has IP restrictions
- Add your IP to Setup → Network Access → Trusted IP Ranges

## Alternative: Enable SOAP API (If You Have Admin Access)

If you're a Salesforce admin and want to enable SOAP API login:

1. Go to Setup
2. Search for "API" in Quick Find
3. Enable "API Enabled" for your user profile
4. Note: Some orgs may have this disabled by policy

However, OAuth 2.0 is the recommended and more secure method.

