"""
End-to-end test runner for the TTB Label Verification API.

Sends each label image in manifest.json to the /api/verify endpoint
and compares the result against the expected pass/fail values.

Usage:
    # Against local wrangler dev server (default):
    uv run tests/run_tests.py

    # Against a deployed URL:
    uv run tests/run_tests.py --url https://your-site.pages.dev

Requirements: wrangler must be running locally if using the default URL.
    wrangler pages dev public --compatibility-flag=nodejs_compat
"""

import argparse
import json
import sys
from pathlib import Path

try:
    import httpx
except ModuleNotFoundError:
    print("Missing dependency. Run with: uv run --with httpx tests/run_tests.py")
    sys.exit(1)

MANIFEST = Path(__file__).parent / "manifest.json"
DEFAULT_URL = "http://localhost:8788"


def check(actual, expected, key):
    """Return (passed: bool, detail: str)."""
    exp = expected.get(key)
    got = actual.get(key, {}).get("pass") if isinstance(actual.get(key), dict) else None
    if exp is None:
        return True, "n/a"
    ok = got == exp
    symbol = "✅" if ok else "❌"
    return ok, f"{symbol} expected={'pass' if exp else 'fail'}, got={'pass' if got else ('fail' if got is False else '?')}"


def run(base_url: str):
    manifest = json.loads(MANIFEST.read_text())
    cases = manifest["cases"]

    passed = 0
    failed = 0

    print(f"\nTTB Label Verification — Test Run")
    print(f"Endpoint: {base_url}/api/verify")
    print(f"Cases:    {len(cases)}\n")
    print("─" * 70)

    for case in cases:
        label_path = Path(__file__).parent.parent / case["file"]
        brand = case["verify_with"]["brand"]
        abv = case["verify_with"]["abv"]
        expected = case["expected"]

        print(f"\n{label_path.name}")
        print(f"  {case['description']}")

        if not label_path.exists():
            print(f"  ⚠️  File not found: {label_path} — skipping")
            failed += 1
            continue

        with open(label_path, "rb") as f:
            image_bytes = f.read()

        try:
            resp = httpx.post(
                f"{base_url}/api/verify",
                files={"image": (label_path.name, image_bytes, "image/png")},
                data={"brand": brand, "abv": abv},
                timeout=30,
            )
        except httpx.ConnectError:
            print(f"  ⚠️  Connection refused at {base_url}. Is wrangler running?")
            failed += 1
            continue

        if resp.status_code != 200:
            print(f"  ⚠️  HTTP {resp.status_code}: {resp.text[:200]}")
            failed += 1
            continue

        result = resp.json()

        if "error" in result:
            print(f"  ⚠️  API error: {result['error']}")
            failed += 1
            continue

        case_ok = True
        for key in ("brand", "abv", "warning"):
            ok, detail = check(result, expected, key)
            found = ""
            if key in result and isinstance(result[key], dict):
                fv = result[key].get("found") or result[key].get("notes") or ""
                if fv:
                    found = f" ({fv[:60]})"
            print(f"  {key:8s} {detail}{found}")
            if not ok:
                case_ok = False

        if case_ok:
            passed += 1
        else:
            failed += 1

    print("\n" + "─" * 70)
    total = passed + failed
    print(f"Results: {passed}/{total} cases matched expectations")
    if failed:
        print(f"         {failed} case(s) did not match — see above")
        sys.exit(1)
    else:
        print("All cases passed.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--url", default=DEFAULT_URL, help="Base URL of the app")
    args = parser.parse_args()
    run(args.url.rstrip("/"))
