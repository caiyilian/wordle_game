from __future__ import annotations

import asyncio
from pathlib import Path
import sys


sys.path.append(str(Path(__file__).resolve().parents[1]))

from database import init_database


async def main() -> None:
    await init_database()


if __name__ == "__main__":
    asyncio.run(main())
