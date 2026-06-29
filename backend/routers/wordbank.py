from __future__ import annotations

from typing import Any, Dict, List

from fastapi import APIRouter, Depends, HTTPException, status

from core.word_loader import list_word_banks, get_available_word_lengths, WORD_BANKS

router = APIRouter(prefix="/api/wordbanks", tags=["wordbanks"])


def _build_wordbank_info() -> List[Dict[str, Any]]:
    result = []
    for bank in list_word_banks():
        lengths = WORD_BANKS.get(bank, {})
        length_counts = {}
        for length, words in lengths.items():
            length_counts[str(length)] = len(words)
        result.append({
            "name": bank,
            "lengths": length_counts,
        })
    return result


@router.get("", response_model=List[Dict[str, Any]])
def get_wordbanks() -> List[Dict[str, Any]]:
    return _build_wordbank_info()


@router.get("/info/{bank_name}", response_model=Dict[str, Any])
def get_wordbank_info(bank_name: str) -> Dict[str, Any]:
    banks = list_word_banks()
    if bank_name not in banks:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Word bank {bank_name} not found")
    lengths = WORD_BANKS.get(bank_name, {})
    length_counts = {}
    for length, words in lengths.items():
        length_counts[str(length)] = len(words)
    return {"name": bank_name, "lengths": length_counts}
