# HV-BIE 軟體需求規格（SRS）

* **產品名稱：** HV Battle Intelligence Extractor（HV-BIE）
* **版本：** v0.3
* **依循標準：** 依循 ISO/IEC/IEEE 29148:2018 之結構與精神

---

## 1. 簡介

### 1.1 目的

本文件定義一個 Python 套件 **HV-BIE** 的需求，用於從 HentaiVerse 戰鬥頁面的 **HTML 原始碼字串** 中萃取結構化戰鬥資訊（玩家狀態、增益/減益、技能與法術清單、怪物清單與生命資源、戰鬥文字紀錄、道具/快捷列），並以穩定的程式介面提供給其他程式使用。

### 1.2 範圍

* **輸入**：戰鬥頁面的 **HTML 原始碼（`str`）**。
* **輸出**：**Python 資料類別**（主輸出），並提供**可選**序列化輔助（`as_dict()` / `to_json()`）。
* **交付**：可於 **PyPI** 發佈並安裝的第三方套件。
* **不包含**：任何對頁面的互動、自動點擊或登入流程；僅進行**唯讀解析**。

### 1.3 名詞

* **Vitals**：玩家的 HP / MP / SP / Overcharge 等資源。
* **Buff/Debuff**：顯示於頁面的狀態效果與剩餘時間。
* **技能/法術**：頁面上可選取的動作（例如近戰技能、治療/攻擊法術）。
* **戰報（Log）**：頁面上的戰鬥文字紀錄。
* **怪物（Monsters）**：本次戰鬥中出現的敵方單位清單。
* **系統怪物（System Monsters）**：HentaiVerse 中具有特殊標記或背景色的怪物，屬於系統生成的特殊敵人。依其稀有度，常見類型有 Rare、Legendary、Ultimate。更多資訊可參考 [EHWiki: System Monsters](https://ehwiki.org/wiki/System_Monsters)。

### 1.4 參考

* 提供之戰鬥頁面樣本檔（供理解介面與驗收測試資料）。
* 既有原型程式（僅供理解需求，不拘泥其內部設計）。

---

## 2. 利害關係人與使用者

### 2.1 利害關係人

* 需求提出者/開發者：希望穩定取得戰鬥資料供研究或工具整合。

### 2.2 使用者特性

* Python 使用者。**本 SRS 不預設**使用者熟悉 pandas、特定執行環境或 CLI/Notebook。

---

## 3. 產品觀

### 3.1 系統環境

* **執行環境**：Python **3.13+**。
* **相依第三方套件**：**beautifulsoup4（bs4）**。
* **輸入形式**：`html: str`。
* **輸出形式（主）**：Python **資料類別（dataclasses）**；提供 `as_dict()` / `to_json()` 作為**選配**序列化。

### 3.2 套件定位

* 作為 **Python 函式庫**（library）使用。
* 不含瀏覽器控制、爬蟲登入等能力。

---

## 4. 產品功能（高層「要什麼」）

> 下列功能描述以「使用者在頁面上能辨識的資訊」為準；具體解析策略（CSS 選擇器、像素轉換、字串剖析）屬設計文件範疇，不在本 SRS 綁定。

### F-1 取得玩家資源（Vitals）

* 能從 HTML 中判定並回傳：

  * **HP / MP / SP**：百分比（0–100，浮點數）與精確數值（整數）。
  * **Overcharge**：精確數值（整數）。
* 若頁面缺漏該資訊，需有可預期的預設值與警示（見 NFR）。

### F-2 取得玩家 Buff/Debuff

* 能列舉目前作用中的 Buff/Debuff 名稱與剩餘時間（如為持續性/永久顯示，須能以特別值表示，例如 `inf` 或 `None` 與旗標）。
* 名稱以頁面呈現的語意為準；允許設計一層可配置同義詞映射（屬實作細節，不在本 SRS 強制）。

### F-3 取得技能與法術清單

* 能列舉目前頁面顯示的技能與法術項目，包含：顯示名稱、是否可用、資源成本（若可由頁面資訊推知）、冷卻（若可由頁面資訊推知）。

### F-4 取得怪物清單與資源

* 能列舉所有敵方單位：**識別碼/位置**（例如第幾個怪物）、顯示名稱、是否存活、以及生命/魔力/精神等資源百分比（若頁面有呈現）。
* 必須能識別怪物是否為**系統怪物**，並（若可判斷）標記其類型（Rare/Legendary/Ultimate）。
* 可列出怪物端的 Buff（若頁面有顯示）。

### F-5 取得戰鬥文字紀錄（Log）

* 能擷取本頁面所顯示的戰鬥文字行，並能（若頁面有）辨識目前回合數與總回合數。

### F-6 取得道具/快捷列

* 能擷取頁面所顯示的道具（例如藥水）與快捷列項目（若頁面有顯示），包含顯示名稱與槽位資訊。

### F-7 快照一致性

* 提供單一呼叫以產生「**戰鬥快照**」，包含 F-1 \~ F-6 的彙整結果，以使同一份 HTML 產生內容一致的結構化資料。

---

## 5. 使用案例

### UC-1：以字串輸入解析單頁

**流程**：呼叫 `parse_snapshot(html: str)` → 取得 `BattleSnapshot` → 讀取屬性或選擇 `as_dict()`。
**結束條件**：得到包含玩家、怪物、技能/法術、戰報、道具的完整快照。

### UC-2：多頁批次處理（由上層自行迭代字串）

**流程**：外部自行迭代多個 HTML 字串，逐一呼叫解析函式並累積結果。
**非功能限制**：解析函式需具可重入性與可預期效能。

---

## 6. 功能性需求（可驗收）

| 編號   | 需求敘述                                       | 驗收準則（基於樣本 HTML）                       |
| ---- | ------------------------------------------ | ------------------------------------- |
| FR-1 | 可回傳玩家 HP/MP/SP 百分比與精確數值，以及 Overcharge 精確數值 | 值存在且型別正確；若缺漏則依 NFR 規定行為               |
| FR-2 | 可列舉玩家 Buff 名稱與剩餘時間/型態                      | 至少能解析出樣本頁面中可見的多個 Buff；永久/自動施放型態以規定值表示 |
| FR-3 | 可列舉技能與法術清單（含可用性、成本/冷卻若可得）                  | 核對樣本中至少各 3 項，欄位齊備                     |
| FR-4 | 可列舉所有怪物資訊（名稱、存活、資源百分比、系統怪物類型）              | 核對樣本中出現的全部怪物，包含系統怪物標記                 |
| FR-5 | 可擷取戰鬥文字行與回合資訊                              | 能回傳一組字串行列；若頁面顯示回合資訊則能解析               |
| FR-6 | 可擷取道具/快捷列                                  | 核對樣本頁中實際顯示的項目與槽位                      |
| FR-7 | 提供快照 API                                   | 一次呼叫取得完整結構（型別正確、鍵名穩定）                 |

---

## 7. 非功能性需求

### 7.1 效能

* **NFR-P1**：解析單一 HTML 字串產生快照的平均時間應足以支援互動式使用（具體數值由後續效能實測訂定，建議目標：在一般桌機上 ≲ 50ms）。

### 7.2 健壯性

* **NFR-R1**：當頁面缺漏預期元素時，不應丟出未捕捉例外；應以預設值/空集合回傳，並提供可記錄的**解析告警**。
* **NFR-R2**：Buff 名稱等可能變動的字面值允許經由**可選的配置映射**做統一化（此屬實作層，非強制）。

### 7.3 可維護性

* **NFR-M1**：解析策略與資料模型分離；資料模型鍵名與型別穩定。
* **NFR-M2**：提供單元測試與整合測試；至少涵蓋關鍵解析分支。

### 7.4 可攜性

* **NFR-T1**：支援 Python 3.13+，不限定作業系統。
* **NFR-T2**：不要求特定瀏覽器或自動化框架。

### 7.5 安全/合規

* **NFR-S1**：僅解析 HTML 字串，不對目標網站進行互動或請求。
* **NFR-S2**：避免執行 HTML 中的任何腳本內容。

### 7.6 可觀測性

* **NFR-O1**：可選：輸出解析摘要（來源長度、雜湊、耗時、警告數量）以利除錯。

---

## 8. 資料需求（資料模型）

> 以下為**主輸出**（Python 資料類別）的欄位結構草案；鍵名與型別在 SRS 中視為穩定契約。序列化為選配輔助。

* `BattleSnapshot`

  * `player: PlayerState`
  * `abilities: AbilitiesState`
  * `monsters: list[Monster]`
  * `log: CombatLog`
  * `items: ItemsState`
  * `warnings: list[str]`
  * `as_dict() -> dict` / `to_json() -> str`（**選配**）

* `PlayerState`

  * `hp_percent: float`
  * `hp_value: int`
  * `mp_percent: float`
  * `mp_value: int`
  * `sp_percent: float`
  * `sp_value: int`
  * `overcharge_value: int`
  * `buffs: list[Buff]`

* `Buff`

  * `name: str`
  * `remaining_seconds: float | None`
  * `is_permanent: bool`

* `AbilitiesState`

  * `skills: dict[str, Ability]`（以技能「顯示名稱」為鍵）
  * `spells: dict[str, Ability]`（以法術「顯示名稱」為鍵）

* `Ability`

  * `name: str`
  * `available: bool`
  * `cost: int`
  * `cost_type: str | None`
  * `cooldown_turns: float`

* `Monster`

  * `slot_index: int`
  * `name: str`
  * `alive: bool`
  * `system_monster_type: str | None`  # 例："Rare" / "Legendary" / "Ultimate"
  * `hp_percent: float`
  * `mp_percent: float`
  * `sp_percent: float`
  * `buffs: list[Buff]`

* `CombatLog`

  * `lines: list[str]`
  * `current_round: int | None`
  * `total_round: int | None`

* `ItemsState`

  * `items: dict[str, Item]`（以道具「顯示名稱」為鍵）
  * `quickbar: list[QuickSlot]`

* `Item`

  * `slot: str | int`
  * `name: str`
  * `available: bool`

* `QuickSlot`

  * `slot: str | int`
  * `name: str`

---

## 9. 介面需求（Public API）

最小穩定面：

```python
from hv_bie import parse_snapshot
from hv_bie.types import BattleSnapshot

def parse_snapshot(html: str) -> BattleSnapshot: ...
```

---

## 10. 限制與假設

* **A-1**：頁面中存在可讓人類辨識的資源條、狀態圖示與文字紀錄；本套件的目標是把**可見資訊**結構化。
* **A-2**：若頁面改版導致資訊呈現方式變動，屬實作層需更新解析策略；不影響本 SRS 所定義的**輸出資料意義**。
* **C-1**：不執行頁面腳本，不對頁面進行任何互動。

---

## 11. 驗證

* **單元測試**：對各區塊解析器（Vitals/Buffs/Abilities/Monsters/Log/Items）以樣本 HTML 建立測例。
* **整合測試**：對 `parse_snapshot` 產出的 `BattleSnapshot` 進行欄位完整性與型別檢查。
* **效能測試**：確認符合 NFR-P1。
* **穩定鍵名測試**：`as_dict()` 輸出的鍵名與階層需固定。

---

## 12. 追溯矩陣（片段）

| 需求   | 對應輸出欄位                                              | 測試                             |
| ---- | --------------------------------------------------- | ------------------------------ |
| FR-1 | `PlayerState.hp_* / mp_* / sp_* / overcharge_value` | `test_parse_vitals.py`         |
| FR-2 | `PlayerState.buffs[]`                               | `test_parse_buffs.py`          |
| FR-3 | `AbilitiesState.skills/spells (dict[str, Ability])` | `test_parse_abilities.py`      |
| FR-4 | `monsters[]`（含 system\_monster\_type）               | `test_parse_monsters.py`       |
| FR-5 | `CombatLog.*`                                       | `test_parse_log.py`            |
| FR-6 | `ItemsState.*`                                      | `test_parse_items.py`          |
| FR-7 | `BattleSnapshot`                                    | `test_snapshot_integration.py` |

---

## 13. 風險與緩解

* **DOM 改版** → 將解析規則集中管理與單元測試覆蓋。
* **字面值差異（名稱/圖示）** → 可選映射表統一名稱；未知值給出警告但不中斷。
* **效能** → 僅使用 bs4，避免不必要的相依。

---

## 14. 交付件

* **PyPI 套件**（`hv_bie`）：

  * `types/`：dataclasses 定義
  * `parsers/`：各區塊解析器
  * `__init__.py`：`parse_snapshot` 入口
  * `tests/`：單元/整合/效能
  * `pyproject.toml`、`README.md`、`CHANGELOG.md`
  * **本 SRS 文件（`SRS.md`）**：作為套件文件的一部分，隨發佈附帶

---

## 15. 驗收標準（摘要）

* 呼叫 `parse_snapshot(html)` 能回傳包含：

  * 玩家 vitals（HP/MP/SP 百分比與精確值、Overcharge 精確值）。
  * 至少 2 個怪物（名稱、存活、資源百分比、系統怪物類型）。
  * 技能與法術清單。
  * 戰鬥文字行與回合資訊（若存在）。
  * 道具與快捷列。
* 測試涵蓋率與效能達到 NFR 目標。
