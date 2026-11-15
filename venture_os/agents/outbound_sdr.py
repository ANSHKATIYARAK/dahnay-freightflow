"""
Agent 6: Outbound SDR (The Loss-Prevention Closer)
Synthesizes hyper-personalized outbound messages containing the pre-computed audit.
Transitions outreach from unsolicited pitch to urgent advisory alert.
"""

from venture_os.state import OutreachHook, VentureState, ProspectAsset
import uuid


class OutboundSDRAgent:
    """Drafts personalized, high-converting loss-prevention hooks."""

    def __init__(self, name: str = "OutboundSDR"):
        self.name = name

    def execute(self, state: VentureState, prospects: list[ProspectAsset]) -> VentureState:
        if not state.audits:
            raise ValueError("Cannot draft outbound hooks without pre-computed audits.")

        prospect_map = {p.prospect_id: p for p in prospects}

        for audit in state.audits:
            prospect = prospect_map.get(audit.prospect_id)
            if not prospect:
                continue

            subject = f"Urgent heads up: {prospect.product_identifier} lost Buy Box on Amazon.in"
            body = (
                f"Hi {prospect.contact_name},\n\n"
                f"Was checking top category listings on Amazon.in today and noticed an issue on your SKU ({audit.product_identifier}):\n\n"
                f"• Current Buy Box Winner: {audit.current_winner}\n"
                f"• Your Price: ₹{audit.client_price_inr:,.0f} | Hijacker Price: ₹{audit.winning_price_inr:,.0f}\n"
                f"• Estimated Weekly Revenue Leak: ~₹{audit.estimated_weekly_revenue_leak_inr:,.0f}/week\n\n"
                f"Most sellers don't catch these night-time price undercuts until days later.\n\n"
                f"We run an automated 24/7 radar that pings your team's Telegram bot within 3 minutes "
                f"of any unauthorized seller stealing your Buy Box or breaking MAP, so you can re-adjust price or file an IP claim instantly.\n\n"
                f"We can deploy this 24/7 radar for 20 of your top ASINs on a 7-day pilot for ₹5,000 (runs securely on your own server/bot).\n\n"
                f"Would you like me to send over the live alert feed for this SKU today?"
            )

            hook = OutreachHook(
                hook_id=f"hook_{uuid.uuid4().hex[:6]}",
                prospect_id=prospect.prospect_id,
                subject_line=subject,
                body_markdown=body,
                call_to_action="Reply 'YES' to receive the live alert feed on Telegram",
                pilot_price_inr=5000.0
            )

            state.outreach_campaign.append(hook)
            state.history_log.append(f"[{self.name}] Created personalized audit hook for {prospect.contact_name} ({prospect.business_name})")

        return state
