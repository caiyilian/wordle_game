import pytest

from core.wordle import evaluate_guess, is_valid_word


def test_evaluate_guess_all_green() -> None:
    assert evaluate_guess("apple", "apple") == ["green", "green", "green", "green", "green"]


def test_evaluate_guess_handles_mixed_colors() -> None:
    assert evaluate_guess("apple", "peach") == ["yellow", "yellow", "yellow", "gray", "gray"]


def test_evaluate_guess_handles_duplicate_letters() -> None:
    assert evaluate_guess("apple", "allee") == ["green", "yellow", "gray", "gray", "green"]


def test_evaluate_guess_requires_equal_lengths() -> None:
    with pytest.raises(ValueError):
        evaluate_guess("apple", "app")


def test_is_valid_word() -> None:
    assert is_valid_word("apple")
    assert not is_valid_word("zzzzznotaword")
