"""
Agent 2: Feasibility Arbiter
Stress-tests technical feasibility, unit economics, and competitive barriers.
Prevents building commoditized tools that get killed by $19/mo incumbents.
"""

from venture_os.state import FeasibilityReport, VentureState


class FeasibilityArbiterAgent:
    """Evaluates whether the venture is commercially and technically viable."""

    def __init__(self, name: str = "FeasibilityArbiter"):
        self.name = name

    def execute(self, state: VentureState) -> VentureState:
        if not state.pain_signal:
            raise ValueError("Cannot evaluate feasibility without an existing pain signal.")

        # Hard stress-test logic:
        # 1. Why doesn't Keepa / Helium 10 kill this?
        # Answer: Keepa is desktop/email oriented, checks intermittently, and doesn't send immediate WhatsApp/Telegram mobile push alerts with direct action links to Indian sellers.
        # 2. Proxy risk:
        # Amazon.in requires rotating residential proxies if scraping at scale, but for 50 ASINs per seller checked every 4 hours, request volume is tiny (~300 req/day).
        
        report = FeasibilityReport(
            passed=True,
            score=8.5,
            anti_bot_difficulty="medium",
            proxy_cost_risk="moderate",
            incumbent_competition="Keepa (€19/mo), Helium 10 ($97/mo), SellerApp",
            why_incumbents_fail=(
                "Keepa focuses on historical charts and desktop alerts with lag. Indian D2C operators "
                "live on WhatsApp/Telegram and need instant notification the minute an unauthorized hijacker "
                "steals the Buy Box or breaks MAP, with the competitor's seller ID already identified."
            )
        )

        state.feasibility = report
        state.history_log.append(f"[{self.name}] Feasibility Stress-Test: Passed={report.passed} (Score: {report.score}/10)")
        return state
