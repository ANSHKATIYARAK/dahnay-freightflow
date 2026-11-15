"""
VentureOS: Persistent Long-Term Agent Memory Layer (Powered by mem0)
Stores and recalls durable cross-session facts: winning niches, objection patterns, and selector repairs.
"""

import os
import json
import sqlite3
from typing import List, Dict, Any, Optional
from datetime import datetime


class AgentMemoryManager:
    """Intelligent memory layer for autonomous agents with mem0 integration and SQLite persistence."""

    def __init__(self, db_path: str = "build/agent_memory.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()
        self.mem0_client = None
        self._init_mem0()

    def _init_mem0(self):
        """Attempts to initialize mem0 if installed and allowed by OS security policies."""
        try:
            from mem0 import Memory
            self.mem0_client = Memory()
        except (Exception, BaseException):
            # Graceful local fallback to embedded SQLite semantic store
            self.mem0_client = None

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS agent_memories (
                memory_id INTEGER PRIMARY KEY AUTOINCREMENT,
                agent_name TEXT,
                category TEXT,
                memory_text TEXT,
                metadata_json TEXT,
                created_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def store_memory(self, agent_name: str, category: str, text: str, metadata: Dict[str, Any] = None) -> int:
        """Stores a durable learning or insight for an agent."""
        # Store in mem0 if active
        if self.mem0_client:
            try:
                self.mem0_client.add(text, user_id=agent_name, metadata=metadata or {})
            except Exception:
                pass

        # Always persist in local SQLite
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO agent_memories (agent_name, category, memory_text, metadata_json, created_at) VALUES (?, ?, ?, ?, ?)",
            (agent_name, category, text, json.dumps(metadata or {}), datetime.utcnow().isoformat())
        )
        mem_id = c.lastrowid
        conn.commit()
        conn.close()
        return mem_id

    def recall_memories(self, agent_name: Optional[str] = None, category: Optional[str] = None, limit: int = 5) -> List[Dict[str, Any]]:
        """Recalls relevant past learnings to prevent repeated mistakes."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        query = "SELECT memory_id, agent_name, category, memory_text, metadata_json, created_at FROM agent_memories"
        params = []
        conditions = []
        
        if agent_name:
            conditions.append("agent_name = ?")
            params.append(agent_name)
        if category:
            conditions.append("category = ?")
            params.append(category)
            
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
            
        query += " ORDER BY memory_id DESC LIMIT ?"
        params.append(limit)
        
        c.execute(query, params)
        rows = c.fetchall()
        conn.close()
        
        return [
            {
                "memory_id": r[0],
                "agent_name": r[1],
                "category": r[2],
                "memory_text": r[3],
                "metadata": json.loads(r[4]),
                "created_at": r[5]
            }
            for r in rows
        ]
