import json
import os
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from datetime import datetime, timezone

from agents.content_fetcher import fetch_content
from agents.item_scorer import score_item
from agents.weighing import load_prefs

_FETCH_CONTENT = os.getenv("BYOF_FETCH_CONTENT", "true").lower() != "false"


@dataclass
class SwarmResult:
    results: list[dict] = field(default_factory=list)
    total_input_tokens: int = 0
    total_output_tokens: int = 0
    failure_count: int = 0


def _process_item(item: dict, prefs: dict) -> tuple[dict, dict | None, dict]:
    if _FETCH_CONTENT:
        fetched = fetch_content(item.get("url", ""))
        item_enriched = {**item, **fetched}
    else:
        item_enriched = {**item, "body": "", "image_url": None, "image_type": None}
    result, usage = score_item(item_enriched, prefs)
    return item_enriched, result, usage


def run_swarm(
    items: list[dict],
    prefs_path: str = "preferences.json",
    max_workers: int = 2,
) -> SwarmResult:
    if not items:
        return SwarmResult()

    prefs = load_prefs(prefs_path)
    swarm = SwarmResult()

    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        futures = {executor.submit(_process_item, item, prefs): item for item in items}
        for future in as_completed(futures):
            try:
                item_enriched, result, usage = future.result()
                swarm.total_input_tokens += usage.get("input_tokens", 0)
                swarm.total_output_tokens += usage.get("output_tokens", 0)
                if result is None:
                    swarm.failure_count += 1
                else:
                    swarm.results.append({
                        "url": item_enriched.get("url"),
                        "body": item_enriched.get("body", ""),
                        "image_url": item_enriched.get("image_url"),
                        "image_type": item_enriched.get("image_type"),
                        "llm_summary": result.get("summary"),
                        "llm_keywords": json.dumps(result.get("keywords", [])),
                        "llm_categories": json.dumps(result.get("categories", [])),
                        "llm_score": result.get("score"),
                        "scored_at": datetime.now(timezone.utc).isoformat(),
                    })
            except Exception:
                swarm.failure_count += 1

    return swarm
