#!/usr/bin/env python3
"""
register_copilot.py — Register or update the Mission Readiness Officer copilot
via the IBM Bob REST API.

Usage:
    python src/bob/register_copilot.py               # register the copilot
    python src/bob/register_copilot.py --dry-run     # print payload only
"""

import argparse
import json
import os
import sys
from pathlib import Path

# ---------------------------------------------------------------------------
# Optional: load .env file if python-dotenv is available
# ---------------------------------------------------------------------------
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    import yaml
except ImportError:
    print("ERROR: PyYAML is required. Install it with: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Resolve paths relative to the repository root (two levels up from this file)
# ---------------------------------------------------------------------------
REPO_ROOT = Path(__file__).resolve().parents[2]
BOB_DIR = REPO_ROOT / ".bob"
BOB_YAML = BOB_DIR / "bob.yaml"
SYSTEM_PROMPT_PATH = BOB_DIR / "system-prompt.md"
TOOLS_YAML_PATH = BOB_DIR / "tools.yaml"


def load_config() -> dict:
    """Load and merge .bob/bob.yaml, system-prompt.md, and tools.yaml into a single payload."""
    if not BOB_YAML.exists():
        print(f"ERROR: Config file not found: {BOB_YAML}")
        sys.exit(1)

    with BOB_YAML.open() as fh:
        config = yaml.safe_load(fh)

    # Inline the system prompt text
    if not SYSTEM_PROMPT_PATH.exists():
        print(f"ERROR: System prompt not found: {SYSTEM_PROMPT_PATH}")
        sys.exit(1)
    config["system_prompt_text"] = SYSTEM_PROMPT_PATH.read_text()

    # Inline the tools definitions
    if not TOOLS_YAML_PATH.exists():
        print(f"ERROR: Tools config not found: {TOOLS_YAML_PATH}")
        sys.exit(1)
    with TOOLS_YAML_PATH.open() as fh:
        tools_data = yaml.safe_load(fh)
    config["tools_definitions"] = tools_data.get("tools", [])

    # Remove path references — they are now inlined
    config.pop("system_prompt", None)
    config.pop("tools", None)

    return config


def build_payload(config: dict) -> dict:
    """Build the IBM Bob REST API registration payload."""
    return {
        "name": config.get("name"),
        "description": config.get("description"),
        "version": config.get("version"),
        "model": config.get("model", {}),
        "system_prompt": config.get("system_prompt_text"),
        "tools": config.get("tools_definitions", []),
        "context": config.get("context", []),
    }


def register(payload: dict, api_url: str, api_key: str) -> None:
    """POST the payload to the IBM Bob REST API."""
    try:
        import requests
    except ImportError:
        print("ERROR: requests library is required. Install it with: pip install requests")
        sys.exit(1)

    endpoint = f"{api_url.rstrip('/')}/v1/copilots"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }

    print(f"Registering copilot at: {endpoint}")
    response = requests.post(endpoint, json=payload, headers=headers, timeout=30)

    if response.ok:
        print(f"SUCCESS [{response.status_code}]: Copilot registered.")
        try:
            result = response.json()
            print(json.dumps(result, indent=2))
        except Exception:
            print(response.text)
    else:
        print(f"ERROR [{response.status_code}]: Registration failed.")
        print(response.text)
        sys.exit(1)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Register the Mission Readiness Officer copilot with IBM Bob REST API."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Print the registration payload as JSON without calling the API.",
    )
    args = parser.parse_args()

    config = load_config()
    payload = build_payload(config)

    if args.dry_run:
        print("=== DRY RUN — registration payload (no API call made) ===\n")
        print(json.dumps(payload, indent=2))
        return

    # --- Live registration ---
    api_key = os.getenv("BOB_API_KEY")
    api_url = os.getenv("BOB_API_URL")

    missing = []
    if not api_key:
        missing.append("BOB_API_KEY")
    if not api_url:
        missing.append("BOB_API_URL")

    if missing:
        print("ERROR: The following environment variables are not set:")
        for var in missing:
            print(f"  {var}")
        print("\nSet them before running:")
        print("  export BOB_API_KEY=your_key")
        print("  export BOB_API_URL=https://your-bob-instance.ibm.com")
        print("\nOr use --dry-run to inspect the payload without credentials.")
        sys.exit(1)

    register(payload, api_url, api_key)


if __name__ == "__main__":
    main()
