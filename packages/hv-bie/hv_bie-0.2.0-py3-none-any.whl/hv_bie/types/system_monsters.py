from __future__ import annotations

"""
系統怪物（System Monsters）名稱到稀有度類型的對照表。

使用方式：

    from hv_bie.types.system_monsters import get_system_monster_type
    rarity = get_system_monster_type(name)  # 回傳 'Rare' / 'Legendary' / 'Ultimate' 或 None

注意：
- 鍵為「怪物顯示名稱」，採不分大小寫比對（會先 .strip().casefold()）。
- 這裡先放範例占位名稱，請依實際需求填入正確清單。
"""

from typing import Optional, Literal

SystemMonsterType = Literal["Rare", "Legendary", "Ultimate"]


def _norm(name: str) -> str:
    return name.strip().casefold()


# 三個清單，直接維護名稱即可；字串大小寫不重要
RARE_NAMES: list[str] = [
    # 範例占位
    "Manbearpig",
    "White Bunneh",
    "Mithra",
    "Dalek",
]

LEGENDARY_NAMES: list[str] = [
    # 範例占位
    "Konata",
    "Mikuru Asahina",
    "Ryouko Asakura",
    "Yuki Nagato",
]

ULTIMATE_NAMES: list[str] = [
    # 範例占位
    "Skuld",
    "Urd",
    "Verdandi",
    "Yggdrasil",
    "Rhaegal",
    "Viserion",
    "Drogon",
    "Real Life",
    "Invisible Pink Unicorn",
    "Flying Spaghetti Monster",
]


# 由三個清單自動生成查詢用對照表（鍵以規範化小寫保存）
NAME_TO_TYPE: dict[str, SystemMonsterType] = {
    **{_norm(n): "Rare" for n in RARE_NAMES},
    **{_norm(n): "Legendary" for n in LEGENDARY_NAMES},
    **{_norm(n): "Ultimate" for n in ULTIMATE_NAMES},
}


def get_system_monster_type(name: str | None) -> Optional[SystemMonsterType]:
    """由怪物顯示名稱回傳其系統怪物稀有度類型。

    若找不到對應，回傳 None。
    """
    if not name:
        return None
    key = _norm(name)
    return NAME_TO_TYPE.get(key)


__all__ = [
    "SystemMonsterType",
    "RARE_NAMES",
    "LEGENDARY_NAMES",
    "ULTIMATE_NAMES",
    "NAME_TO_TYPE",
    "get_system_monster_type",
]
