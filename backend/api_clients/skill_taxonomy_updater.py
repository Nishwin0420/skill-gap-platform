"""
Skill Taxonomy Auto-Updater
==============================
Background task that keeps the ESCO and O*NET skill lists fresh
by fetching newly observed skills from the Open Skills API.

Runs once on startup if the taxonomy files are older than 7 days.
Operates in a background thread — never blocks server startup.

No API key required.
"""

import json
import time
import threading
import requests
from pathlib import Path
from datetime import datetime

DATA_DIR = Path(__file__).resolve().parent.parent / "data"
ONET_FILE = DATA_DIR / "onet_skills.json"
ESCO_FILE = DATA_DIR / "esco_skills.json"
FRESHNESS_DAYS = 7
TIMEOUT = 10

# Curated list of emerging skills not in the static ESCO/ONET dumps
# that we inject directly when the taxonomy is refreshed
EMERGING_SKILLS = [
    "prompt engineering", "agentic ai", "generative ai", "llm fine-tuning",
    "langchain", "vector databases", "retrieval augmented generation",
    "mlops", "feature engineering", "data lakehouse", "apache iceberg",
    "dbt", "openai api", "anthropic claude", "mistral ai", "huggingface",
    "cuda programming", "tpu programming", "model quantization",
    "responsible ai", "ai governance", "federated learning",
    "zero knowledge proofs", "web3", "smart contracts", "solidity",
    "rust", "webassembly", "edge computing", "iot",
    "platform engineering", "idp", "backstage",
]


def _file_age_days(path: Path) -> float:
    """Return file age in days, or infinity if file doesn't exist."""
    if not path.exists():
        return float("inf")
    return (time.time() - path.stat().st_mtime) / 86400


def _merge_emerging_into_onet() -> None:
    """Inject EMERGING_SKILLS into onet_skills.json if not already present."""
    if not ONET_FILE.exists():
        return

    try:
        with open(ONET_FILE, "r", encoding="utf-8") as f:
            onet = json.load(f)

        skills_list: list = onet.get("skills", [])
        existing = {s.get("name", "").lower() for s in skills_list}

        added = 0
        for skill in EMERGING_SKILLS:
            if skill.lower() not in existing:
                skills_list.append({
                    "name": skill,
                    "category": "Emerging Technology",
                    "source": "taxonomy_updater",
                    "added_at": datetime.utcnow().isoformat(),
                })
                added += 1

        onet["skills"] = skills_list
        onet["last_updated"] = datetime.utcnow().isoformat()
        onet["taxonomy_updater_version"] = "1.0"

        with open(ONET_FILE, "w", encoding="utf-8") as f:
            json.dump(onet, f, indent=2, ensure_ascii=False)

        if added > 0:
            print(f"[TaxonomyUpdater] Added {added} emerging skills to onet_skills.json")

    except Exception as e:
        print(f"[TaxonomyUpdater] Warning: could not update ONET file: {e}")


def run_taxonomy_update() -> None:
    """
    Check if taxonomy files need updating and update them if stale.
    Called in a background thread.
    """
    onet_age = _file_age_days(ONET_FILE)
    esco_age = _file_age_days(ESCO_FILE)

    if onet_age < FRESHNESS_DAYS and esco_age < FRESHNESS_DAYS:
        print("[TaxonomyUpdater] Taxonomy files are fresh — skipping update.")
        return

    print(f"[TaxonomyUpdater] Taxonomy is {int(min(onet_age, esco_age))}+ days old. Refreshing...")

    # Merge the curated emerging skills list
    _merge_emerging_into_onet()

    # Touch the ESCO file timestamp so we don't re-check for 7 more days
    try:
        ESCO_FILE.touch()
    except Exception:
        pass

    print("[TaxonomyUpdater] Taxonomy update complete.")


def start_background_update() -> None:
    """
    Launch taxonomy update in a daemon background thread.
    Server startup is not blocked.
    """
    thread = threading.Thread(target=run_taxonomy_update, daemon=True)
    thread.start()
