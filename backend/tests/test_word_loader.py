from core.word_loader import get_available_word_lengths, get_random_word, list_word_banks


def test_word_bank_index_loads_existing_resources() -> None:
    assert "CET4" in list_word_banks()
    assert 5 in get_available_word_lengths("CET4")


def test_get_random_word_returns_word_and_meaning() -> None:
    word, meaning = get_random_word("CET4", 5)

    assert len(word) == 5
    assert word.isalpha()
    assert meaning
