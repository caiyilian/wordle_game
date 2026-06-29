from core.scoring import calculate_score, update_user_stats


def test_calculate_score_first_guess() -> None:
    score = calculate_score(1, 6, 5)
    assert score == 50  # 5 * 10 * 1.0


def test_calculate_score_last_guess() -> None:
    score = calculate_score(6, 6, 5)
    assert score >= 1  # Minimum score is 1


def test_calculate_score_middle() -> None:
    score = calculate_score(3, 6, 5)
    assert score > 0
    assert score < 50


def test_update_user_stats_win() -> None:
    stats = {}
    result = update_user_stats(stats, won=True, guesses_made=3, word_length=5)
    assert result["total_games"] == 1
    assert result["wins"] == 1
    assert result["current_streak"] == 1
    assert result["guess_distribution"]["3"] == 1


def test_update_user_stats_loss_resets_streak() -> None:
    stats = {"current_streak": 3, "max_streak": 3}
    result = update_user_stats(stats, won=False, guesses_made=5)
    assert result["current_streak"] == 0
    assert result["max_streak"] == 3
