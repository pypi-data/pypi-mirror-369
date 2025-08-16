from __future__ import annotations

import re
from typing import Optional
from bs4 import BeautifulSoup
from typing import Any

from ..types.models import (
    PlayerState,
    Buff,
    AbilitiesState,
    Ability,
    Monster,
    CombatLog,
    ItemsState,
    Item,
    QuickSlot,
)
from ..types.system_monsters import get_system_monster_type

# Constants inferred from fixtures
_PLAYER_BAR_FULL_PX = 414
_MONSTER_BAR_MAX_PX = 120
_OC_POINTS_PER_CHARGE = 25


def _safe_int(text: Optional[str]) -> int:
    try:
        return int(text.strip()) if text is not None else 0
    except Exception:
        return 0


def parse_player_vitals(soup: BeautifulSoup, warnings: list[str]) -> PlayerState:
    pane_el = soup.find("div", id="pane_vitals")
    hp_pct = mp_pct = sp_pct = 0.0
    hp_val = mp_val = sp_val = 0
    oc_val = 0
    if not (pane_el and hasattr(pane_el, "find")):
        warnings.append("pane_vitals not found")
        return PlayerState()
    pane: Any = pane_el

    def width_px(selector: str) -> Optional[int]:
        img = pane.find("img", src=re.compile(selector))
        if not img:
            return None
        m = re.search(r"width:(\d+)px", img.get("style", ""))
        return int(m.group(1)) if m else None

    hp_w = width_px(r"bar_[bd]green\.png")
    mp_w = width_px(r"bar_blue\.png")
    sp_w = width_px(r"bar_red\.png")
    oc_w = width_px(r"bar_orange\.png")

    if hp_w is not None:
        hp_pct = min(100.0, max(0.0, hp_w / _PLAYER_BAR_FULL_PX * 100))
    else:
        warnings.append("hp bar width missing")
    if mp_w is not None:
        mp_pct = min(100.0, max(0.0, mp_w / _PLAYER_BAR_FULL_PX * 100))
    else:
        warnings.append("mp bar width missing")
    if sp_w is not None:
        sp_pct = min(100.0, max(0.0, sp_w / _PLAYER_BAR_FULL_PX * 100))
    else:
        warnings.append("sp bar width missing")
    if oc_w is not None:
        # Fixtures show orange width mapped to 0..250 scale
        oc_val = int(round(oc_w / _PLAYER_BAR_FULL_PX * 250))

    dvrhd = pane.find("div", id="dvrhd")
    dvrm = pane.find("div", id="dvrm")
    dvrs = pane.find("div", id="dvrs")
    dvrc = pane.find("div", id="dvrc")
    hp_val = _safe_int(dvrhd.text if dvrhd and hasattr(dvrhd, "text") else None)
    mp_val = _safe_int(dvrm.text if dvrm and hasattr(dvrm, "text") else None)
    sp_val = _safe_int(dvrs.text if dvrs and hasattr(dvrs, "text") else None)
    if dvrc and hasattr(dvrc, "text"):
        oc_val = _safe_int(dvrc.text)
    elif oc_w is not None:
        oc_val = int(round(oc_w / _PLAYER_BAR_FULL_PX * 250))

    return PlayerState(
        hp_percent=hp_pct,
        hp_value=hp_val,
        mp_percent=mp_pct,
        mp_value=mp_val,
        sp_percent=sp_pct,
        sp_value=sp_val,
        overcharge_value=oc_val,
    )


_ICON_MAP = {
    # direct names from onmouseover examples
    "Regeneration": "Regeneration",
    "Regen": "Regen",
    "Absorbing Ward": "Absorbing Ward",
    "Hastened": "Haste",
    "Shadow Veil": "Shadow Veil",
    "Spark of Life": "Spark of Life",
    "Spirit Shield": "Spirit Shield",
    "Overwhelming Strikes": "Overwhelming Strikes",
    "Health Draught": "Regeneration",
    "Heartseeker": "Heartseeker",
}


def parse_player_buffs(soup: BeautifulSoup, warnings: list[str]) -> dict[str, Buff]:
    out: dict[str, Buff] = {}
    # Spirit stance is indicated by spirit_a.png on ckey_spirit
    spirit = soup.find("img", id="ckey_spirit")
    if (
        spirit
        and hasattr(spirit, "get")
        and "spirit_a.png" in (spirit.get("src") or "")
    ):
        out["Spirit Stance"] = Buff(
            name="Spirit Stance", remaining_turns=None, is_permanent=True
        )

    pane = soup.find("div", id="pane_effects")
    if not (pane and hasattr(pane, "find_all")):
        return out

    for img in pane.find_all("img"):
        om = img.get("onmouseover", "")
        m = re.search(
            r"set_infopane_effect\('([^']+)'\s*,\s*'[^']*'\s*,\s*([^\)]+)\)", om
        )
        if not m:
            continue
        name = m.group(1)
        dur_raw = m.group(2).strip().strip("'\"")
        is_perm = False
        rem: Optional[float] = None
        if dur_raw in ("autocast", "permanent"):
            is_perm = True
            rem = None
        else:
            try:
                rem = float(dur_raw)
            except ValueError:
                rem = None
        # normalize some names
        norm = _ICON_MAP.get(name, name)
        # About-to-expire opacity indicates ticking, but we keep numeric seconds as-is
        out[norm] = Buff(name=norm, remaining_turns=rem, is_permanent=is_perm)

    return out


def _parse_ability_div(div) -> Ability:
    name_div = div.find("div", class_="fc2 fal fcb")
    name = (
        name_div.find("div").get_text(strip=True)
        if name_div and name_div.find("div")
        else ""
    )
    available = "opacity:0.5" not in (div.get("style") or "")
    om = div.get("onmouseover", "")
    nums = [int(n) for n in re.findall(r"\b(\d+)\b", om)]
    cost = 0
    cd = 0
    cost_type: Optional[str] = None
    if len(nums) >= 3:
        # Heuristic from fixtures:
        # Spells: (mp_cost, 0, cooldown)
        # Skills: (0, overcharge_cost, cooldown)
        first, second, third = nums[-3:]
        if first > 0 and second == 0:
            cost = first
            cost_type = "MP"
        elif second > 0:
            cost = _OC_POINTS_PER_CHARGE * second
            cost_type = "Overcharge"
        cd = third
    return Ability(
        name=name,
        available=available,
        cost=cost,
        cost_type=cost_type,
        cooldown_turns=cd,
    )


def parse_abilities(soup: BeautifulSoup, warnings: list[str]) -> AbilitiesState:
    skills: dict[str, Ability] = {}
    spells: dict[str, Ability] = {}

    t_skills = soup.find("table", id="table_skills")
    if t_skills and hasattr(t_skills, "find_all"):
        for d in t_skills.find_all("div", class_="btsd"):
            ab = _parse_ability_div(d)
            if ab.name:
                skills[ab.name] = ab
    else:
        warnings.append("table_skills not found")

    t_magic = soup.find("table", id="table_magic")
    if t_magic and hasattr(t_magic, "find_all"):
        for d in t_magic.find_all("div", class_="btsd"):
            ab = _parse_ability_div(d)
            if ab.name:
                spells[ab.name] = ab
    else:
        warnings.append("table_magic not found")

    return AbilitiesState(skills=skills, spells=spells)


def parse_monsters(soup: BeautifulSoup, warnings: list[str]) -> dict[int, Monster]:
    pane = soup.find("div", id="pane_monster")
    if not (pane and hasattr(pane, "find_all")):
        warnings.append("pane_monster not found")
        return {}

    monsters: dict[int, Monster] = {}

    for mdiv in pane.find_all("div", id=re.compile(r"mkey_\d+")):
        m_id_m = re.search(r"mkey_(\d+)", mdiv.get("id", ""))
        idx = int(m_id_m.group(1)) if m_id_m else -1
        # System monster typing: prefer name-based mapping; fallback to style heuristic
        system_type: Optional[str] = None
        style = mdiv.get("style") or ""
        # name
        name_div = mdiv.find("div", class_="btm3")
        name = ""
        if name_div:
            title = name_div.find("div", class_="fc2 fal fcb")
            if title and title.find("div"):
                name = title.find("div").get_text(strip=True)
        # mapping by name (if available)
        system_type = get_system_monster_type(name)
        # fallback heuristic by styled border/background
        if system_type is None and ("border-color:" in style or "background:" in style):
            system_type = "Rare"

        # vitals: widths up to 120px
        def bar_pct(src_pat: str, alt: str | None = None) -> float:
            bars = mdiv.find_all("img", src=re.compile(src_pat))
            for bar in bars:
                if alt is None or bar.get("alt") == alt:
                    m = re.search(r"width:(\d+)px", bar.get("style", ""))
                    if m:
                        return max(
                            0.0,
                            min(100.0, int(m.group(1)) / _MONSTER_BAR_MAX_PX * 100.0),
                        )
            return 0.0

        dead = "opacity:0.3" in style
        hp = -1.0 if dead else bar_pct(r"nbargreen\.png", "health")
        mp = -1.0 if dead else bar_pct(r"nbarblue\.png", "magic")
        sp = -1.0 if dead else bar_pct(r"nbarred\.png", "spirit")

        # monster buffs
        m_buffs: dict[str, Buff] = {}
        bc = mdiv.find("div", class_="btm6")
        if bc:
            for img in bc.find_all("img"):
                om = img.get("onmouseover", "")
                mm = re.search(
                    r"set_infopane_effect\('([^']+)'\s*,\s*'[^']*'\s*,\s*([^\)]+)\)", om
                )
                if mm:
                    bname = mm.group(1)
                    dur_raw = mm.group(2).strip().strip("'\"")
                    is_perm = False
                    rem: Optional[float] = None
                    if dur_raw in ("autocast", "permanent"):
                        is_perm = True
                        rem = None
                    else:
                        try:
                            rem = float(dur_raw)
                        except ValueError:
                            rem = None
                    m_buffs[bname] = Buff(
                        name=bname, remaining_turns=rem, is_permanent=is_perm
                    )

        monsters[idx] = Monster(
            slot_index=idx,
            name=name,
            alive=(hp != -1.0),
            system_monster_type=system_type,
            hp_percent=hp if hp >= 0 else 0.0,
            mp_percent=mp if mp >= 0 else 0.0,
            sp_percent=sp if sp >= 0 else 0.0,
            buffs=m_buffs,
        )

    return monsters


def parse_log(soup: BeautifulSoup, warnings: list[str]) -> CombatLog:
    tbl = soup.find("table", id="textlog")
    lines: list[str] = []
    current: Optional[int] = None
    total: Optional[int] = None
    if tbl and hasattr(tbl, "find_all"):
        for td in tbl.find_all("td"):
            t = td.get_text(strip=True)
            if t:
                lines.append(t)
                m = re.search(r"Round\s+(\d+)\s*/\s*(\d+)", t)
                if m:
                    current = int(m.group(1))
                    total = int(m.group(2))
    else:
        warnings.append("textlog not found")
    return CombatLog(lines=lines[::-1], current_round=current, total_round=total)


def parse_items(soup: BeautifulSoup, warnings: list[str]) -> ItemsState:
    items: dict[str, Item] = {}
    quick: list[QuickSlot] = []

    pane_item = soup.find("div", id="pane_item")
    if pane_item and hasattr(pane_item, "find_all"):
        # Find all bti1 containers that contain items
        for bti_container in pane_item.find_all("div", class_="bti1"):
            # Get slot from bti2 div
            slot_div = bti_container.find("div", class_="bti2")
            slot_text = "unknown"
            if slot_div:
                slot_text = slot_div.get_text(strip=True).lower()

            # Look for item in bti3 div
            bti3 = bti_container.find("div", class_="bti3")
            if not bti3:
                continue

            # Check for available items (with onclick)
            available_item = bti3.find("div", onclick=True)
            if available_item:
                name_div = available_item.find("div", class_="fc2 fal fcb")
                if name_div and name_div.find("div"):
                    name = name_div.find("div").get_text(strip=True)
                    if name:
                        item = Item(
                            slot=(
                                slot_text if not slot_text.isdigit() else int(slot_text)
                            ),
                            name=name,
                            available=True,
                        )
                        items[name] = item
            else:
                # Check for unavailable items (with fcg class)
                unavailable_div = bti3.find("div", class_="fc2 fal fcg")
                if unavailable_div and unavailable_div.find("div"):
                    name = unavailable_div.find("div").get_text(strip=True)
                    if name:
                        item = Item(
                            slot=(
                                slot_text if not slot_text.isdigit() else int(slot_text)
                            ),
                            name=name,
                            available=False,
                        )
                        items[name] = item
    else:
        warnings.append("pane_item not found")

    quickbar = soup.find("div", id="quickbar")
    if quickbar and hasattr(quickbar, "find_all"):
        # In fixtures, quickbar has empty placeholders only; keep structure to future-fill if names become available
        idx = 1
        for _ in quickbar.find_all("div", class_="btqs"):
            quick.append(QuickSlot(slot=idx, name=""))
            idx += 1
    else:
        warnings.append("quickbar not found")

    return ItemsState(items=items, quickbar=quick)
