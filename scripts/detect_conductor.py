#!/usr/bin/env python3
"""
Conductor environment detection and status reporting.

Usage:
    python3 detect_conductor.py [project_root]

Returns JSON with:
- exists: whether conductor/ directory exists
- setup_complete: whether setup is fully done
- setup_step: current setup step (if not complete)
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
        "setup_step": None,
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

    # Check code style guides
    styleguides_dir = conductor_dir / "code_styleguides"
    if styleguides_dir.is_dir():
        result["context_files"]["code_styleguides"] = [
            f.name for f in sorted(styleguides_dir.iterdir()) if f.suffix == ".md"
        ]
    else:
        result["context_files"]["code_styleguides"] = []

    # Check setup state
    state_file = conductor_dir / "setup_state.json"
    if state_file.is_file():
        try:
            state = json.loads(state_file.read_text())
            step = state.get("last_successful_step", state.get("STEP", ""))
            result["setup_step"] = step
            result["setup_complete"] = step in ("complete", "3.3_initial_track_generated")
            result["classification"] = state.get("CLASSIFICATION")
        except (json.JSONDecodeError, KeyError):
            pass

    # Parse tracks.md for the new list format
    tracks_file = conductor_dir / "tracks.md"
    if tracks_file.is_file():
        tracks_text = tracks_file.read_text()

        # New format: - [x] **Track: Description**
        for match in re.finditer(
            r"^- \[([x~\s])\] \*\*Track:\s*(.+?)\*\*\s*\n\s*\*Link:\s*\[.*?\]\((.*?)\)",
            tracks_text, re.MULTILINE
        ):
            status_char, title, link = match.groups()
            status_map = {"x": "complete", "~": "in_progress", " ": "pending"}
            track_id = link.strip("/").split("/")[-1] if "/" in link else title
            result["tracks"].append({
                "id": track_id,
                "title": title.strip(),
                "status": status_map.get(status_char, "unknown"),
                "link": link,
            })

        # Old table format fallback
        if not result["tracks"]:
            for match in re.finditer(
                r"^\|\s*(\S+)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|\s*(.+?)\s*\|",
                tracks_text, re.MULTILINE
            ):
                track_id, title, status_raw, created = match.groups()
                if track_id in ("ID", "----", "---"):
                    continue
                status = "unknown"
                if "Complete" in status_raw or "✅" in status_raw:
                    status = "complete"
                elif "In Progress" in status_raw or "🔄" in status_raw:
                    status = "in_progress"
                elif "Pending" in status_raw or "⏳" in status_raw:
                    status = "pending"
                elif "Abandoned" in status_raw or "❌" in status_raw:
                    status = "abandoned"
                result["tracks"].append({
                    "id": track_id,
                    "title": title.strip(),
                    "status": status,
                    "created": created.strip(),
                })

    # Scan track directories for detailed info
    tracks_dir = conductor_dir / "tracks"
    if tracks_dir.is_dir():
        for track_path in sorted(tracks_dir.iterdir()):
            if not track_path.is_dir():
                continue

            track_id = track_path.name

            # Find existing entry or create new one
            track_info = None
            for t in result["tracks"]:
                if t["id"] == track_id:
                    track_info = t
                    break
            if track_info is None:
                track_info = {"id": track_id, "status": "unknown"}
                result["tracks"].append(track_info)

            # Read metadata
            meta_file = track_path / "metadata.json"
            if meta_file.is_file():
                try:
                    meta = json.loads(meta_file.read_text())
                    if track_info.get("status") == "unknown":
                        track_info["status"] = meta.get("status", "unknown")
                    track_info["title"] = meta.get("title", meta.get("description", track_id))
                    track_info["type"] = meta.get("type", "unknown")
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

                # Also count sub-tasks (indented)
                sub_total = len(re.findall(r"^\s+- \[[ x~]\]", plan_text, re.MULTILINE))
                sub_done = len(re.findall(r"^\s+- \[x\]", plan_text, re.MULTILINE))

                track_info["tasks_total"] = total
                track_info["tasks_done"] = done
                track_info["tasks_in_progress"] = in_progress
                track_info["tasks_pending"] = pending
                track_info["subtasks_total"] = sub_total
                track_info["subtasks_done"] = sub_done

                # Count phases
                phases = re.findall(r"^## Phase \d+", plan_text, re.MULTILINE)
                checkpoints = re.findall(r"\[checkpoint:", plan_text)
                track_info["phases_total"] = len(phases)
                track_info["phases_complete"] = len(checkpoints)

                # Find next task
                track_info["next_task"] = None
                for line in plan_text.splitlines():
                    line_stripped = line.strip()
                    if line_stripped.startswith("- [~]"):
                        track_info["next_task"] = line_stripped[6:].strip()
                        break
                    elif line_stripped.startswith("- [ ]") and not track_info.get("next_task"):
                        track_info["next_task"] = line_stripped[6:].strip()

            # Set active track
            if track_info.get("status") in ("in_progress", "new") and not result["active_track"]:
                result["active_track"] = track_info

    # Set global next_task from active track
    if result["active_track"] and result["active_track"].get("next_task"):
        result["next_task"] = result["active_track"]["next_task"]

    return result


def main():
    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    result = detect_conductor(project_root)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
