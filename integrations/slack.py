"""Slack Integration"""

import logging
import os
import asyncio
from typing import Dict, Any, Optional, List
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

# Try to import slack_sdk, but handle gracefully if not installed
try:
    from slack_sdk import WebClient
    from slack_sdk.errors import SlackApiError
    SLACK_SDK_AVAILABLE = True
except ImportError:
    SLACK_SDK_AVAILABLE = False
    logger.warning("slack-sdk not installed. Install with: pip install slack-sdk")


class SlackIntegration:
    """Integration with Slack"""
    
    def __init__(self, token: Optional[str] = None):
        """
        Initialize Slack integration
        
        Args:
            token: Slack bot token (or from SLACK_TOKEN env var)
        """
        self.token = token or os.getenv("SLACK_TOKEN")
        self.client: Optional[Any] = None
        self.executor = ThreadPoolExecutor(max_workers=5)
        self._channel_cache: Dict[str, str] = {}  # Cache channel name -> channel ID
        
        self._initialize_client()
    
    def _initialize_client(self):
        """Initialize the Slack WebClient"""
        if not SLACK_SDK_AVAILABLE:
            logger.warning("slack-sdk not available. Slack operations will fail.")
            return
        
        if not self.token:
            logger.warning("SLACK_TOKEN not set. Slack operations will fail.")
            return
        
        try:
            # Initialize client with SSL verification
            self.client = WebClient(token=self.token)
            # Test connection
            response = self.client.auth_test()
            logger.info(f"Slack client initialized successfully. Connected as: {response.get('user')}")
        except Exception as e:
            error_str = str(e)
            if "SSL" in error_str or "CERTIFICATE" in error_str or "certificate verify failed" in error_str:
                logger.error(
                    f"SSL certificate verification failed: {e}\n\n"
                    f"To fix this issue, try one of the following:\n\n"
                    f"1. INSTALL CERTIFICATES (Recommended):\n"
                    f"   macOS: Run: /Applications/Python\\ 3.x/Install\\ Certificates.command\n"
                    f"   Or: python -m pip install --upgrade certifi\n\n"
                    f"2. SET SSL CERTIFICATE FILE:\n"
                    f"   export SSL_CERT_FILE=$(python -m certifi)\n\n"
                    f"3. INSTALL CERTIFI PACKAGE:\n"
                    f"   pip install --upgrade certifi\n\n"
                    f"4. TEMPORARY WORKAROUND (Less Secure):\n"
                    f"   Set environment variable: export PYTHONHTTPSVERIFY=0\n"
                    f"   (Not recommended for production)\n\n"
                    f"After fixing, restart your application."
                )
            else:
                logger.error(f"Failed to initialize Slack client: {e}")
            self.client = None
    
    async def _run_sync(self, func, *args, **kwargs):
        """Run a synchronous function in a thread pool"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(self.executor, func, *args, **kwargs)
    
    async def _get_channel_id(self, channel: str) -> Optional[str]:
        """Get channel ID from channel name or ID"""
        if channel.startswith("C") and len(channel) == 9:
            # Already a channel ID
            return channel
        
        if channel in self._channel_cache:
            return self._channel_cache[channel]
        
        if not self.client:
            return None
        
        def get_channel_id_sync():
            try:
                # Try to find channel by name
                response = self.client.conversations_list(types="public_channel,private_channel")
                
                for ch in response["channels"]:
                    if ch["name"] == channel or ch["id"] == channel:
                        channel_id = ch["id"]
                        self._channel_cache[channel] = channel_id
                        return channel_id
                
                # If not found, try to create it (may fail due to permissions)
                try:
                    response = self.client.conversations_create(name=channel)
                    channel_id = response["channel"]["id"]
                    self._channel_cache[channel] = channel_id
                    return channel_id
                except SlackApiError as e:
                    if e.response["error"] != "name_taken":
                        logger.warning(f"Could not create channel {channel}: {e}")
                
                return None
            except Exception as e:
                logger.error(f"Error getting channel ID for {channel}: {e}")
                return None
        
        return await self._run_sync(get_channel_id_sync)
    
    async def execute_tool(self, tool_name: str, parameters: Dict[str, Any]) -> Any:
        """Execute a Slack tool"""
        if parameters is None:
            parameters = {}
        
        if tool_name == "search_messages":
            query = parameters.get("query")
            if not query:
                received_params = list(parameters.keys()) if parameters else []
                error_msg = (
                    f"search_messages requires 'query' parameter. "
                    f"Received parameters: {received_params}. "
                    f"Please provide 'query' as a string."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            return await self.search_messages(
                query,
                parameters.get("channel")
            )
        elif tool_name == "get_channel_history":
            channel = parameters.get("channel")
            if not channel:
                received_params = list(parameters.keys()) if parameters else []
                error_msg = (
                    f"get_channel_history requires 'channel' parameter. "
                    f"Received parameters: {received_params}. "
                    f"Please provide 'channel' as a string."
                )
                logger.error(error_msg)
                raise ValueError(error_msg)
            return await self.get_channel_history(
                channel,
                parameters.get("limit", 100)
            )
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    async def search_messages(self, query: str, channel: Optional[str] = None) -> List[Dict[str, Any]]:
        """Search Slack messages"""
        if not self.client:
            raise ValueError("Slack client not initialized. Check your SLACK_TOKEN.")
        
        # Get channel ID if channel name provided (do this before sync execution)
        channel_id = None
        if channel:
            channel_id = await self._get_channel_id(channel)
        
        def search_messages_sync():
            try:
                # Build search query
                search_query = query
                if channel_id:
                    search_query = f"in:{channel_id} {query}"
                
                response = self.client.search_messages(query=search_query)
                
                matches = []
                if "messages" in response and "matches" in response["messages"]:
                    for match in response["messages"]["matches"]:
                        matches.append({
                            "text": match.get("text", ""),
                            "user": match.get("username", ""),
                            "channel": match.get("channel", {}).get("name", ""),
                            "timestamp": match.get("ts", ""),
                            "permalink": match.get("permalink", "")
                        })
                print(f"matches: {matches}")
                return matches
            except SlackApiError as e:
                error_code = ""
                error_response = {}
                if hasattr(e, "response"):
                    error_response = e.response if isinstance(e.response, dict) else {}
                    error_code = error_response.get("error", "")
                
                # if error_code == "not_allowed_token_type":
                #     error_msg = (
                #         f"Slack API error: Token type not allowed for search.messages.\n\n"
                #         f"This error means your Slack token doesn't have the required permissions "
                #         f"or is the wrong token type for the search.messages API.\n\n"
                #         f"TO FIX THIS ISSUE:\n\n"
                #         f"1. CHECK YOUR TOKEN TYPE:\n"
                #         f"   - Bot tokens (xoxb-*) are recommended and should work\n"
                #         f"   - User tokens (xoxp-*) may have restrictions\n"
                #         f"   - Legacy tokens (xoxa-*, xoxo-*) are NOT supported\n"
                #         f"   - Your token should start with 'xoxb-' for bot tokens\n\n"
                #         f"2. ADD REQUIRED SCOPE:\n"
                #         f"   The search.messages API requires the 'search:read' scope.\n\n"
                #         f"3. UPDATE YOUR SLACK APP PERMISSIONS:\n"
                #         f"   a. Go to: https://api.slack.com/apps\n"
                #         f"   b. Select your app (or create a new one)\n"
                #         f"   c. Navigate to: 'OAuth & Permissions' in the sidebar\n"
                #         f"   d. Scroll to 'Bot Token Scopes'\n"
                #         f"   e. Click 'Add an OAuth Scope'\n"
                #         f"   f. Add: 'search:read'\n"
                #         f"   g. Click 'Save Changes'\n"
                #         f"   h. Scroll to top and click 'Reinstall to Workspace'\n"
                #         f"   i. Authorize the new permissions\n"
                #         f"   j. Copy the new 'Bot User OAuth Token' (starts with xoxb-)\n"
                #         f"   k. Update your SLACK_TOKEN environment variable\n\n"
                #         f"4. ALTERNATIVE WORKAROUND:\n"
                #         f"   If you can't add the search:read scope, you can:\n"
                #         f"   - Use 'get_channel_history' tool instead to read specific channels\n"
                #         f"   - This doesn't require search:read scope, only 'channels:history'\n\n"
                #         f"5. VERIFY YOUR TOKEN:\n"
                #         f"   - Make sure you're using a Bot Token (xoxb-*)\n"
                #         f"   - Not a User Token or Legacy Token\n"
                #         f"   - Token should be from the 'Bot User OAuth Token' section\n\n"
                #         f"Full error details: {e}\n"
                #         f"Error response: {error_response}"
                #     )
                #     logger.error(error_msg)
                    raise ValueError(error_code) from e
                elif error_code == "missing_scope":
                    error_msg = (
                        f"Slack API error: Missing required scope.\n\n"
                        f"The search.messages API requires the 'search:read' scope.\n"
                        f"Please add this scope to your Slack app (see instructions above)."
                    )
                    logger.error(error_msg)
                    raise ValueError(error_msg) from e
                else:
                    logger.error(f"Slack API error searching messages: {e}")
                    if error_response:
                        logger.error(f"Error response: {error_response}")
                    raise
            except Exception as e:
                logger.error(f"Error searching Slack messages: {e}")
                raise
        
        try:
            return await self._run_sync(search_messages_sync)
        except Exception as e:
            logger.error(f"Error searching Slack messages: {e}")
            raise
    
    async def get_channel_history(
        self,
        channel: str,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get channel message history"""
        if not self.client:
            raise ValueError("Slack client not initialized. Check your SLACK_TOKEN.")
        
        channel_id = await self._get_channel_id(channel)
        if not channel_id:
            raise ValueError(f"Channel '{channel}' not found or accessible")
        
        def get_history_sync():
            try:
                response = self.client.conversations_history(
                    channel=channel_id,
                    limit=min(limit, 1000)  # Slack API limit
                )
                
                messages = []
                for message in response.get("messages", []):
                    # Skip bot messages if desired, or include them
                    messages.append({
                        "text": message.get("text", ""),
                        "user": message.get("user", ""),
                        "timestamp": message.get("ts", ""),
                        "type": message.get("type", "message"),
                        "subtype": message.get("subtype")
                    })
                
                return messages
            except SlackApiError as e:
                logger.error(f"Slack API error getting channel history: {e}")
                raise
            except Exception as e:
                logger.error(f"Error getting channel history: {e}")
                raise
        
        try:
            return await self._run_sync(get_history_sync)
        except Exception as e:
            logger.error(f"Error getting channel history: {e}")
            raise
    
    async def send_message(
        self,
        channel: str,
        text: str,
        thread_ts: Optional[str] = None
    ) -> Dict[str, Any]:
        """Send a message to a Slack channel"""
        if not self.client:
            raise ValueError("Slack client not initialized. Check your SLACK_TOKEN.")
        
        channel_id = await self._get_channel_id(channel)
        if not channel_id:
            raise ValueError(f"Channel '{channel}' not found or accessible")
        
        def send_message_sync():
            try:
                response = self.client.chat_postMessage(
                    channel=channel_id,
                    text=text,
                    thread_ts=thread_ts
                )
                return {
                    "ok": response.get("ok", False),
                    "ts": response.get("ts", ""),
                    "message": dict(response.get("message", {}))
                }
            except SlackApiError as e:
                logger.error(f"Slack API error sending message: {e}")
                raise
            except Exception as e:
                logger.error(f"Error sending message: {e}")
                raise
        
        try:
            return await self._run_sync(send_message_sync)
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise
    
    async def close(self):
        """Clean up resources"""
        if self.executor:
            self.executor.shutdown(wait=True)

