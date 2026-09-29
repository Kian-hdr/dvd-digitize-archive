#!/usr/bin/env python3
"""Build a numbered, storage-light MP4 view and plain-text guide from watch_order.json."""

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path

from media_filename import safe_part


def inside(path, root):
    return os.path.commonpath((str(path), str(root))) == str(root)


def load_plan(root):
    manifest = root / "watch_order.json"
    data = json.loads(manifest.read_text(encoding="utf-8"))
    if data.get("schema_version") != 1 or not isinstance(data.get("entries"), list):
        raise ValueError("watch_order.json must have schema_version 1 and entries list")
    proposed = data.get("planned_sequence", [])
    if not isinstance(proposed, list):
        raise ValueError("planned_sequence must be a list when present")
    proposed_ids = set()
    for item in proposed:
        if (not isinstance(item, dict) or not isinstance(item.get("id"), str) or not item["id"]
                or not isinstance(item.get("title"), str) or not item["title"]):
            raise ValueError("every planned sequence item needs an id and title")
        if item["id"] in proposed_ids:
            raise ValueError("planned sequence IDs must be unique")
        if not isinstance(item.get("evidence", []), list) or any(
                not isinstance(evidence, dict) for evidence in item.get("evidence", [])):
            raise ValueError(f"{item['id']}: evidence must be a list of records")
        proposed_ids.add(item["id"])
    seen = set()
    plan = []
    for ordinal, entry in enumerate(data["entries"], 1):
        if not isinstance(entry, dict):
            raise ValueError("every watch-order entry must be a record")
        identity = entry.get("id")
        if not identity or identity in seen:
            raise ValueError("every entry needs a unique stable id")
        seen.add(identity)
        status = entry.get("status")
        if status not in {"owned", "missing"}:
            raise ValueError(f"{identity}: status must be owned or missing")
        offers = entry.get("streaming_offers", [])
        if not isinstance(offers, list) or any(not isinstance(offer, dict) for offer in offers):
            raise ValueError(f"{identity}: streaming_offers must be a list of records")
        source = None
        if status == "owned":
            if entry.get("verified") is not True:
                raise ValueError(f"{identity}: owned MP4 is not verified")
            relative = entry.get("source_path")
            if not isinstance(relative, str) or not relative:
                raise ValueError(f"{identity}: source_path missing")
            source = (root / relative).resolve()
            if not inside(source, root) or not source.is_file() or source.suffix.lower() != ".mp4":
                raise ValueError(f"{identity}: source MP4 missing or outside workspace")
            name = f"{ordinal:04d}_{safe_part(source.stem)}.mp4"
        else:
            card = entry.get("card_path")
            if card:
                source = (root / card).resolve()
                if not inside(source, root) or not source.is_file() or source.suffix.lower() != ".mp4":
                    raise ValueError(f"{identity}: information card missing or outside workspace")
                name = f"{ordinal:04d}_{safe_part(source.stem)}.mp4"
            else:
                name = None
        plan.append((ordinal, entry, source, name))
    return data, plan


def guide(data, plan):
    lines = [data.get("title", "Watch order"),
             f"Continuity: {data.get('continuity', 'Unverified')}",
             f"Order basis: {data.get('order_basis', 'Not recorded')}",
             f"Missing works: {data.get('missing_titles_status', 'Not assessed')}",
             "Number prefixes are regenerated when titles are added; the IDs remain stable.",
             "Streaming availability is dated and region-specific. TV text viewing is unverified.", ""]
    if data.get("planned_sequence"):
        lines.append("Story plan for supplied discs (case labels and exact title maps require disc inspection):")
        for number, item in enumerate(data["planned_sequence"], 1):
            lines.append(f"{number:02d}. {item['title']} ({item['id']})")
            for field, label in (("placement", "Placement"), ("disc_to_inspect", "Disc to inspect"),
                                 ("qualification", "Qualification"), ("progress", "Progress")):
                if item.get(field):
                    lines.append(f"    {label}: {item[field]}")
            for evidence in item.get("evidence", []):
                if evidence.get("url"):
                    lines.append(f"    Evidence: {evidence['url']}")
        lines.append("")
    if not plan:
        lines.append("No verified episode or film MP4s in the numbered playback view yet.")
        lines.append("")
    for ordinal, entry, source, _name in plan:
        label = "OWNED MP4" if entry["status"] == "owned" else "MISSING"
        lines.append(f"{ordinal:04d}  [{label}] {entry.get('title', entry['id'])} ({entry['id']})")
        if source and entry["status"] == "owned":
            lines.append(f"      File: {source.name}")
        if entry.get("note"):
            lines.append(f"      Note: {entry['note']}")
        for offer in entry.get("streaming_offers", []):
            country = offer.get("country", "?")
            provider = offer.get("provider", "?")
            type_ = offer.get("type", "offer")
            checked = offer.get("checked_at", "date unknown")
            lines.append(f"      {country}: {provider} ({type_}; checked {checked})")
            if offer.get("url"):
                lines.append(f"      {offer['url']}")
    lines.extend(["", "Viewing offers are dated and region-specific; verify provider access for this account.", ""])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("workspace", type=Path)
    parser.add_argument("--run", action="store_true", help="build and promote candidate view; default previews")
    args = parser.parse_args()
    root = args.workspace.resolve()
    if not root.is_dir():
        parser.error("workspace not found")
    try:
        data, plan = load_plan(root)
        rendered_guide = guide(data, plan)
    except (OSError, ValueError, TypeError, AttributeError, KeyError, json.JSONDecodeError) as error:
        print(f"watch-order plan failed: {error}", file=sys.stderr)
        return 1
    names = [name for _, _, _, name in plan if name]
    if len(names) != len(set(names)):
        print("numbered filenames collide", file=sys.stderr)
        return 1
    print(f"{len(plan)} entries; {sum(e['status']=='owned' for _,e,_,_ in plan)} owned; "
          f"{sum(e['status']=='missing' for _,e,_,_ in plan)} missing; {len(names)} visible MP4s")
    if not args.run:
        print(rendered_guide)
        return 0

    stage = Path(tempfile.mkdtemp(prefix=".Watch_Order_candidate_", dir=root))
    target = root / "Watch_Order"
    previous = root / (".Watch_Order_previous_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"))
    guide_target = root / "WATCH_ORDER.txt"
    previous_guide = root / (".WATCH_ORDER_previous_" + datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ") + ".txt")
    temp_guide = None
    promoted = False
    try:
        for _ordinal, _entry, source, name in plan:
            if source and name:
                os.link(source, stage / name)
        if len(list(stage.iterdir())) != len(names):
            raise RuntimeError("candidate file count mismatch")
        if target.exists() or target.is_symlink():
            if (target.is_symlink() or not target.is_dir()
                    or previous.exists() or previous.is_symlink()):
                raise RuntimeError("existing watch view cannot be safely retained")
            os.rename(target, previous)
        os.rename(stage, target)
        promoted = True
        with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", prefix=".WATCH_ORDER.",
                                         dir=root, delete=False) as text_file:
            temp_guide = Path(text_file.name)
            text_file.write(rendered_guide)
            text_file.flush()
            os.fsync(text_file.fileno())
        if guide_target.exists() or guide_target.is_symlink():
            if (guide_target.is_symlink() or not guide_target.is_file()
                    or previous_guide.exists() or previous_guide.is_symlink()):
                raise RuntimeError("existing watch guide cannot be safely retained")
            os.rename(guide_target, previous_guide)
        os.replace(temp_guide, guide_target)
        temp_guide = None
        print(f"Built {target} and {guide_target}; prior view: {previous if previous.exists() else 'none'}; "
              f"prior guide: {previous_guide if previous_guide.exists() else 'none'}")
        return 0
    except (OSError, RuntimeError) as error:
        if temp_guide and temp_guide.exists():
            temp_guide.unlink()
        if previous_guide.exists():
            if guide_target.exists():
                guide_target.unlink()
            os.rename(previous_guide, guide_target)
        if stage.exists():
            shutil.rmtree(stage)
        if promoted and target.exists():
            shutil.rmtree(target)
        if previous.exists():
            os.rename(previous, target)
        print(f"watch-order build failed: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
