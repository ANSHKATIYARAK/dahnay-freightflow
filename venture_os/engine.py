"""
VentureOS: Master Orchestration Engine
Executes the deterministic state machine connecting all 7 agents.
"""

from venture_os.state import VentureState, ProspectAsset
from venture_os.agents.pain_hunter import PainHunterAgent
from venture_os.agents.feasibility_arbiter import FeasibilityArbiterAgent
from venture_os.agents.product_synthesizer import ProductSynthesizerAgent
from venture_os.agents.sandbox_verifier import SandboxVerifierAgent
from venture_os.agents.trojan_auditor import TrojanAuditorAgent
from venture_os.agents.outbound_sdr import OutboundSDRAgent
from venture_os.agents.governor import GovernorAgent
import uuid


class VentureOSEngine:
    """The master orchestrator for end-to-end autonomous product-to-outbound cycles."""

    def __init__(self):
        self.pain_hunter = PainHunterAgent()
        self.feasibility_arbiter = FeasibilityArbiterAgent()
        self.product_synthesizer = ProductSynthesizerAgent()
        self.sandbox_verifier = SandboxVerifierAgent()
        self.trojan_auditor = TrojanAuditorAgent()
        self.outbound_sdr = OutboundSDRAgent()
        self.governor = GovernorAgent()

    def run_lifecycle(self, niche: str, sample_prospects: list[ProspectAsset], simulated_replies: int = 1) -> VentureState:
        """Executes the full pipeline from raw pain discovery to pre-computed outbound delivery."""
        
        # 1. Initialize State
        state = VentureState(
            venture_id=f"ven_{uuid.uuid4().hex[:6]}",
            niche=niche
        )
        state.history_log.append(f"[Engine] Starting VentureOS lifecycle for niche: '{niche}' (ID: {state.venture_id})")

        # 2. Mine Pain
        state = self.pain_hunter.execute(state)

        # 3. Stress-Test Feasibility
        state = self.feasibility_arbiter.execute(state)
        if not state.feasibility.passed:
            state.history_log.append("[Engine] Pipeline stopped: Feasibility test failed.")
            return state

        # 4. Synthesize Micro-Product Code & Spec
        state = self.product_synthesizer.execute(state)

        # 5. Sandbox Self-Healing Verification
        state = self.sandbox_verifier.execute(state)
        if state.product_spec.verification_status != "passed":
            state.history_log.append("[Engine] Pipeline stopped: Sandbox verification failed.")
            return state

        # 6. Trojan Pre-Computation Audit on Real Prospect Assets
        state = self.trojan_auditor.execute(state, sample_prospects)

        # 7. Synthesize Personalized Outbound Campaign
        state = self.outbound_sdr.execute(state, sample_prospects)

        # 8. Governance & Telemetry Check
        state = self.governor.evaluate(state, simulated_replies=simulated_replies)

        return state
