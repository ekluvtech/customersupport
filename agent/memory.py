"""Memory and Context Persistence Manager"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from collections import defaultdict

logger = logging.getLogger(__name__)


class InMemoryStorage:
    """In-memory storage for conversation history"""
    
    def __init__(self, max_history: int = 50):
        # Structure: {conversation_key: [messages]}
        # Each message: {"role": str, "content": str, "timestamp": str, "metadata": dict}
        self.conversations: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.max_history = max_history
    
    def _get_conversation_key(self, user_id: Optional[str], channel: Optional[str]) -> str:
        """Generate a unique key for a conversation"""
        if user_id and channel:
            return f"{user_id}:{channel}"
        elif user_id:
            return f"user:{user_id}"
        elif channel:
            return f"channel:{channel}"
        else:
            return "default"
    
    def add_message(
        self,
        user_id: Optional[str],
        channel: Optional[str],
        role: str,
        content: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Add a message to the conversation history"""
        key = self._get_conversation_key(user_id, channel)
        timestamp = datetime.now().isoformat()
        
        message = {
            "role": role,
            "content": content,
            "timestamp": timestamp,
            "metadata": metadata or {},
            "user_id": user_id,
            "channel": channel
        }
        
        self.conversations[key].append(message)
        
        # Trim if exceeds max history
        if len(self.conversations[key]) > self.max_history * 2:
            self.conversations[key] = self.conversations[key][-self.max_history * 2:]
    
    def get_messages(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        limit: Optional[int] = None,
        role: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Retrieve messages from conversation history"""
        key = self._get_conversation_key(user_id, channel)
        messages = self.conversations.get(key, [])
        
        # Filter by role if specified
        if role:
            messages = [msg for msg in messages if msg["role"] == role]
        
        # Apply limit
        if limit:
            messages = messages[-limit:]
        
        return messages
    
    def get_context_messages(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """Get messages in format suitable for LLM context"""
        messages = self.get_messages(user_id, channel, limit)
        return [
            {"role": msg["role"], "content": msg["content"]}
            for msg in messages
        ]
    
    def clear_conversation(self, user_id: Optional[str] = None, channel: Optional[str] = None):
        """Clear conversation history for a specific user/channel"""
        key = self._get_conversation_key(user_id, channel)
        if key in self.conversations:
            del self.conversations[key]
    
    def clear_all(self):
        """Clear all conversation history"""
        self.conversations.clear()
    
    def get_conversation_count(self) -> int:
        """Get total number of conversations"""
        return len(self.conversations)
    
    def get_total_messages(self) -> int:
        """Get total number of messages across all conversations"""
        return sum(len(messages) for messages in self.conversations.values())


class MemoryManager:
    """Manages conversation context and memory persistence"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.backend = config.get("memory_backend", "chromadb")
        self.max_history = config.get("max_history", 50)
        self.persist_across_sessions = config.get("persist_across_sessions", True)
        self.storage: Optional[Any] = None
        self.in_memory_storage: Optional[InMemoryStorage] = None
    
    async def initialize(self):
        """Initialize the memory backend"""
        if self.backend == "chromadb":
            try:
                import chromadb
                self.client = chromadb.Client()
                self.collection = self.client.get_or_create_collection("conversations")
                logger.info("Initialized ChromaDB memory backend")
            except ImportError:
                logger.warning("ChromaDB not available, using in-memory storage")
                self.in_memory_storage = InMemoryStorage(max_history=self.max_history)
                self.backend = "memory"
        elif self.backend == "memory" or self.backend == "in_memory":
            # Use in-memory storage
            self.in_memory_storage = InMemoryStorage(max_history=self.max_history)
            logger.info("Using in-memory storage")
        else:
            # Default to in-memory if backend not recognized
            logger.warning(f"Unknown backend '{self.backend}', using in-memory storage")
            self.in_memory_storage = InMemoryStorage(max_history=self.max_history)
            self.backend = "memory"
    
    async def get_context(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None,
        limit: Optional[int] = None
    ) -> List[Dict[str, str]]:
        """
        Retrieve conversation context
        
        Args:
            user_id: User identifier
            channel: Channel identifier
            limit: Maximum number of messages to retrieve
        
        Returns:
            List of messages in format [{"role": "user/assistant", "content": "..."}]
        """
        limit = limit or self.max_history
        
        try:
            if self.backend == "chromadb" and hasattr(self, "collection"):
                # Query ChromaDB
                where = {}
                if user_id:
                    where["user_id"] = user_id
                if channel:
                    where["channel"] = channel
                
                results = self.collection.query(
                    where=where if where else None,
                    n_results=limit,
                    include=["documents", "metadatas"]
                )
                
                # Convert to message format
                messages = []
                if results.get("documents"):
                    for doc, metadata in zip(results["documents"][0], results["metadatas"][0]):
                        # Parse stored document format
                        # This would need proper serialization/deserialization
                        messages.append({
                            "role": metadata.get("role", "user"),
                            "content": doc
                        })
                
                return messages[::-1]  # Reverse to get chronological order
            
            elif self.in_memory_storage:
                # Use in-memory storage
                return self.in_memory_storage.get_context_messages(
                    user_id=user_id,
                    channel=channel,
                    limit=limit
                )
            else:
                # Fallback to old storage format
                if not self.storage:
                    return []
                
                key = f"{user_id}:{channel}" if user_id or channel else "default"
                history = self.storage.get(key, [])
                return history[-limit:]
        
        except Exception as e:
            logger.error(f"Error retrieving context: {e}", exc_info=True)
            return []
    
    async def store_interaction(
        self,
        user_id: Optional[str],
        channel: Optional[str],
        message: str,
        response: str,
        metadata: Optional[Dict[str, Any]] = None
    ):
        """Store an interaction in memory"""
        try:
            if self.backend == "chromadb" and hasattr(self, "collection"):
                # Store in ChromaDB
                timestamp = datetime.now().isoformat()
                
                # Store user message
                self.collection.add(
                    documents=[message],
                    metadatas=[{
                        "role": "user",
                        "user_id": user_id or "unknown",
                        "channel": channel or "unknown",
                        "timestamp": timestamp,
                        **(metadata or {})
                    }],
                    ids=[f"{user_id}:{timestamp}:user" if user_id else f"{timestamp}:user"]
                )
                
                # Store assistant response
                self.collection.add(
                    documents=[response],
                    metadatas=[{
                        "role": "assistant",
                        "user_id": user_id or "unknown",
                        "channel": channel or "unknown",
                        "timestamp": timestamp,
                        **(metadata or {})
                    }],
                    ids=[f"{user_id}:{timestamp}:assistant" if user_id else f"{timestamp}:assistant"]
                )
            
            elif self.in_memory_storage:
                # Use in-memory storage
                self.in_memory_storage.add_message(
                    user_id=user_id,
                    channel=channel,
                    role="user",
                    content=message,
                    metadata=metadata
                )
                self.in_memory_storage.add_message(
                    user_id=user_id,
                    channel=channel,
                    role="assistant",
                    content=response,
                    metadata=metadata
                )
            
            else:
                # Fallback to old storage format
                if not self.storage:
                    self.storage = {}
                
                key = f"{user_id}:{channel}" if user_id or channel else "default"
                if key not in self.storage:
                    self.storage[key] = []
                
                self.storage[key].append({"role": "user", "content": message})
                self.storage[key].append({"role": "assistant", "content": response})
                
                # Trim if too long
                if len(self.storage[key]) > self.max_history * 2:
                    self.storage[key] = self.storage[key][-self.max_history * 2:]
        
        except Exception as e:
            logger.error(f"Error storing interaction: {e}", exc_info=True)
    
    async def clear_conversation(
        self,
        user_id: Optional[str] = None,
        channel: Optional[str] = None
    ):
        """Clear conversation history for a specific user/channel"""
        try:
            if self.in_memory_storage:
                self.in_memory_storage.clear_conversation(user_id=user_id, channel=channel)
                logger.info(f"Cleared conversation for user_id={user_id}, channel={channel}")
            elif self.storage:
                key = f"{user_id}:{channel}" if user_id or channel else "default"
                if key in self.storage:
                    del self.storage[key]
                    logger.info(f"Cleared conversation for key={key}")
        except Exception as e:
            logger.error(f"Error clearing conversation: {e}", exc_info=True)
    
    async def get_stats(self) -> Dict[str, Any]:
        """Get statistics about stored conversations"""
        try:
            if self.in_memory_storage:
                return {
                    "backend": "in_memory",
                    "conversation_count": self.in_memory_storage.get_conversation_count(),
                    "total_messages": self.in_memory_storage.get_total_messages(),
                    "max_history": self.max_history
                }
            elif self.backend == "chromadb" and hasattr(self, "collection"):
                count = self.collection.count()
                return {
                    "backend": "chromadb",
                    "message_count": count,
                    "max_history": self.max_history
                }
            elif self.storage:
                total_messages = sum(len(msgs) for msgs in self.storage.values())
                return {
                    "backend": "legacy_memory",
                    "conversation_count": len(self.storage),
                    "total_messages": total_messages,
                    "max_history": self.max_history
                }
            else:
                return {
                    "backend": "none",
                    "conversation_count": 0,
                    "total_messages": 0,
                    "max_history": self.max_history
                }
        except Exception as e:
            logger.error(f"Error getting stats: {e}", exc_info=True)
            return {"error": str(e)}
    
    async def close(self):
        """Close the memory backend"""
        try:
            if hasattr(self, "client"):
                # ChromaDB cleanup if needed
                pass
            if self.in_memory_storage and not self.persist_across_sessions:
                # Clear in-memory storage if not persisting
                self.in_memory_storage.clear_all()
                logger.info("Cleared in-memory storage (persist_across_sessions=False)")
            logger.info("Memory manager closed")
        except Exception as e:
            logger.error(f"Error closing memory manager: {e}", exc_info=True)

