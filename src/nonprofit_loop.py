"""Domain model for a small nonprofit agent loop."""

from dataclasses import dataclass


@dataclass(frozen=True)
class CampaignInput:
    donor_receipts: tuple[str, ...]
    volunteer_reminders: tuple[str, ...]
    campaign_report: str


@dataclass(frozen=True)
class LoopResult:
    status: str
    messages: tuple[str, ...]


def run_campaign_loop(input_data: CampaignInput) -> LoopResult:
    """Return the messages an agent should publish for this campaign run."""
    messages: list[str] = []
    if input_data.donor_receipts:
        messages.append("Donor receipts\n" + "\n".join(input_data.donor_receipts))
    if input_data.volunteer_reminders:
        messages.append("Volunteer reminders\n" + "\n".join(input_data.volunteer_reminders))
    if input_data.campaign_report:
        messages.append("Campaign report\n" + input_data.campaign_report)
    if not messages:
        return LoopResult("idle", ())
    return LoopResult("publish", tuple(messages))


def render_loop_result(result: LoopResult) -> str:
    if result.status == "idle":
        return "No nonprofit updates to publish."
    return "\n\n".join(result.messages)
