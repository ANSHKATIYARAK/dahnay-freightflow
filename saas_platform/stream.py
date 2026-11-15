"""
SaaS Platform: Server-Sent Events (SSE) Streaming & Async Job Queue
Streams live step-by-step agent thoughts, code generation, and audits to the frontend.
"""

import asyncio
import json
import uuid
import time
from typing import AsyncGenerator, Dict, Any, List
from saas_platform.models import AgentJob, DatabaseManager
from studio_engine.registry import AgentRegistry
from studio_engine.dispatcher import AgentDispatcher, TaskRequest


class JobQueueManager:
    """Manages asynchronous agent execution and event dispatching for SSE streaming."""

    def __init__(self, db: DatabaseManager, registry: AgentRegistry, dispatcher: AgentDispatcher):
        self.db = db
        self.registry = registry
        self.dispatcher = dispatcher
        self.active_jobs: Dict[str, AgentJob] = {}
        self.event_queues: Dict[str, asyncio.Queue] = {}

    def submit_job(self, workspace_id: str, agent_name: str, prompt: str, domain: str = "General") -> AgentJob:
        job = AgentJob(
            workspace_id=workspace_id,
            agent_name=agent_name,
            prompt=prompt,
            domain=domain,
            status="queued"
        )
        self.active_jobs[job.job_id] = job
        self.event_queues[job.job_id] = asyncio.Queue()
        return job

    async def execute_job(self, job_id: str):
        job = self.active_jobs.get(job_id)
        if not job:
            return

        q = self.event_queues[job_id]
        job.status = "processing"

        await q.put({"event": "status", "data": {"step": f"Dispatched task to {job.agent_name}", "progress": 10}})
        await asyncio.sleep(0.1)

        await q.put({"event": "status", "data": {"step": f"Analyzing domain constraints for {job.domain}...", "progress": 35}})
        await asyncio.sleep(0.1)

        # Run actual agent dispatch
        req = TaskRequest(agent_name=job.agent_name, prompt=job.prompt, domain=job.domain)
        result = self.dispatcher.dispatch(req)

        await q.put({"event": "status", "data": {"step": "Synthesizing production deliverable...", "progress": 70}})
        await asyncio.sleep(0.1)

        # Push artifact preview if available
        if result.structured_artifacts:
            await q.put({"event": "artifact", "data": result.structured_artifacts})

        job.status = "completed"
        job.result_payload = {
            "output_text": result.output_text,
            "artifacts": result.structured_artifacts,
            "execution_time_ms": result.execution_time_ms
        }
        job.completed_at = time.strftime("%Y-%m-%dT%H:%M:%SZ")

        # Deduct credit upon successful job completion
        self.db.deduct_credits(job.workspace_id, 1)

        await q.put({"event": "complete", "data": job.result_payload})

    async def stream_job_events(self, job_id: str) -> AsyncGenerator[str, None]:
        """Async generator yielding SSE formatted text."""
        q = self.event_queues.get(job_id)
        if not q:
            yield f"event: error\ndata: {json.dumps({'error': 'Job not found'})}\n\n"
            return

        # Start execution in background if still queued
        job = self.active_jobs.get(job_id)
        if job and job.status == "queued":
            asyncio.create_task(self.execute_job(job_id))

        while True:
            item = await q.get()
            event_name = item.get("event", "message")
            data_str = json.dumps(item.get("data", {}))
            yield f"event: {event_name}\ndata: {data_str}\n\n"
            if event_name in ["complete", "error"]:
                break
