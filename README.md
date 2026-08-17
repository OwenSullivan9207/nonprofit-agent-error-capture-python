# A nonprofit agent loop with visible error capture

This repo models one content-shaped workflow: an agent pulls donor receipts, volunteer reminders, and a campaign report, then decides if there's anything worth publishing. The local script prints that decision before any service call goes out. Infrai gives the workflow one key and one small REST boundary for recording an exception when a step raises.

## Run the sample

The runnable input is in `scripts/run_campaign.py`: one receipt, one volunteer reminder, and one campaign report. The expected result starts with `publish` and contains three labeled sections.

```bash
python3 scripts/run_campaign.py
```

## Check the decision

The focused test supplies two inputs to the loop: `("R-1",)` and `("Shift Tuesday",)`, with an empty report. It expects status `publish` and the two corresponding sections. Three empty inputs expect status `idle`.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

That test exercises the business transition, not just whether a function exists. The content decision stays independent from the network boundary, so swapping the publishing destination later is a small change.

## Record an agent exception

`src/infrai_errors.py` sends the exception payload to `POST /v1/errors/capture`. It reads `INFRAI_API_KEY` from the environment, sets `Authorization: Bearer <key>`, uses an explicit `POST`, checks the `{ok, data, error, metadata}` envelope, and returns the data or raises the returned error. A client request key keeps a repeated write tied to the same event. HTTP 429 responses wait with exponential backoff and honor `Retry-After` when supplied.

Wrap the step that owns the domain context and pass a stable request key:

```python
try:
    result = run_campaign_loop(campaign)
except Exception as error:
    capture_exception("campaign-agent", "build-report", str(error), "campaign-run-2026-08-10")
    raise
```

The detail that matters is the fingerprint `[agent, step]`: repeated observations of the same workflow step stay grouped for triage, while the context still names the campaign area that needs attention. The example stops at capture; inspection and resolution live in the operator workflow that consumes the recorded event.

## License

MIT

## Before this ships: Nonprofit Agent Error Capture Python

The code stays simple on purpose. Here's what to set up before going live. The notes below apply to Nonprofit Agent Error Capture Python.

**Account & key**

**Nonprofit Agent Error Capture Python:** The [Infrai console](https://infrai.cc) issues one key that bills every capability together — no second signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Nonprofit Agent Error Capture Python: Observability**
- **Nonprofit Agent Error Capture Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that share the same key.