from collections import Counter
from typing import List, Literal

from spellchecker import SpellChecker

from .word_loader import get_available_word_lengths, get_random_word

ColorResult = Literal["green", "yellow", "gray"]

_spell_checker = SpellChecker()


def evaluate_guess(answer: str, guess: str) -> List[ColorResult]:
    normalized_answer = answer.lower()
    normalized_guess = guess.lower()

    if len(normalized_answer) != len(normalized_guess):
        raise ValueError("answer and guess must have the same length")

    colors: List[ColorResult] = ["gray"] * len(normalized_answer)
    remaining_letters: Counter = Counter()

    for index, letter in enumerate(normalized_answer):
        if letter != normalized_guess[index]:
            remaining_letters[letter] += 1

    for index, letter in enumerate(normalized_guess):
        if letter == normalized_answer[index]:
            colors[index] = "green"
            remaining_letters[letter] -= 1

    for index, letter in enumerate(normalized_guess):
        if colors[index] == "green":
            continue
        if remaining_letters[letter] > 0:
            colors[index] = "yellow"
            remaining_letters[letter] -= 1
        else:
            colors[index] = "gray"

    return colors


def is_valid_word(word: str) -> bool:
    normalized = word.strip().lower()
    return bool(normalized.isalpha() and not _spell_checker.unknown([normalized]))
