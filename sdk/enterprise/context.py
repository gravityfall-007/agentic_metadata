"""
Context management module for Enterprise SDK.

This module handles persistent memory / conversation history for agents.
"""

import json
import os
from typing import List, Dict, Optional
from threading import Lock

class ContextManager:
    """
    Manages conversation history (memory).
    
    Supports simple local file persistence for demonstration.
    """
    
    def __init__(self, agent_id: str, storage_path: str = ".context_store"):
        self.agent_id = agent_id
        self.storage_path = storage_path
        self._lock = Lock()
        
        # Ensure storage directory exists
        if not os.path.exists(self.storage_path):
            os.makedirs(self.storage_path, exist_ok=True)
            
        self.file_path = os.path.join(self.storage_path, f"{self.agent_id}.json")
        self._load_context()

    def _load_context(self):
        """Load context from disk."""
        if os.path.exists(self.file_path):
            with open(self.file_path, 'r') as f:
                try:
                    self.history = json.load(f)
                except json.JSONDecodeError:
                    self.history = []
        else:
            self.history = []

    def _save_context(self):
        """Save context to disk."""
        with self._lock:
            with open(self.file_path, 'w') as f:
                json.dump(self.history, f, indent=2)

    def add_message(self, role: str, content: str, meta: Optional[Dict] = None):
        """
        Add a message to the history.
        
        Args:
            role (str): 'user', 'assistant', or 'system'.
            content (str): The message content.
            meta (dict, optional): Additional metadata.
        """
        message = {
            "role": role,
            "content": content,
            "timestamp": None  # In real app, add time.time()
        }
        if meta:
            message["meta"] = meta
            
        self.history.append(message)
        self._save_context()

    def get_context(self, limit: int = 10) -> List[Dict]:
        """
        Get the most recent messages.
        
        Args:
            limit (int): Number of recent messages to retrieve.
        """
        return self.history[-limit:]

    def clear(self):
        """Clear history."""
        self.history = []
        self._save_context()
