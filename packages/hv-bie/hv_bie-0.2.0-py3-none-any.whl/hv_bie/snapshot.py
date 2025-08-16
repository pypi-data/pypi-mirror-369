from __future__ import annotations

from bs4 import BeautifulSoup

from .types.models import BattleSnapshot
from .parsers.core import (
    parse_player_vitals,
    parse_player_buffs,
    parse_abilities,
    parse_monsters,
    parse_log,
    parse_items,
)


def parse_snapshot(html: str) -> BattleSnapshot:
    """Parse a HentaiVerse battle HTML string into a BattleSnapshot.
    This function never raises on missing sections; it fills defaults and records warnings.
    """
    soup = BeautifulSoup(html, "html.parser")
    warnings: list[str] = []

    player = parse_player_vitals(soup, warnings)
    player.buffs = parse_player_buffs(soup, warnings)

    abilities = parse_abilities(soup, warnings)
    monsters = parse_monsters(soup, warnings)
    clog = parse_log(soup, warnings)
    items = parse_items(soup, warnings)

    return BattleSnapshot(
        player=player,
        abilities=abilities,
        monsters=monsters,
        log=clog,
        items=items,
        warnings=warnings,
    )
