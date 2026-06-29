from ws.utils import sanitize_message


def test_sanitize_basic() -> None:
    assert sanitize_message("hello world") == "hello world"


def test_sanitize_html_escape() -> None:
    result = sanitize_message("<script>alert(1)</script>")
    assert "<" not in result
    assert ">" not in result
    assert "&lt;" in result


def test_sanitize_truncate() -> None:
    long_msg = "a" * 600
    result = sanitize_message(long_msg)
    assert len(result) <= 500


def test_sanitize_control_chars() -> None:
    result = sanitize_message("hello\x00world")
    assert "\x00" not in result
    assert result == "helloworld"


def test_sanitize_empty() -> None:
    assert sanitize_message("") == ""
    assert sanitize_message("   ") == ""
