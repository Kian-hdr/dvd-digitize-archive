#!/usr/bin/env python3
"""Print the episode-first underscore filename used for optical archive outputs."""

import argparse
import re
import sys
import unicodedata


def safe_part(value):
    normalized = unicodedata.normalize("NFC", value.strip())
    part = re.sub(r"_+", "_", re.sub(r"[^\w]+", "_", normalized, flags=re.UNICODE)).strip("_")
    if not part:
        raise ValueError("a filename component is empty after sanitizing")
    return part


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="kind", required=True)
    episode = sub.add_parser("episode")
    episode.add_argument("--season", type=int, required=True)
    episode.add_argument("--episode", type=int, required=True)
    episode.add_argument("--end-episode", type=int, help="temporary multi-episode source only; never a final MP4")
    episode.add_argument("--title", required=True)
    episode.add_argument("--series", required=True)
    film = sub.add_parser("film")
    film.add_argument("--title", required=True)
    for item in (episode, film):
        item.add_argument("--year", type=int)
        item.add_argument("--variant", help="e.g. Surround or English")
        item.add_argument("--watch-order", type=int, help="positive in-universe ordinal for a flat TV playback view")
        item.add_argument("--ext", help="e.g. mkv, mp4, or srt; omit for stem only")
    args = parser.parse_args()

    try:
        if args.kind == "episode":
            if args.season < 0 or args.episode < 1:
                parser.error("season must be nonnegative and episode must be positive")
            if args.end_episode is not None and args.end_episode <= args.episode:
                parser.error("--end-episode must be greater than --episode")
            if args.end_episode is not None and args.ext and args.ext.lstrip(".").lower() == "mp4":
                parser.error("final MP4 files must contain one official episode; split this source")
            code = f"S{args.season:02d}E{args.episode:02d}"
            if args.end_episode is not None:
                code += f"-E{args.end_episode:02d}"
            parts = [code, safe_part(args.title), safe_part(args.series)]
        else:
            parts = [safe_part(args.title)]
        if args.year is not None:
            if not 1000 <= args.year <= 9999:
                parser.error("year must be four digits")
            parts.append(str(args.year))
        if args.variant:
            parts.append(safe_part(args.variant))
        stem = "_".join(parts)
        if args.watch_order is not None:
            if args.watch_order < 1:
                parser.error("--watch-order must be positive")
            stem = f"{args.watch_order:04d}_{stem}"
        if args.ext:
            extension = args.ext.lstrip(".")
            if not re.fullmatch(r"[A-Za-z0-9]{1,8}", extension):
                parser.error("extension must be 1-8 letters or digits")
            stem += "." + extension.lower()
        print(stem)
    except ValueError as error:
        parser.error(str(error))
    return 0


if __name__ == "__main__":
    sys.exit(main())
