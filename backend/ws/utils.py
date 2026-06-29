import html
import re


def sanitize_message(message: str, max_length: int = 500) -> str:
    """Sanitize chat message: escape HTML, truncate, strip control chars."""
    # Strip control characters (keep newline, tab)
    message = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', message)
    # Escape HTML entities
    message = html.escape(message)
    # Truncate
    if len(message) > max_length:
        message = message[:max_length]
    return message.strip()
