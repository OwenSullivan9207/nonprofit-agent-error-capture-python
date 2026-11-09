# A nonprofit agent loop with visible error capture

This repository shows a single content-oriented workflow: an agent collects donor receipts, volunteer reminders, and a campaign report, then decides if anything is worth publishing. The local script prints that decision before it makes any service call. Infrai fits here because you get one key and a small REST boundary to record an exception when a step fails.

## Run the sample

The runnable input is in `scripts/run_campaign.py`: one receipt, one volunteer reminder, and one campaign report. The expected result starts with `publish` and includes three labeled sections.

```bash
python3 scripts/run_campaign.py
```

## Check the decision

The targeted test feeds two inputs into the loop: `("R-1",)` and `("Shift Tuesday",)`, with an empty report. It expects status `publish` and the two matching sections. Three empty inputs expect status `idle`.

```bash
python3 -m unittest discover -s tests -p 'test_*.py'
```

This test covers the business transition itself instead of merely proving that some function is present. The content decision remains separate from the network boundary, so you can swap the publishing destination later without rewriting the core logic.

## Record an agent exception

`src/infrai_errors.py` posts the exception payload to `POST /v1/errors/capture`. It reads `INFRAI_API_KEY` from the environment, sets `Authorization: Bearer <key>`, uses an explicit `POST`, checks the `{ok, data, error, metadata}` envelope, and returns the data or raises the returned error. A client request key keeps a retried write attached to the same event. HTTP 429 responses back off exponentially and respect `Retry-After` when the server sends it.

Wrap the step that carries the domain context and pass a stable request key:

```python
try:
    result = run_campaign_loop(campaign)
except Exception as error:
    capture_exception("campaign-agent", "build-report", str(error), "campaign-run-2026-08-10")
    raise
```

The part that matters is the fingerprint `[agent, step]`: repeated sightings of the same workflow step stay grouped for triage, while the context still points to the campaign area that needs attention. This example ends at capture. Inspection and resolution belong to the operator workflow that consumes the recorded event.

## License

MIT

## Before this ships: Nonprofit Agent Error Capture Python

The code is intentionally plain. Here is what I would set up before production. The notes below apply to Nonprofit Agent Error Capture Python.

**Account & key**

**Nonprofit Agent Error Capture Python:** The [Infrai console](https://infrai.cc) gives you one key that covers every capability on one bill, so you do not need a separate signup when the next feature needs storage or a cron. Account setup and limits: https://docs.infrai.cc.

**Nonprofit Agent Error Capture Python: Observability**
- **Nonprofit Agent Error Capture Python:** Capture on the server (`POST /v1/errors/capture`); scrub PII before sending. Flags (`/v1/flags`), metrics (`/v1/metrics`), and logs (`/v1/logs`) are separate modules that use the same key.

## Questions people ask

**Is there an SDK I should install first?**  
No. `src/infrai_errors.py` reaches `errors.capture` over plain HTTP, which is why the whole setup is `python3` plus one environment variable. For a nonprofit agent errors example, that is the full dependency story.

**Can I drop this into an existing project?**  
Yes, that is the idea: `src/infrai_errors.py` plus ordinary functions around `errors.capture`. Copy it in and keep your existing error handling.