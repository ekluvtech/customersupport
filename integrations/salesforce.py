"""Salesforce Integration using REST API with OAuth 2.0"""

import logging
import os
import asyncio
from typing import Dict, Any, Optional, List
import httpx

logger = logging.getLogger(__name__)


class SalesforceIntegration:
    """Integration with Salesforce CRM using REST API and OAuth 2.0"""
    
    def __init__(
        self,
        access_token: Optional[str] = None,
        instance_url: Optional[str] = None,
        client_id: Optional[str] = None,
        client_secret: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        security_token: Optional[str] = None
    ):
        """
        Initialize Salesforce integration using REST API with OAuth 2.0
        
        Recommended method: Direct OAuth 2.0 access token
        - access_token: OAuth 2.0 access token
        - instance_url: Salesforce instance URL (e.g., https://yourinstance.salesforce.com)
        
        Alternative method: Username-Password OAuth flow (if you have client_id/client_secret)
        - client_id: Connected App Consumer Key
        - client_secret: Connected App Consumer Secret
        - username: Salesforce username
        - password: Salesforce password
        - security_token: Salesforce security token (optional if IP is allowlisted)
        
        Environment variables:
        - SALESFORCE_ACCESS_TOKEN: OAuth access token (recommended)
        - SALESFORCE_INSTANCE_URL: Instance URL
        - SALESFORCE_CLIENT_ID: Connected App Consumer Key (for username-password flow)
        - SALESFORCE_CLIENT_SECRET: Connected App Consumer Secret (for username-password flow)
        - SALESFORCE_USERNAME: Username (for username-password flow)
        - SALESFORCE_PASSWORD: Password (for username-password flow)
        - SALESFORCE_SECURITY_TOKEN: Security token (for username-password flow)
        """
        self.access_token = access_token or os.getenv("SALESFORCE_ACCESS_TOKEN")
        self.instance_url = instance_url or os.getenv("SALESFORCE_INSTANCE_URL")
        self.client_id = client_id or os.getenv("SALESFORCE_CLIENT_ID")
        self.client_secret = client_secret or os.getenv("SALESFORCE_CLIENT_SECRET")
        self.username = username or os.getenv("SALESFORCE_USERNAME")
        self.password = password or os.getenv("SALESFORCE_PASSWORD")
        self.security_token = security_token or os.getenv("SALESFORCE_SECURITY_TOKEN")
        
        self.client: Optional[httpx.AsyncClient] = None
        self._contact_cache: Dict[str, str] = {}
        self._initialized = False
        
        # Normalize instance URL
        if self.instance_url:
            self.instance_url = self.instance_url.rstrip("/")
            if not self.instance_url.startswith("https://"):
                self.instance_url = f"https://{self.instance_url}"
        
        # Initialize client synchronously for access token method
        self._initialize_client_sync()
    
    def _initialize_client_sync(self):
        """Initialize the HTTP client synchronously (for access token method)"""
        # Method 1: Use access token directly (recommended)
        if self.access_token and self.instance_url:
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            logger.info(f"Salesforce REST API client initialized with OAuth 2.0 access token")
            self._initialized = True
            return
        
        # Method 2: Username-Password OAuth flow (needs async initialization)
        if all([self.client_id, self.client_secret, self.username, self.password]):
            logger.info("Username-password OAuth credentials provided (will authenticate on first use)")
            self._initialized = False  # Will initialize async on first use
            return
        
        # No valid credentials
        logger.warning(
            "Salesforce credentials not configured.\n"
            "Recommended: Set SALESFORCE_ACCESS_TOKEN and SALESFORCE_INSTANCE_URL\n"
            "Alternative: Set SALESFORCE_CLIENT_ID, SALESFORCE_CLIENT_SECRET, "
            "SALESFORCE_USERNAME, SALESFORCE_PASSWORD"
        )
        self.client = None
    
    async def _ensure_initialized(self):
        """Ensure the client is initialized (handles async initialization for username-password flow)"""
        if self._initialized and self.client:
            return
        
        # If we have username-password credentials but no client, authenticate
        if all([self.client_id, self.client_secret, self.username, self.password]) and not self.client:
            try:
                await self._authenticate_username_password()
                self._initialized = True
            except Exception as e:
                logger.error(f"Failed to authenticate with username/password: {e}")
                raise
    
    async def _test_connection(self):
        """Test the connection to Salesforce (optional - can be called after initialization)"""
        if not self.client:
            return
        
        try:
            response = await self.client.get(f"{self.instance_url}/services/data/v58.0/")
            response.raise_for_status()
            logger.info("Salesforce connection test successful")
        except Exception as e:
            logger.error(f"Salesforce connection test failed: {e}")
            raise
    
    async def _authenticate_username_password(self):
        """Authenticate using username-password OAuth flow"""
        login_url = "https://login.salesforce.com/services/oauth2/token"
        
        data = {
            "grant_type": "password",
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "username": self.username,
            "password": self.password + (self.security_token or "")
        }
        
        async with httpx.AsyncClient() as temp_client:
            response = await temp_client.post(login_url, data=data)
            response.raise_for_status()
            token_data = response.json()
            
            self.access_token = token_data["access_token"]
            self.instance_url = token_data["instance_url"].rstrip("/")
            
            # Initialize client with access token
            self.client = httpx.AsyncClient(
                headers={
                    "Authorization": f"Bearer {self.access_token}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )
            
            logger.info("Salesforce authentication successful using username-password OAuth flow")
    
    async def _get_api_version(self) -> str:
        """Get the latest API version"""
        # Default to v58.0, but you can query available versions
        return "v58.0"
    
    async def _request(self, method: str, endpoint: str, **kwargs) -> Any:
        """Make a REST API request to Salesforce"""
        await self._ensure_initialized()
        
        if not self.client:
            raise ValueError("Salesforce client not initialized. Check your credentials.")
        
        api_version = await self._get_api_version()
        url = f"{self.instance_url}/services/data/{api_version}{endpoint}"
        
        response = await self.client.request(method, url, **kwargs)
        
        # Better error handling
        if response.status_code == 401:
            raise ValueError("Authentication failed. Access token may have expired.")
        elif response.status_code == 404:
            raise ValueError(f"Resource not found: {endpoint}")
        elif not response.is_success:
            error_detail = "Unknown error"
            try:
                error_response = response.json()
                if isinstance(error_response, list) and len(error_response) > 0:
                    error_detail = error_response[0].get("message", str(error_response))
                elif isinstance(error_response, dict):
                    error_detail = error_response.get("message", str(error_response))
                else:
                    error_detail = response.text
            except:
                error_detail = response.text
            
            logger.error(f"Salesforce API error {response.status_code}: {error_detail}")
            raise ValueError(f"Salesforce API error {response.status_code}: {error_detail}")
        
        if response.content:
            return response.json()
        return None
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a Salesforce tool"""
        if tool_name == "get_case":
            return await self.get_case(parameters["case_id"])
        elif tool_name == "create_case":
            return await self.create_case(
                parameters["subject"],
                parameters["description"],
                parameters["contact_email"]
            )
        elif tool_name == "update_case":
            return await self.update_case(
                parameters["case_id"],
                parameters.get("status"),
                parameters.get("comment")
            )
        elif tool_name == "query_cases":
            return await self.query_cases(
                parameters.get("contact_email"),
                parameters.get("status"),
                parameters.get("limit", 100)
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def get_case(self, case_id: str) -> Dict[str, Any]:
        """Get case details from Salesforce"""
        try:
            result = await self._request("GET", f"/sobjects/Case/{case_id}")
            return result
        except Exception as e:
            logger.error(f"Error getting case {case_id}: {e}")
            raise
    
    async def create_case(
        self,
        subject: str,
        description: str,
        contact_email: str
    ) -> Dict[str, Any]:
        """Create a new case in Salesforce"""
        # Get or create contact
        contact_id = await self._get_or_create_contact(contact_email)
        if not contact_id:
            raise ValueError(f"Could not get or create contact for {contact_email}")
        
        try:
            case_data = {
                "Subject": subject,
                "Description": description,
                "ContactId": contact_id,
                "Status": "New",
                "Origin": "Web"
            }
            
            result = await self._request("POST", "/sobjects/Case/", json=case_data)
            
            # Fetch the created case
            case_id = result["id"]
            case = await self.get_case(case_id)
            return case
        except Exception as e:
            logger.error(f"Error creating case: {e}")
            raise
    
    async def update_case(
        self,
        case_id: str,
        status: Optional[str] = None,
        comment: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a Salesforce case"""
        try:
            update_data = {}
            if status:
                update_data["Status"] = status
            
            if comment:
                # Try to create a case comment
                try:
                    comment_data = {
                        "ParentId": case_id,
                        "CommentBody": comment,
                        "IsPublished": True
                    }
                    await self._request("POST", "/sobjects/CaseComment/", json=comment_data)
                except Exception as e:
                    logger.warning(f"Could not create case comment: {e}")
                    # Fall back to updating description
                    case = await self.get_case(case_id)
                    current_desc = case.get("Description", "")
                    update_data["Description"] = f"{current_desc}\n\n{comment}".strip()
            
            if update_data:
                await self._request("PATCH", f"/sobjects/Case/{case_id}", json=update_data)
            
            # Fetch updated case
            case = await self.get_case(case_id)
            return case
        except Exception as e:
            logger.error(f"Error updating case {case_id}: {e}")
            raise
    
    async def query_cases(
        self,
        contact_email: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Query cases from Salesforce"""
        try:
            query = "SELECT Id, Subject, Status, ContactId, CreatedDate FROM Case WHERE 1=1"
            
            if contact_email:
                contact_id = await self._get_or_create_contact(contact_email, create_if_not_exists=False)
                if contact_id:
                    query += f" AND ContactId = '{contact_id}'"
            
            if status:
                query += f" AND Status = '{status}'"
            
            query += f" ORDER BY CreatedDate DESC LIMIT {min(limit, 2000)}"
            
            # URL encode the query
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            
            result = await self._request("GET", f"/query/?q={encoded_query}")
            return result.get("records", [])
        except Exception as e:
            logger.error(f"Error querying cases: {e}")
            raise
    
    async def _get_or_create_contact(self, email: str, create_if_not_exists: bool = True) -> Optional[str]:
        """Get or create a contact by email, return contact ID"""
        if email in self._contact_cache:
            return self._contact_cache[email]
        
        try:
            # Query for existing contact
            import urllib.parse
            query = f"SELECT Id, Email FROM Contact WHERE Email = '{email}' LIMIT 1"
            encoded_query = urllib.parse.quote(query)
            
            result = await self._request("GET", f"/query/?q={encoded_query}")
            
            if result.get("records"):
                contact_id = result["records"][0]["Id"]
                self._contact_cache[email] = contact_id
                return contact_id
            
            # Create new contact if not found and allowed
            if create_if_not_exists:
                name = email.split("@")[0].replace(".", " ").title()
                contact_data = {
                    "LastName": name,
                    "Email": email
                }
                
                result = await self._request("POST", "/sobjects/Contact/", json=contact_data)
                contact_id = result["id"]
                self._contact_cache[email] = contact_id
                return contact_id
            
            return None
        except Exception as e:
            logger.error(f"Error getting/creating contact for {email}: {e}")
            return None
    
    async def close(self):
        """Clean up resources"""
        if self.client:
            await self.client.aclose()
