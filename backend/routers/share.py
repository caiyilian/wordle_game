from __future__ import annotations

import io
from pathlib import Path
from typing import Any, Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import Response
from PIL import Image, ImageDraw, ImageFont
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from database import get_session
from models import GameRecord, PlayerGuess

router = APIRouter(prefix="/api", tags=["share"])

# ── constants ────────────────────────────────────────────────
CARD_W = 540
CARD_H = 720
MARGIN = 40
CELL_SIZE = 60
CELL_GAP = 8
GRID_COLS = 5  # default word length, may be overridden per game
COLOR_MAP = {
    "green": (106, 170, 100),
    "yellow": (201, 180, 88),
    "gray": (120, 124, 126),
    "bg": (18, 18, 19),
    "card": (30, 30, 32),
    "text": (255, 255, 255),
    "text_dim": (150, 150, 150),
}
FONT_DIR = Path(__file__).resolve().parents[1] / "resources" / "fonts"
FONT_PATH = FONT_DIR / "KarnakPro-Bold.ttf"


def _load_font(size: int) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    if FONT_PATH.exists():
        return ImageFont.truetype(str(FONT_PATH), size)
    return ImageFont.load_default()


def _draw_rounded_rect(
    draw: ImageDraw.ImageDraw,
    x: int, y: int, w: int, h: int, r: int,
    fill: tuple[int, int, int],
) -> None:
    draw.rounded_rectangle([x, y, x + w, y + h], radius=r, fill=fill)


def _build_color_grid(guesses: list[dict[str, Any]]) -> list[list[str]]:
    grid = []
    for g in guesses:
        colors: list[str] = g.get("colors", [])
        row = [c if c in ("green", "yellow", "gray") else "gray" for c in colors]
        grid.append(row)
    return grid


async def _resolve_game_data(
    game_id: str,
    session: AsyncSession,
) -> dict[str, Any]:
    result = await session.execute(select(GameRecord).where(GameRecord.id == game_id))
    game = result.scalar_one_or_none()
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")

    guesses_result = await session.execute(
        select(PlayerGuess)
        .where(PlayerGuess.game_id == game_id)
        .order_by(PlayerGuess.guess_number)
    )
    raw_guesses = guesses_result.scalars().all()

    guesses = [
        {
            "word": g.guess_word,
            "colors": g.colors,
            "number": g.guess_number,
        }
        for g in raw_guesses
    ]

    return {
        "answer_word": game.answer_word,
        "status": game.status,
        "word_length": game.word_length,
        "max_guesses": game.max_guesses,
        "guesses": guesses,
    }


def _render_card(data: dict[str, Any]) -> bytes:
    word_length = data["word_length"]
    answer = data["answer_word"]
    status = data["status"]
    max_g = data["max_guesses"]
    grid = _build_color_grid(data["guesses"])

    # Calculate dynamic card height based on grid rows
    rows_count = max(len(grid), 1)
    grid_top = 180
    grid_bot = grid_top + rows_count * (CELL_SIZE + CELL_GAP)
    card_h = max(grid_bot + 140, 400)

    img = Image.new("RGB", (CARD_W, card_h), COLOR_MAP["bg"])
    draw = ImageDraw.Draw(img)

    # Card background
    _draw_rounded_rect(draw, 20, 20, CARD_W - 40, card_h - 40, 16, COLOR_MAP["card"])

    # Title
    title_font = _load_font(36)
    title_text = "Wordle"
    _, _, tw, _ = draw.textbbox((0, 0), title_text, font=title_font)
    draw.text(
        ((CARD_W - tw) // 2, 60),
        title_text,
        font=title_font,
        fill=COLOR_MAP["text"],
    )

    # Result badge
    badge_color = COLOR_MAP["green"] if status == "win" else COLOR_MAP["gray"]
    badge_text = "Victory!" if status == "win" else "Game Over"
    badge_font = _load_font(20)
    bb = draw.textbbox((0, 0), badge_text, font=badge_font)
    bw = bb[2] - bb[0] + 40
    bh = bb[3] - bb[1] + 16
    bx = (CARD_W - bw) // 2
    _draw_rounded_rect(draw, bx, 110, bw, bh, 12, badge_color)
    draw.text(
        ((CARD_W - (bb[2] - bb[0])) // 2, 110 + (bh - (bb[3] - bb[1])) // 2 - 2),
        badge_text,
        font=badge_font,
        fill=COLOR_MAP["bg"],
    )

    # Grid
    cell_font = _load_font(28)
    grid_w = word_length * (CELL_SIZE + CELL_GAP) - CELL_GAP
    gx0 = (CARD_W - grid_w) // 2

    for row_idx, row in enumerate(grid):
        for col_idx, color_name in enumerate(row):
            x = gx0 + col_idx * (CELL_SIZE + CELL_GAP)
            y = grid_top + row_idx * (CELL_SIZE + CELL_GAP)
            fill = COLOR_MAP.get(color_name, COLOR_MAP["gray"])
            _draw_rounded_rect(draw, x, y, CELL_SIZE, CELL_SIZE, 8, fill)
            letter = row[col_idx] if len(row) > col_idx else ""
            if letter:
                lbox = draw.textbbox((0, 0), letter.upper(), font=cell_font)
                lw = lbox[2] - lbox[0]
                lh = lbox[3] - lbox[1]
                draw.text(
                    (x + (CELL_SIZE - lw) // 2, y + (CELL_SIZE - lh) // 2 - 2),
                    letter.upper(),
                    font=cell_font,
                    fill=COLOR_MAP["text"],
                )

    # Fill remaining rows if not all max_guesses used
    for empty_row in range(len(grid), max_g):
        y = grid_top + empty_row * (CELL_SIZE + CELL_GAP)
        for col_idx in range(word_length):
            x = gx0 + col_idx * (CELL_SIZE + CELL_GAP)
            _draw_rounded_rect(draw, x, y, CELL_SIZE, CELL_SIZE, 8, COLOR_MAP["gray"])

    # Answer word
    answer_font = _load_font(22)
    answer_text = f"Answer: {answer.upper()}"
    ab = draw.textbbox((0, 0), answer_text, font=answer_font)
    draw.text(
        ((CARD_W - (ab[2] - ab[0])) // 2, grid_bot + 20),
        answer_text,
        font=answer_font,
        fill=COLOR_MAP["text_dim"],
    )

    # Write to bytes
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


@router.post("/games/{game_id}/share-image")
async def share_image(
    game_id: str,
    session: AsyncSession = Depends(get_session),
) -> Response:
    data = await _resolve_game_data(game_id, session)
    png_bytes = _render_card(data)
    return Response(content=png_bytes, media_type="image/png")
