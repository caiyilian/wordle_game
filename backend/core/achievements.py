from typing import Any, Dict, List


ACHIEVEMENTS = [
    {"id": "first_win", "name": "First Win", "desc": "Win your first game", "condition": lambda s: s["wins"] >= 1},
    {"id": "perfect_guess", "name": "Perfect Guess", "desc": "Guess in one try", "condition": lambda s: "1" in s.get("guess_distribution", {}) and s.get("guess_distribution", {})["1"] >= 1},
    {"id": "streak_5", "name": "On Fire", "desc": "Win 5 in a row", "condition": lambda s: s.get("max_streak", 0) >= 5},
    {"id": "streak_10", "name": "Unstoppable", "desc": "Win 10 in a row", "condition": lambda s: s.get("max_streak", 0) >= 10},
    {"id": "shooter", "name": "Sharpshooter", "desc": "3 wins within 3 guesses", "condition": lambda s: s.get("wins", 0) >= 3 and "1" in s.get("guess_distribution", {}) and "2" in s.get("guess_distribution", {}) and "3" in s.get("guess_distribution", {})},
    {"id": "veteran", "name": "Veteran", "desc": "Play 50 games", "condition": lambda s: s.get("total_games", 0) >= 50},
    {"id": "half_century", "name": "Half Century", "desc": "Play 100 games", "condition": lambda s: s.get("total_games", 0) >= 100},
]


def check_achievements(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    unlocked = []
    for ach in ACHIEVEMENTS:
        try:
            if ach["condition"](stats):
                unlocked.append({
                    "id": ach["id"],
                    "name": ach["name"],
                    "desc": ach["desc"],
                    "unlocked": True,
                })
        except Exception:
            pass
    return unlocked


def get_all_achievements(stats: Dict[str, Any]) -> List[Dict[str, Any]]:
    unlocked_ids = {a["id"] for a in check_achievements(stats)}
    result = []
    for ach in ACHIEVEMENTS:
        result.append({
            "id": ach["id"],
            "name": ach["name"],
            "desc": ach["desc"],
            "unlocked": ach["id"] in unlocked_ids,
        })
    return result