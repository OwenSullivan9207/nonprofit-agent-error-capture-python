import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from nonprofit_loop import CampaignInput, render_loop_result, run_campaign_loop


class NonprofitLoopTest(unittest.TestCase):
    def test_receipt_and_reminder_move_loop_to_publish(self):
        result = run_campaign_loop(CampaignInput(("R-1",), ("Shift Tuesday",), ""))
        self.assertEqual(result.status, "publish")
        self.assertEqual(render_loop_result(result), "Donor receipts\nR-1\n\nVolunteer reminders\nShift Tuesday")

    def test_empty_inputs_leave_loop_idle(self):
        result = run_campaign_loop(CampaignInput((), (), ""))
        self.assertEqual(result, type(result)("idle", ()))
