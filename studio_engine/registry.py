"""
StudioEngine: Agent Registry & Specification Loader
Dynamically loads and validates all 32 specialized agents across all 7 departments.
"""

import os
import yaml
from typing import Dict, List, Optional
from pydantic import BaseModel, Field


class AgentSpec(BaseModel):
    name: str
    department: str
    role: str
    capabilities: List[str] = Field(default_factory=list)
    input_schema: Dict[str, str] = Field(default_factory=dict)
    output_schema: Dict[str, str] = Field(default_factory=dict)
    system_prompt: str = ""
    file_path: str = ""
    status: str = "idle"  # idle, working, completed, error


class AgentRegistry:
    """Central registry of all available autonomous agents in the studio."""

    def __init__(self, agents_dir: str = ".claude/agents"):
        self.agents_dir = agents_dir
        self.agents: Dict[str, AgentSpec] = {}
        self.departments: Dict[str, List[str]] = {}
        self.load_agents()

    def load_agents(self):
        """Scans the agents directory and loads all .md agent declarations."""
        self.agents.clear()
        self.departments.clear()

        if not os.path.exists(self.agents_dir):
            return

        for root, _, files in os.walk(self.agents_dir):
            for file in files:
                if file.endswith(".md"):
                    full_path = os.path.join(root, file)
                    spec = self._parse_agent_file(full_path)
                    if spec:
                        self.agents[spec.name] = spec
                        dept = spec.department
                        if dept not in self.departments:
                            self.departments[dept] = []
                        self.departments[dept].append(spec.name)

    def _parse_agent_file(self, file_path: str) -> Optional[AgentSpec]:
        """Parses frontmatter and body from a markdown file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            if not content.startswith("---"):
                return None

            parts = content.split("---", 2)
            if len(parts) < 3:
                return None

            frontmatter_raw = parts[1]
            body = parts[2].strip()

            meta = yaml.safe_load(frontmatter_raw)
            if not meta or "name" not in meta:
                return None

            return AgentSpec(
                name=meta.get("name"),
                department=meta.get("department", "general"),
                role=meta.get("role", "Specialist"),
                capabilities=meta.get("capabilities", []),
                input_schema=meta.get("input_schema", {}),
                output_schema=meta.get("output_schema", {}),
                system_prompt=body,
                file_path=file_path,
                status="idle"
            )
        except Exception as e:
            print(f"Error parsing agent at {file_path}: {e}")
            return None

    def get_agent(self, name: str) -> Optional[AgentSpec]:
        return self.agents.get(name)

    def list_by_department(self, dept: str) -> List[AgentSpec]:
        agent_names = self.departments.get(dept, [])
        return [self.agents[name] for name in agent_names if name in self.agents]

    def total_count(self) -> int:
        return len(self.agents)
