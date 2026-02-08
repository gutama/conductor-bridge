#!/usr/bin/env python3
"""
Conductor environment detection and status reporting.

Usage:
    python3 detect_conductor.py [project_root]

Returns JSON with:
- exists: whether conductor/ directory exists
- setup_complete: whether setup is fully done
- active_tracks: list of in-progress tracks
- pending_tracks: list of pending tracks
- context_files: which context files exist
"""

import json
import os
import re
import sys
from pathlib import Path


def detect_conductor(project_root: str = ".") -> dict:
    root = Path(project_root).resolve()
    conductor_dir = root / "conductor"

    result = {
        "exists": conductor_dir.is_dir(),
        "setup_complete": False,
        "classification": None,
        "context_files": {},
        "tracks": [],
        "active_track": None,
        "next_task": None,
    }

    if not result["exists"]:
        return result

    # Check context files
    for fname in [
        "index.md", "product.md", "product-guidelines.md",
        "tech-stack.md", "workflow.md", "tracks.md"
    ]:
        result["context_files"][fname] = (conductor_dir / fname).is_file()

    # Check setup state
    state_file = conductor_dir / "setup_state.json"
    if state_file.is_file():
        try:
            state = json.loads(state_file.read_text())
            result["setup_complete"] = state.get("STEP") == "complete"
            result["classification"] = state.get("CLASSIFICATION")
        except (json.JSONDecodeError, KeyError):
            pass

    # Scan tracks
    tracks_dir = conductor_dir / "tracks"
    if tracks_dir.is_dir():
        for track_path in sorted(tracks_dir.iterdir()):
            if not track_path.is_dir():
                continue

            track_id = track_path.name
            track_info = {"id": track_id, "status": "unknown", "next_task": None}

            # Read metadata
            meta_file = track_path / "metadata.json"
            if meta_file.is_file():
                try:
                    meta = json.loads(meta_file.read_text())
                    track_info["status"] = meta.get("status", "unknown")
                    track_info["title"] = meta.get("title", track_id)
                except (json.JSONDecodeError, KeyError):
                    pass

            # Parse plan for progress
            plan_file = track_path / "plan.md"
            if plan_file.is_file():
                plan_text = plan_file.read_text()
                total = len(re.findall(r"^- \[[ x~]\]", plan_text, re.MULTILINE))
                done = len(re.findall(r"^- \[x\]", plan_text, re.MULTILINE))
                in_progress = len(re.findall(r"^- \[~\]", plan_text, re.MULTILINE))
                pending = len(re.findall(r"^- \[ \]", plan_text, re.MULTILINE))

                track_info["tasks_total"] = total
                track_info["tasks_done"] = done
                track_info["tasks_in_progress"] = in_progress
                track_info["tasks_pending"] = pending

                # Find next task
                for line in plan_text.splitlines():
                    line_stripped = line.strip()
                    if line_stripped.startswith("- [~]"):
                        track_info["next_task"] = line_stripped[6:].strip()
                        break
                    elif line_stripped.startswith("- [ ]") and not track_info.get("next_task"):
                        track_info["next_task"] = line_stripped[6:].strip()

            result["tracks"].append(track_info)

            # Set active track
            if track_info["status"] == "in_progress" and not result["active_track"]:
                result["active_track"] = track_info

    return result


def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    result = detect_conductor(project_root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
