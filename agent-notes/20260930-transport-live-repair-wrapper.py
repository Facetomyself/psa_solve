"""Single parent-reviewed engine-local transport correction; no v2 claim."""
import argparse
import importlib.util
from pathlib import Path
import sys

BASE_WRAPPER = Path(r"D:\reverse_ENV\workspace\psa_solve\agent-notes\20260930-transport-live-wrapper.py")
spec = importlib.util.spec_from_file_location("psa_transport_operation", BASE_WRAPPER)
op = importlib.util.module_from_spec(spec)
spec.loader.exec_module(op)
op.REPAIR = True
op.RUN_ID = "3355e716c80b4c60b07c8caa5c2d2a57"
op.STATE = op.NOTES / "20260930-transport-live.repair.state.json"
op.CONTROL = op.BASE / "control" / op.RUN_ID
op.RUN = op.BASE / op.RUN_ID
op.RUNNER = op.CONTROL / "transport-runner.js"
# Extend the same chrome-only readback family with the corrected proxy selector.
old = '"network.process.enabled"]'
new = '"network.process.enabled", "network.proxy.type"]'
if op.TRANSPORT_HELPER.count(old) != 1:
    raise RuntimeError("ambiguous-proxy-readback-anchor")
op.TRANSPORT_HELPER = op.TRANSPORT_HELPER.replace(old, new, 1)

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("phase", choices=["prepare", "execute"])
    args = parser.parse_args()
    try:
        op.prepare() if args.phase == "prepare" else op.execute()
    except Exception as error:
        op.state(status="failed", terminal="failed", wrapperPid=None, errorType=type(error).__name__)
        print(op.json.dumps({"status": "failed", "errorType": type(error).__name__}))
        sys.exit(1)
