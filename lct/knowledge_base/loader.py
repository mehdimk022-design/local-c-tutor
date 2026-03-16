from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def get_topics_file_path() -> Path:
    return Path(__file__).resolve().parents[2] / "data" / "c_topics" / "topics.json"


def load_topics() -> list[dict[str, Any]]:
    topics_path = get_topics_file_path()

    with topics_path.open("r", encoding="utf-8") as file:
        data = json.load(file)

    if not isinstance(data, list):
        raise ValueError("topics.json must contain a list of topics.")

    return data


def detect_topics_in_source(source_code: str) -> list[dict[str, Any]]:
    detected_topics: list[dict[str, Any]] = []
    source_lower = source_code.lower()

    for topic in load_topics():
        keywords = topic.get("keywords", [])

        if any(str(keyword).lower() in source_lower for keyword in keywords):
            detected_topics.append(topic)

    return detected_topics