from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Optional
import json


@dataclass
class Buff:
    name: str
    remaining_turns: Optional[float]
    is_permanent: bool


@dataclass
class Ability:
    name: str
    available: bool
    cost: int
    cost_type: Optional[str]
    cooldown_turns: int


@dataclass
class AbilitiesState:
    skills: dict[str, Ability] = field(default_factory=dict)
    spells: dict[str, Ability] = field(default_factory=dict)


@dataclass
class PlayerState:
    hp_percent: float = 0.0
    hp_value: int = 0
    mp_percent: float = 0.0
    mp_value: int = 0
    sp_percent: float = 0.0
    sp_value: int = 0
    overcharge_value: int = 0
    # Buffs keyed by buff name
    buffs: dict[str, Buff] = field(default_factory=dict)


@dataclass
class Monster:
    slot_index: int
    name: str
    alive: bool
    system_monster_type: Optional[str]
    hp_percent: float
    mp_percent: float
    sp_percent: float
    buffs: dict[str, Buff] = field(default_factory=dict)


@dataclass
class CombatLog:
    lines: list[str] = field(default_factory=list)
    current_round: Optional[int] = None
    total_round: Optional[int] = None


@dataclass
class Item:
    slot: str | int
    name: str
    available: bool


@dataclass
class QuickSlot:
    slot: str | int
    name: str


@dataclass
class ItemsState:
    items: dict[str, Item] = field(default_factory=dict)
    quickbar: list[QuickSlot] = field(default_factory=list)


@dataclass
class BattleSnapshot:
    player: PlayerState
    abilities: AbilitiesState
    monsters: dict[int, Monster]
    log: CombatLog
    items: ItemsState
    warnings: list[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return asdict(self)

    def to_json(self) -> str:
        return json.dumps(self.as_dict(), ensure_ascii=False)
