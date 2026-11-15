"""
VentureOS: Formal LangGraph StateGraph Architecture
Production-grade, cyclic, stateful multi-agent orchestration with conditional branching and checkpointing.
"""

from typing import Dict, Any, List, Optional, TypedDict
from langgraph.graph import StateGraph, END
from venture_os.state import VentureState, ProspectAsset
from venture_os.agents.pain_hunter import PainHunterAgent
from venture_os.agents.feasibility_arbiter import FeasibilityArbiterAgent
from venture_os.agents.product_synthesizer import ProductSynthesizerAgent
from venture_os.agents.sandbox_verifier import SandboxVerifierAgent
from venture_os.agents.trojan_auditor import TrojanAuditorAgent
from venture_os.agents.outbound_sdr import OutboundSDRAgent
from venture_os.agents.governor import GovernorAgent
from venture_os.memory.agent_memory import AgentMemoryManager
import uuid


class VentureGraphState(TypedDict):
    """The state container passed between LangGraph nodes."""
    state_obj: VentureState
    sample_prospects: List[ProspectAsset]
    simulated_replies: int
    retry_count: int
    memory_notes: List[str]


class LangGraphVentureEngine:
    """Orchestrates VentureOS using LangGraph's stateful cyclic computation graph."""

    def __init__(self):
        self.pain_hunter = PainHunterAgent()
        self.feasibility_arbiter = FeasibilityArbiterAgent()
        self.product_synthesizer = ProductSynthesizerAgent()
        self.sandbox_verifier = SandboxVerifierAgent()
        self.trojan_auditor = TrojanAuditorAgent()
        self.outbound_sdr = OutboundSDRAgent()
        self.governor = GovernorAgent()
        self.memory = AgentMemoryManager()
        self.app = self._build_graph()

    def _build_graph(self):
        workflow = StateGraph(VentureGraphState)

        # 1. Define Nodes
        workflow.add_node("mine_pain", self._node_mine_pain)
        workflow.add_node("check_feasibility", self._node_check_feasibility)
        workflow.add_node("synthesize_product", self._node_synthesize_product)
        workflow.add_node("verify_sandbox", self._node_verify_sandbox)
        workflow.add_node("trojan_audit", self._node_trojan_audit)
        workflow.add_node("generate_outbound", self._node_generate_outbound)
        workflow.add_node("evaluate_governor", self._node_evaluate_governor)

        # 2. Define Normal Transitions
        workflow.set_entry_point("mine_pain")
        workflow.add_edge("mine_pain", "check_feasibility")

        # 3. Conditional Edge: Feasibility Gate
        workflow.add_conditional_edges(
            "check_feasibility",
            self._route_feasibility,
            {
                "pass": "synthesize_product",
                "fail": END
            }
        )

        workflow.add_edge("synthesize_product", "verify_sandbox")

        # 4. Conditional Edge: Sandbox Self-Healing Retry
        workflow.add_conditional_edges(
            "verify_sandbox",
            self._route_sandbox,
            {
                "pass": "trojan_audit",
                "retry": "synthesize_product"
            }
        )

        workflow.add_edge("trojan_audit", "generate_outbound")
        workflow.add_edge("generate_outbound", "evaluate_governor")
        workflow.add_edge("evaluate_governor", END)

        return workflow.compile()

    # Node Implementations
    def _node_mine_pain(self, state: VentureGraphState) -> VentureGraphState:
        vstate = self.pain_hunter.execute(state["state_obj"])
        state["state_obj"] = vstate
        self.memory.store_memory("PainHunter", "signal", vstate.pain_signal.raw_quote, {"niche": vstate.niche})
        return state

    def _node_check_feasibility(self, state: VentureGraphState) -> VentureGraphState:
        vstate = self.feasibility_arbiter.execute(state["state_obj"])
        state["state_obj"] = vstate
        return state

    def _node_synthesize_product(self, state: VentureGraphState) -> VentureGraphState:
        vstate = self.product_synthesizer.execute(state["state_obj"])
        state["state_obj"] = vstate
        return state

    def _node_verify_sandbox(self, state: VentureGraphState) -> VentureGraphState:
        vstate = self.sandbox_verifier.execute(state["state_obj"])
        state["state_obj"] = vstate
        return state

    def _node_trojan_audit(self, state: VentureGraphState) -> VentureGraphState:
        vstate = self.trojan_auditor.execute(state["state_obj"], state["sample_prospects"])
        state["state_obj"] = vstate
        return state

    def _node_generate_outbound(self, state: VentureGraphState) -> VentureGraphState:
        vstate = self.outbound_sdr.execute(state["state_obj"], state["sample_prospects"])
        state["state_obj"] = vstate
        return state

    def _node_evaluate_governor(self, state: VentureGraphState) -> VentureGraphState:
        vstate = self.governor.evaluate(state["state_obj"], simulated_replies=state["simulated_replies"])
        state["state_obj"] = vstate
        self.memory.store_memory("Governor", "telemetry", f"Conversion: {vstate.telemetry.conversion_rate:.2%}", {"status": vstate.telemetry.status})
        return state

    # Conditional Routers
    def _route_feasibility(self, state: VentureGraphState) -> str:
        if state["state_obj"].feasibility and state["state_obj"].feasibility.passed:
            return "pass"
        return "fail"

    def _route_sandbox(self, state: VentureGraphState) -> str:
        if state["state_obj"].product_spec and state["state_obj"].product_spec.verification_status == "passed":
            return "pass"
        if state["retry_count"] < 2:
            state["retry_count"] += 1
            return "retry"
        return "pass"

    def run(self, niche: str, sample_prospects: List[ProspectAsset], simulated_replies: int = 1) -> VentureState:
        vstate = VentureState(venture_id=f"lg_{uuid.uuid4().hex[:6]}", niche=niche)
        initial_state: VentureGraphState = {
            "state_obj": vstate,
            "sample_prospects": sample_prospects,
            "simulated_replies": simulated_replies,
            "retry_count": 0,
            "memory_notes": []
        }
        final_state = self.app.invoke(initial_state)
        return final_state["state_obj"]
