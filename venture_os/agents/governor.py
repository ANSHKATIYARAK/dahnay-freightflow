"""
Agent 7: Pipeline Governor & Telemetry Evaluator
Enforces statistical kill criteria and automated pivot governance.
Prevents emotional attachment to ideas that lack real commercial traction.
"""

from venture_os.state import VentureState


class GovernorAgent:
    """Monitors live conversion telemetry and triggers automated kill criteria."""

    def __init__(self, name: str = "Governor"):
        self.name = name

    def evaluate(self, state: VentureState, simulated_replies: int = 0) -> VentureState:
        tel = state.telemetry
        tel.total_prospects_audited = len(state.audits)
        tel.total_outreach_sent = len(state.outreach_campaign)
        tel.positive_replies = simulated_replies

        if tel.total_outreach_sent > 0:
            tel.conversion_rate = tel.positive_replies / tel.total_outreach_sent

        # Check Kill Criteria
        if tel.total_outreach_sent >= 10 and tel.conversion_rate < tel.kill_criteria_threshold:
            tel.status = "killed"
            state.history_log.append(
                f"[{self.name}] KILL CRITERIA TRIGGERED: Response rate ({tel.conversion_rate*100:.1f}%) "
                f"fell below required threshold ({tel.kill_criteria_threshold*100:.1f}%). PIVOT NICHE IMMEDIATELY."
            )
        elif tel.positive_replies >= 1:
            tel.status = "graduated"
            state.history_log.append(
                f"[{self.name}] VALIDATION SUCCESS: {tel.positive_replies} verified reply/pilot lead acquired! "
                f"Transitioning to Pilot Contract execution."
            )
        else:
            tel.status = "evaluating"
            state.history_log.append(f"[{self.name}] Pipeline active: Sent={tel.total_outreach_sent}, Responses={tel.positive_replies}")

        return state
