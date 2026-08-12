import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nonprofit_loop import CampaignInput, render_loop_result, run_campaign_loop


campaign = CampaignInput(
    donor_receipts=("Receipt R-104 ready for Maya",),
    volunteer_reminders=("Saturday pantry shift at 10:00",),
    campaign_report="Spring drive: 68% of the target recorded.",
)
result = run_campaign_loop(campaign)
print(result.status)
print(render_loop_result(result))
