from core.achievements import check_achievements, get_all_achievements


def test_first_win_unlocked() -> None:
    stats = {"wins": 1, "total_games": 1, "max_streak": 1, "guess_distribution": {"3": 1}}
    unlocked = check_achievements(stats)
    ids = [a["id"] for a in unlocked]
    assert "first_win" in ids


def test_first_win_not_unlocked() -> None:
    stats = {"wins": 0, "total_games": 0, "max_streak": 0, "guess_distribution": {}}
    unlocked = check_achievements(stats)
    ids = [a["id"] for a in unlocked]
    assert "first_win" not in ids


def test_perfect_guess_unlocked() -> None:
    stats = {"wins": 1, "guess_distribution": {"1": 1}}
    unlocked = check_achievements(stats)
    ids = [a["id"] for a in unlocked]
    assert "perfect_guess" in ids


def test_all_achievements_return_list() -> None:
    stats = {"wins": 0, "total_games": 0}
    all_achs = get_all_achievements(stats)
    assert isinstance(all_achs, list)
    assert len(all_achs) > 0
    for ach in all_achs:
        assert "id" in ach
        assert "unlocked" in ach
