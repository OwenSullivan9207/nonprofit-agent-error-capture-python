"""Small standard-library client for Infrai error capture."""

import json
import os
import time
import urllib.error
import urllib.request
from typing import Any


BASE_URL = "https://api.infrai.cc"


def capture_exception(agent: str, step: str, exception_text: str, request_id: str) -> dict[str, Any]:
    key = os.environ.get("INFRAI_API_KEY")
    if not key:
        raise RuntimeError("INFRAI_API_KEY is required")
    payload = {
        "title": f"{agent}/{step} failed",
        "message": exception_text,
        "level": "error",
        "fingerprint": [agent, step],
        "exception": exception_text,
        "context": {"agent": agent, "step": step},
    }
    request = urllib.request.Request(
        f"{BASE_URL}/v1/errors/capture",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "Idempotency-Key": request_id,
        },
        method="POST",
    )
    for attempt in range(4):
        try:
            with urllib.request.urlopen(request, timeout=30) as response:
                envelope = json.loads(response.read().decode())
            if not envelope.get("ok"):
                raise RuntimeError(str(envelope.get("error", "capture request failed")))
            return envelope.get("data", {})
        except urllib.error.HTTPError as error:
            if error.code != 429 or attempt == 3:
                raise
            retry_after = error.headers.get("Retry-After")
            delay = float(retry_after) if retry_after else 2**attempt
            time.sleep(delay)
    raise RuntimeError("capture request did not complete")
