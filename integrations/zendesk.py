"""Zendesk Integration"""

import logging
from typing import Dict, Any, Optional
import httpx

logger = logging.getLogger(__name__)


class ZendeskIntegration:
    """Integration with Zendesk ticketing system"""
    
    def __init__(self, subdomain: Optional[str] = None, email: Optional[str] = None, api_key: Optional[str] = None):
        import os
        self.subdomain = subdomain or os.getenv("ZENDESK_SUBDOMAIN")
        self.email = email or os.getenv("ZENDESK_EMAIL")
        self.api_key = api_key or os.getenv("ZENDESK_API_KEY")
        
        # Validate credentials before creating client
        if not all([self.subdomain, self.email, self.api_key]):
            missing = []
            if not self.subdomain:
                missing.append("ZENDESK_SUBDOMAIN")
            if not self.email:
                missing.append("ZENDESK_EMAIL")
            if not self.api_key:
                missing.append("ZENDESK_API_KEY")
            
            logger.warning(
                f"Zendesk credentials not fully configured. Missing: {', '.join(missing)}. "
                "Set environment variables or pass as arguments."
            )
            self.base_url = None
            self.client = None
            return
        
        self.base_url = f"https://{self.subdomain}.zendesk.com/api/v2"
        
        # Zendesk API token authentication format: email/token:api_key
        # Note: The email should NOT include /token in the actual email value
        # httpx will handle the Basic Auth encoding
        auth_email = f"{self.email}/token"
        self.client = httpx.AsyncClient(
            auth=(auth_email, self.api_key),
            timeout=30.0,
            headers={
                "Content-Type": "application/json",
                "Accept": "application/json"
            }
        )
        logger.info(f"Zendesk integration initialized for {self.subdomain}.zendesk.com")
        logger.debug(f"Using email: {self.email} (API key length: {len(self.api_key) if self.api_key else 0})")
    
    async def verify_credentials(self) -> bool:
        """Verify Zendesk credentials by making a test API call"""
        if not self.client:
            return False
        
        try:
            # Make a simple API call to verify credentials
            response = await self.client.get(f"{self.base_url}/users/me.json")
            if response.status_code == 200:
                logger.info("Zendesk credentials verified successfully")
                return True
            elif response.status_code == 401:
                logger.error("Zendesk credentials verification failed: 401 Unauthorized")
                return False
            else:
                logger.warning(f"Zendesk credentials verification returned status {response.status_code}")
                return False
        except Exception as e:
            logger.error(f"Error verifying Zendesk credentials: {e}")
            return False
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a Zendesk tool"""
        if parameters is None:
            parameters = {}
        
        if tool_name == "get_ticket":
            ticket_id = parameters.get("ticket_id")
            if not ticket_id:
                received_params = list(parameters.keys()) if parameters else []
                error_msg = (
                    f"get_ticket requires 'ticket_id' parameter. "
                    f"Received parameters: {received_params}. "
                    f"Please provide 'ticket_id' as a string."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            return await self.get_ticket(ticket_id)
        elif tool_name == "update_ticket":
            ticket_id = parameters.get("ticket_id")
            if not ticket_id:
                received_params = list(parameters.keys()) if parameters else []
                error_msg = (
                    f"update_ticket requires 'ticket_id' parameter. "
                    f"Received parameters: {received_params}. "
                    f"Please provide 'ticket_id' as a string."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            return await self.update_ticket(
                ticket_id,
                parameters.get("comment"),
                parameters.get("status")
            )
        elif tool_name == "create_ticket":
            subject = parameters.get("subject")
            description = parameters.get("description")
            requester_email = parameters.get("requester_email")
            
            if not subject:
                raise ValueError("create_ticket requires 'subject' parameter")
            if not description:
                raise ValueError("create_ticket requires 'description' parameter")
            if not requester_email:
                raise ValueError("create_ticket requires 'requester_email' parameter")
            
            return await self.create_ticket(
                subject,
                description,
                requester_email,
                parameters.get("requester_name", requester_email.split("@")[0])
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def get_ticket(self, ticket_id: str) -> Dict[str, Any]:
        """Get ticket details"""
        if not self.client:
            raise ValueError("Zendesk client not initialized. Check your credentials.")
        
        try:
            response = await self.client.get(f"{self.base_url}/tickets/{ticket_id}.json")
            
            # Handle authentication errors with helpful messages
            if response.status_code == 401:
                error_msg = (
                    f"Zendesk authentication failed (401 Unauthorized).\n\n"
                    f"Current configuration:\n"
                    f"  - Email: {self.email}\n"
                    f"  - Subdomain: {self.subdomain}\n"
                    f"  - API Key: {'*' * min(len(self.api_key), 10) if self.api_key else 'NOT SET'}...\n\n"
                    f"To fix this issue, please verify:\n\n"
                    f"1. EMAIL VERIFICATION:\n"
                    f"   - The email must be the EXACT email address you use to log into Zendesk\n"
                    f"   - It should be: {self.email}\n"
                    f"   - Do NOT include '/token' in the email - the code adds this automatically\n\n"
                    f"2. API TOKEN SETUP:\n"
                    f"   - Go to: https://{self.subdomain}.zendesk.com/admin/apps-integrations/apis/zendesk-api\n"
                    f"   - Or: Admin → Apps and integrations → APIs → Zendesk API\n"
                    f"   - Make sure 'Token Access' is ENABLED\n"
                    f"   - Click 'Add API token' or use an existing one\n"
                    f"   - Copy the token immediately (you can only see it once)\n"
                    f"   - Set it as: export ZENDESK_API_KEY='your_token_here'\n\n"
                    f"3. API TOKEN PERMISSIONS:\n"
                    f"   - The API token must have at least 'Read' access to tickets\n"
                    f"   - Check your user role permissions in Zendesk Admin\n\n"
                    f"4. SUBDOMAIN VERIFICATION:\n"
                    f"   - Subdomain should be just the part before '.zendesk.com'\n"
                    f"   - Current: {self.subdomain}\n"
                    f"   - Should access: https://{self.subdomain}.zendesk.com\n\n"
                    f"5. TEST YOUR CREDENTIALS:\n"
                    f"   - Try logging into: https://{self.subdomain}.zendesk.com\n"
                    f"   - Verify the email '{self.email}' can log in\n"
                    f"   - Make sure the API token was generated for this account"
                )
                logger.error(error_msg)
                try:
                    error_response = response.json()
                    if "error" in error_response:
                        zendesk_error = error_response.get('error', 'Unknown error')
                        error_msg += f"\n\nZendesk API Error: {zendesk_error}"
                        if "Couldn't authenticate" in str(zendesk_error):
                            error_msg += (
                                f"\n\nThis usually means:\n"
                                f"  - The email doesn't match your Zendesk account\n"
                                f"  - The API token is incorrect or expired\n"
                                f"  - Token Access is not enabled in your Zendesk settings"
                            )
                except:
                    error_msg += f"\n\nRaw response: {response.text[:200]}"
                raise ValueError(error_msg)
            
            response.raise_for_status()
            return response.json()["ticket"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                # Re-raise with better message (handled above)
                raise
            logger.error(f"Error getting ticket {ticket_id}: HTTP {e.response.status_code}")
            raise
        except ValueError:
            # Re-raise authentication errors
            raise
        except Exception as e:
            logger.error(f"Error getting ticket {ticket_id}: {e}", exc_info=True)
            raise
    
    async def update_ticket(
        self,
        ticket_id: str,
        comment: Optional[str] = None,
        status: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a ticket"""
        if not self.client:
            raise ValueError("Zendesk client not initialized. Check your credentials.")
        
        try:
            data = {"ticket": {}}
            if comment:
                data["ticket"]["comment"] = {"body": comment, "public": False}
            if status:
                data["ticket"]["status"] = status
            
            response = await self.client.put(
                f"{self.base_url}/tickets/{ticket_id}.json",
                json=data
            )
            
            # Handle authentication errors
            if response.status_code == 401:
                error_msg = (
                    f"Zendesk authentication failed (401 Unauthorized) when updating ticket.\n\n"
                    f"Please verify your credentials (see get_ticket error for detailed instructions).\n"
                    f"Additionally, ensure the API token has 'Write' permissions for tickets."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            
            response.raise_for_status()
            return response.json()["ticket"]
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                raise
            logger.error(f"Error updating ticket {ticket_id}: HTTP {e.response.status_code}")
            raise
        except ValueError:
            raise
        except Exception as e:
            logger.error(f"Error updating ticket {ticket_id}: {e}", exc_info=True)
            raise
    
    async def create_ticket(
        self,
        subject: str,
        description: str,
        requester_email: str,
        requester_name: str,
    ) -> Dict[str, Any]:
        """Create a new ticket"""
        if not self.client:
            raise ValueError("Zendesk client not initialized. Check your credentials.")
        
        try:
            # Zendesk API requires comments to be an array, and requester can be just email
            data = {
                "ticket": {
                    "subject": subject,
                    "comment": {
                        "body": description,
                        "public": True  # Make comment public by default
                    },
                    "requester": {
                        "name": requester_name,
                        "email": requester_email
                    }
                }
            }
            
            response = await self.client.post(
                f"{self.base_url}/tickets.json",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            # Better error handling - show actual Zendesk error message
            if response.status_code != 201:
                error_detail = "Unknown error"
                error_messages = []
                try:
                    error_response = response.json()
                    
                    # Zendesk error structure can vary
                    if "error" in error_response:
                        if isinstance(error_response["error"], str):
                            error_messages.append(error_response["error"])
                        elif isinstance(error_response["error"], dict):
                            error_messages.append(str(error_response["error"]))
                    
                    if "description" in error_response:
                        error_messages.append(error_response["description"])
                    
                    if "details" in error_response:
                        if isinstance(error_response["details"], dict):
                            # Format field-specific errors
                            for field, messages in error_response["details"].items():
                                if isinstance(messages, list):
                                    error_messages.append(f"{field}: {', '.join(messages)}")
                                else:
                                    error_messages.append(f"{field}: {messages}")
                        else:
                            error_messages.append(str(error_response["details"]))
                    
                    if "base" in error_response:
                        if isinstance(error_response["base"], list):
                            error_messages.extend(error_response["base"])
                        else:
                            error_messages.append(str(error_response["base"]))
                    
                    error_detail = " | ".join(error_messages) if error_messages else str(error_response)
                    
                    logger.error(
                        f"Zendesk API error {response.status_code}: {error_detail}\n"
                        f"Request payload: {data}\n"
                        f"Full response: {error_response}"
                    )
                except Exception as parse_error:
                    error_detail = response.text
                    logger.error(
                        f"Zendesk API error {response.status_code}: {error_detail}\n"
                        f"Request payload: {data}\n"
                        f"Could not parse error response: {parse_error}"
                    )
                
                response.raise_for_status()
            
            return response.json()["ticket"]
        except httpx.HTTPStatusError as e:
            # Extract error details from response
            error_msg = f"HTTP {e.response.status_code}: {e.response.reason_phrase}"
            try:
                error_response = e.response.json()
                error_parts = []
                
                if "error" in error_response:
                    error_parts.append(f"Error: {error_response['error']}")
                if "description" in error_response:
                    error_parts.append(f"Description: {error_response['description']}")
                if "details" in error_response:
                    details = error_response["details"]
                    if isinstance(details, dict):
                        for field, messages in details.items():
                            if isinstance(messages, list):
                                error_parts.append(f"{field}: {', '.join(messages)}")
                            else:
                                error_parts.append(f"{field}: {messages}")
                    else:
                        error_parts.append(f"Details: {details}")
                
                if error_parts:
                    error_msg = f"{error_msg}\n" + "\n".join(error_parts)
                else:
                    error_msg = f"{error_msg}\nResponse: {error_response}"
            except:
                error_msg = f"{error_msg}\nResponse: {e.response.text}"
            
            logger.error(f"Error creating ticket: {error_msg}")
            raise ValueError(f"Failed to create Zendesk ticket: {error_msg}") from e
        except Exception as e:
            logger.error(f"Error creating ticket: {e}", exc_info=True)
            raise
    
    async def close(self):
        """Close the HTTP client"""
        if self.client:
            await self.client.aclose()

