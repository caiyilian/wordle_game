from typing import Any, Dict


def calculate_score(guesses_made: int, max_guesses: int, word_length: int = 5) -> int:
    """Calculate score for a completed game.
    
    Fewer guesses = higher score. Base score is proportional to word length.
    """
    if guesses_made <= 0:
        return 0
    ratio = 1.0 - (guesses_made - 1) / max(max_guesses - 1, 1)
    base = word_length * 10
    return max(1, int(base * ratio))


def update_user_stats(
    current_stats: Dict[str, Any],
    won: bool,
    guesses_made: int,
    word_length: int = 5,
) -> Dict[str, Any]:
    """Update user statistics after a game.
    
    Returns updated stats dict.
    """
    stats = dict(current_stats)
    
    total = stats.get("total_games", 0) + 1
    wins = stats.get("wins", 0) + (1 if won else 0)
    
    current_streak = stats.get("current_streak", 0)
    if won:
        current_streak += 1
    else:
        current_streak = 0
    
    max_streak = max(stats.get("max_streak", 0), current_streak)
    
    dist = dict(stats.get("guess_distribution", {}))
    key = str(guesses_made)
    dist[key] = dist.get(key, 0) + 1
    
    score = calculate_score(guesses_made, 6, word_length) if won else 0
    
    return {
        "total_games": total,
        "wins": wins,
        "current_streak": current_streak,
        "max_streak": max_streak,
        "guess_distribution": dist,
        "total_score": stats.get("total_score", 0) + score,
    }
