import json
import random
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

WordEntry = Tuple[str, str]
WordIndex = Dict[str, Dict[int, List[WordEntry]]]


def _candidate_words_dirs() -> List[Path]:
    backend_dir = Path(__file__).resolve().parents[1]
    project_dir = backend_dir.parent
    return [
        backend_dir / "resources" / "words",
        project_dir / "resources" / "words",
    ]


def _resolve_words_dir() -> Path:
    for words_dir in _candidate_words_dirs():
        if words_dir.exists():
            return words_dir
    raise FileNotFoundError("No resources/words directory was found.")


def _extract_meaning(raw_entry: Any) -> str:
    if isinstance(raw_entry, dict):
        value = raw_entry.get("\u4e2d\u91ca") or raw_entry.get("meaning") or raw_entry.get("translation")
        return str(value or "")
    return str(raw_entry)


def load_word_banks(words_dir: Optional[Path] = None) -> WordIndex:
    source_dir = words_dir or _resolve_words_dir()
    index: Dict[str, Dict[int, List[WordEntry]]] = defaultdict(lambda: defaultdict(list))

    for path in sorted(source_dir.glob("*.json")):
        with path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        if not isinstance(data, dict):
            continue

        for word, entry in data.items():
            normalized = str(word).strip().lower()
            if not normalized.isalpha():
                continue
            index[path.stem][len(normalized)].append((normalized, _extract_meaning(entry)))

    return {bank: dict(lengths) for bank, lengths in index.items()}


WORD_BANKS: WordIndex = load_word_banks()


def list_word_banks() -> List[str]:
    return sorted(WORD_BANKS)


def get_available_word_lengths(word_bank: Optional[str] = None) -> List[int]:
    if word_bank is not None:
        return sorted(WORD_BANKS.get(word_bank, {}))

    lengths = {length for words_by_length in WORD_BANKS.values() for length in words_by_length}
    return sorted(lengths)


def get_random_word(word_bank: str, length: int) -> WordEntry:
    words = WORD_BANKS.get(word_bank, {}).get(length, [])
    if not words:
        raise ValueError(f"No words found for bank {word_bank!r} with length {length}.")
    return random.choice(words)
