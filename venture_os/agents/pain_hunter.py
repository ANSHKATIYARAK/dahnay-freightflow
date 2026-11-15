"""
Agent 1: Pain Hunter
Mines market friction signals and structures them into validated PainSignal contracts.
"""

from venture_os.state import PainSignal, VentureState
import uuid


class PainHunterAgent:
    """Discovers and structures acute operational pain points."""

    def __init__(self, name: str = "PainHunter"):
        self.name = name

    def execute(self, state: VentureState, simulated_query: str = None) -> VentureState:
        """
        Mines the target niche for severe pain signals.
        In production, this queries Reddit APIs, Seller Forums, or web search.
        """
        # Grounded real-world case: Amazon India / Meesho Buy Box & Hijacking
        pain = PainSignal(
            signal_id=f"sig_{uuid.uuid4().hex[:6]}",
            niche=state.niche,
            source_platform="seller_forums",
            raw_quote=(
                "Losing 30% of sales on our hero SKU because a 3rd party seller undercut us by ₹5 at 2 AM "
                "and stole the Buy Box. We didn't notice until 11 AM next day. Keepa doesn't alert our phone fast enough."
            ),
            target_persona="Amazon India Private Label & D2C Brand Owners",
            current_workaround="Manual refresh 4 times a day or checking seller central reports late",
            estimated_monthly_loss_inr=45000.0,
            urgency_score=9.2
        )
        
        state.pain_signal = pain
        state.history_log.append(f"[{self.name}] Discovered high-urgency pain signal: {pain.signal_id} (Score: {pain.urgency_score})")
        return state
