#!/usr/bin/env python3
"""
Export Estonian Word List Data from Ekilex Checkpoint
=====================================================

Reads the raw Ekilex API checkpoint (JSONL) and Hermit Dave frequency data,
then generates clean, documented TSV/TXT files for public use.

Usage:
    python3 scripts/export_from_checkpoint.py \
        --checkpoint /path/to/ekilex_checkpoint.jsonl \
        --frequency /path/to/hermit_dave_et_50k.txt \
        --output-dir data/

If arguments are omitted, the script looks for source files in the
AI-Assistant project at ~/Desktop/Development/AI-Assistant/scripts/data/.
"""

import argparse
import json
import sys
from collections import Counter
from pathlib import Path

# ---------------------------------------------------------------------------
# Defaults
# ---------------------------------------------------------------------------

DEFAULT_AI_ASSISTANT = Path.home() / "Desktop" / "Development" / "AI-Assistant"
DEFAULT_CHECKPOINT = DEFAULT_AI_ASSISTANT / "scripts" / "data" / "ekilex_checkpoint.jsonl"
DEFAULT_FREQUENCY = DEFAULT_AI_ASSISTANT / "scripts" / "data" / "hermit_dave_et_50k.txt"
SCRIPT_DIR = Path(__file__).resolve().parent
DEFAULT_OUTPUT = SCRIPT_DIR.parent / "data"

# Proficiency sort order (A1 = most basic/common → C1 = advanced)
PROFICIENCY_ORDER = {"A1": 1, "A2": 2, "B1": 3, "B2": 4, "C1": 5}

# POS code to English name mapping
POS_LABELS = {
    "s": "noun",
    "adj": "adjective",
    "v": "verb",
    "adv": "adverb",
    "prop": "proper noun",
    "pron": "pronoun",
    "konj": "conjunction",
    "num": "numeral",
    "interj": "interjection",
    "postp": "postposition",
    "prep": "preposition",
    "adjg": "adjective (genitive attribute)",
    "adjid": "adjective (plural only)",
    "vrm": "verb form",
}


# ---------------------------------------------------------------------------
# Loading
# ---------------------------------------------------------------------------


def load_checkpoint(path: Path) -> list[dict]:
    """Load Ekilex checkpoint JSONL into a list of entries."""
    entries = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            entries.append(json.loads(line))
    return entries


def load_frequency(path: Path) -> dict[str, tuple[int, int]]:
    """Load Hermit Dave frequency file.

    Returns dict mapping word -> (rank, corpus_count).
    Rank is assigned by descending corpus count (1 = most common).
    """
    raw = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            parts = line.strip().split()
            if len(parts) == 2:
                word, count = parts[0], int(parts[1])
                raw.append((word, count))

    # Sort by count descending to assign ranks
    raw.sort(key=lambda x: -x[1])
    freq = {}
    for rank, (word, count) in enumerate(raw, 1):
        freq[word] = (rank, count)
    return freq


# ---------------------------------------------------------------------------
# Export functions
# ---------------------------------------------------------------------------


def export_main_dataset(
    entries: list[dict],
    freq: dict[str, tuple[int, int]],
    output_dir: Path,
) -> list[dict]:
    """Export est_words_160k.tsv — the main enriched dataset.

    Sorted by: freq_rank (tier 1) → proficiency (tier 2) → alphabetical (tier 3).
    Returns the sorted entries for reuse.
    """
    # Deduplicate case-insensitively, keeping first occurrence
    seen = set()
    unique = []
    for entry in entries:
        low = entry["word"].lower()
        if low not in seen:
            seen.add(low)
            unique.append(entry)

    max_rank = len(freq) + 1

    def sort_key(e):
        word = e["word"].lower()
        rank = freq.get(word, (0, 0))[0]
        prof = e.get("proficiency") or ""
        prof_order = PROFICIENCY_ORDER.get(prof, 99)

        if rank > 0:
            # Tier 1: has frequency rank — sort by rank ascending
            return (0, rank, word)
        elif prof:
            # Tier 2: has proficiency but no frequency — sort by proficiency then alpha
            return (1, prof_order, word)
        else:
            # Tier 3: neither — alphabetical
            return (2, 0, word)

    unique.sort(key=sort_key)

    path = output_dir / "est_words_160k.tsv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("word\tfreq_rank\tproficiency\tpos\n")
        for e in unique:
            word = e["word"]
            rank = freq.get(word.lower(), (0, 0))[0]
            prof = e.get("proficiency") or ""
            pos = ",".join(e.get("pos", []))
            f.write(f"{word}\t{rank}\t{prof}\t{pos}\n")

    print(f"  est_words_160k.tsv: {len(unique):,} words")
    return unique


def export_inflected_forms(entries: list[dict], output_dir: Path):
    """Export est_inflected_forms.tsv — word + all inflected forms."""
    path = output_dir / "est_inflected_forms.tsv"
    count = 0
    total_forms = 0
    with open(path, "w", encoding="utf-8") as f:
        f.write("word\tforms\n")
        for e in entries:
            forms = e.get("inflected_forms", [])
            # Filter out placeholder dashes
            forms = [fm for fm in forms if fm and fm != "-"]
            if forms:
                f.write(f"{e['word']}\t{','.join(forms)}\n")
                count += 1
                total_forms += len(forms)

    print(f"  est_inflected_forms.tsv: {count:,} words, {total_forms:,} total forms")


def export_proficiency_words(entries: list[dict], output_dir: Path):
    """Export est_proficiency_words.tsv — only words with CEFR proficiency levels."""
    path = output_dir / "est_proficiency_words.tsv"
    count = 0
    with open(path, "w", encoding="utf-8") as f:
        f.write("word\tproficiency\tpos\n")
        for e in entries:
            prof = e.get("proficiency")
            if prof:
                pos = ",".join(e.get("pos", []))
                f.write(f"{e['word']}\t{prof}\t{pos}\n")
                count += 1

    print(f"  est_proficiency_words.tsv: {count:,} words")


def export_frequency_ranked(
    entries: list[dict],
    freq: dict[str, tuple[int, int]],
    output_dir: Path,
):
    """Export est_frequency_ranked.tsv — words with Hermit Dave frequency data."""
    # Build set of our words for intersection
    our_words = {e["word"].lower(): e["word"] for e in entries}

    matched = []
    for word_lower, (rank, count) in freq.items():
        if word_lower in our_words:
            matched.append((rank, our_words[word_lower], count))

    matched.sort()  # by rank ascending

    path = output_dir / "est_frequency_ranked.tsv"
    with open(path, "w", encoding="utf-8") as f:
        f.write("word\trank\tcorpus_count\n")
        for rank, word, count in matched:
            f.write(f"{word}\t{rank}\t{count}\n")

    print(f"  est_frequency_ranked.tsv: {len(matched):,} words")


def export_simple_wordlist(sorted_entries: list[dict], output_dir: Path):
    """Export est_words_simple.txt — plain word list, one per line."""
    path = output_dir / "est_words_simple.txt"
    with open(path, "w", encoding="utf-8") as f:
        for e in sorted_entries:
            f.write(e["word"] + "\n")

    print(f"  est_words_simple.txt: {len(sorted_entries):,} words")


# ---------------------------------------------------------------------------
# Stats
# ---------------------------------------------------------------------------


def print_stats(entries: list[dict], freq: dict[str, tuple[int, int]]):
    """Print summary statistics for the README."""
    total = len(entries)
    our_words_lower = {e["word"].lower() for e in entries}

    freq_matched = sum(1 for w in our_words_lower if w in freq)
    with_prof = sum(1 for e in entries if e.get("proficiency"))
    with_pos = sum(1 for e in entries if e.get("pos"))
    with_forms = sum(1 for e in entries if e.get("inflected_forms"))
    total_forms = sum(len(e.get("inflected_forms", [])) for e in entries)
    ekilex_found = sum(1 for e in entries if e.get("ekilex_found"))

    # Proficiency distribution
    prof_counts = Counter(e.get("proficiency") for e in entries if e.get("proficiency"))

    # POS distribution
    pos_counts = Counter()
    for e in entries:
        for p in e.get("pos", []):
            pos_counts[p] += 1

    print(f"\n{'='*60}")
    print(f"  Dataset Statistics")
    print(f"{'='*60}")
    print(f"  Total words:              {total:,}")
    print(f"  Found in Ekilex:          {ekilex_found:,}")
    print(f"  With frequency rank:      {freq_matched:,} ({100*freq_matched/total:.1f}%)")
    print(f"  With proficiency level:   {with_prof:,} ({100*with_prof/total:.1f}%)")
    print(f"  With POS tag:             {with_pos:,} ({100*with_pos/total:.1f}%)")
    print(f"  With inflected forms:     {with_forms:,} ({100*with_forms/total:.1f}%)")
    print(f"  Total inflected forms:    {total_forms:,}")
    print(f"  Avg forms/word:           {total_forms/max(with_forms,1):.1f}")
    print()
    print(f"  Proficiency distribution:")
    for level in ["A1", "A2", "B1", "B2", "C1"]:
        c = prof_counts.get(level, 0)
        print(f"    {level}: {c:,}")
    print()
    print(f"  POS distribution (top 10):")
    for pos, c in pos_counts.most_common(10):
        label = POS_LABELS.get(pos, pos)
        print(f"    {pos:>6} ({label}): {c:,}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Export Estonian word list data from Ekilex checkpoint"
    )
    parser.add_argument(
        "--checkpoint", type=Path, default=DEFAULT_CHECKPOINT,
        help="Path to ekilex_checkpoint.jsonl",
    )
    parser.add_argument(
        "--frequency", type=Path, default=DEFAULT_FREQUENCY,
        help="Path to hermit_dave_et_50k.txt",
    )
    parser.add_argument(
        "--output-dir", type=Path, default=DEFAULT_OUTPUT,
        help="Output directory for generated files",
    )
    args = parser.parse_args()

    # Validate inputs
    if not args.checkpoint.exists():
        print(f"ERROR: Checkpoint not found: {args.checkpoint}")
        sys.exit(1)
    if not args.frequency.exists():
        print(f"ERROR: Frequency file not found: {args.frequency}")
        sys.exit(1)

    args.output_dir.mkdir(parents=True, exist_ok=True)

    print("=== Estonian Word List Exporter ===")
    print(f"  Checkpoint: {args.checkpoint}")
    print(f"  Frequency:  {args.frequency}")
    print(f"  Output:     {args.output_dir}")

    # Load sources
    print("\nLoading checkpoint...")
    entries = load_checkpoint(args.checkpoint)
    print(f"  Loaded {len(entries):,} entries")

    print("Loading frequency data...")
    freq = load_frequency(args.frequency)
    print(f"  Loaded {len(freq):,} frequency entries")

    # Export all files
    print("\nExporting files:")
    sorted_entries = export_main_dataset(entries, freq, args.output_dir)
    export_inflected_forms(entries, args.output_dir)
    export_proficiency_words(entries, args.output_dir)
    export_frequency_ranked(entries, freq, args.output_dir)
    export_simple_wordlist(sorted_entries, args.output_dir)

    # Stats
    print_stats(entries, freq)

    print(f"\nDone! Files written to {args.output_dir}/")


if __name__ == "__main__":
    main()
