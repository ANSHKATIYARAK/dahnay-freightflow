"""
SaaS Platform: Multi-Tenant Data Models & Schema
Manages Workspaces, Users, API Keys, Stripe Subscriptions, and Usage Metering.
"""

from typing import Optional, List, Dict, Any, Literal
from pydantic import BaseModel, Field
from datetime import datetime
import uuid
import sqlite3
import json
import os


class Workspace(BaseModel):
    workspace_id: str = Field(default_factory=lambda: f"ws_{uuid.uuid4().hex[:8]}")
    name: str
    owner_email: str
    plan_tier: Literal["free", "starter", "pro", "enterprise"] = "starter"
    credits_balance: int = 100  # Default 100 credits on signup
    stripe_customer_id: Optional[str] = None
    stripe_subscription_id: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class User(BaseModel):
    user_id: str = Field(default_factory=lambda: f"usr_{uuid.uuid4().hex[:8]}")
    workspace_id: str
    email: str
    full_name: str
    role: Literal["owner", "admin", "member"] = "member"


class ApiKey(BaseModel):
    key_id: str = Field(default_factory=lambda: f"key_{uuid.uuid4().hex[:8]}")
    workspace_id: str
    api_key_secret: str = Field(default_factory=lambda: f"sk_live_{uuid.uuid4().hex}")
    name: str
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class UsageRecord(BaseModel):
    record_id: str = Field(default_factory=lambda: f"usg_{uuid.uuid4().hex[:8]}")
    workspace_id: str
    agent_name: str
    task_description: str
    credits_deducted: int = 1
    execution_time_ms: float
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


class AgentJob(BaseModel):
    job_id: str = Field(default_factory=lambda: f"job_{uuid.uuid4().hex[:8]}")
    workspace_id: str
    agent_name: str
    prompt: str
    domain: str
    status: Literal["queued", "processing", "completed", "failed"] = "queued"
    steps: List[str] = Field(default_factory=list)
    result_payload: Optional[Dict[str, Any]] = None
    error_message: Optional[str] = None
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    completed_at: Optional[str] = None


class DatabaseManager:
    """Embedded SQLite persistence for multi-tenant SaaS operations."""

    def __init__(self, db_path: str = "build/saas_platform.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("""
            CREATE TABLE IF NOT EXISTS workspaces (
                workspace_id TEXT PRIMARY KEY,
                name TEXT,
                owner_email TEXT,
                plan_tier TEXT,
                credits_balance INTEGER,
                stripe_customer_id TEXT,
                stripe_subscription_id TEXT,
                created_at TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS usage_records (
                record_id TEXT PRIMARY KEY,
                workspace_id TEXT,
                agent_name TEXT,
                task_description TEXT,
                credits_deducted INTEGER,
                execution_time_ms REAL,
                timestamp TEXT
            )
        """)
        c.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                job_id TEXT PRIMARY KEY,
                workspace_id TEXT,
                agent_name TEXT,
                prompt TEXT,
                domain TEXT,
                status TEXT,
                steps_json TEXT,
                result_json TEXT,
                created_at TEXT,
                completed_at TEXT
            )
        """)
        conn.commit()
        conn.close()

    def create_workspace(self, name: str, owner_email: str) -> Workspace:
        ws = Workspace(name=name, owner_email=owner_email)
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(
            "INSERT INTO workspaces VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (ws.workspace_id, ws.name, ws.owner_email, ws.plan_tier, ws.credits_balance, ws.stripe_customer_id, ws.stripe_subscription_id, ws.created_at)
        )
        conn.commit()
        conn.close()
        return ws

    def get_workspace(self, workspace_id: str) -> Optional[Workspace]:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("SELECT * FROM workspaces WHERE workspace_id = ?", (workspace_id,))
        row = c.fetchone()
        conn.close()
        if not row:
            return None
        return Workspace(
            workspace_id=row[0],
            name=row[1],
            owner_email=row[2],
            plan_tier=row[3],
            credits_balance=row[4],
            stripe_customer_id=row[5],
            stripe_subscription_id=row[6],
            created_at=row[7]
        )

    def deduct_credits(self, workspace_id: str, credits: int = 1) -> bool:
        ws = self.get_workspace(workspace_id)
        if not ws or ws.credits_balance < credits:
            return False
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE workspaces SET credits_balance = credits_balance - ? WHERE workspace_id = ?", (credits, workspace_id))
        conn.commit()
        conn.close()
        return True

    def add_credits(self, workspace_id: str, credits: int) -> None:
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute("UPDATE workspaces SET credits_balance = credits_balance + ? WHERE workspace_id = ?", (credits, workspace_id))
        conn.commit()
        conn.close()
