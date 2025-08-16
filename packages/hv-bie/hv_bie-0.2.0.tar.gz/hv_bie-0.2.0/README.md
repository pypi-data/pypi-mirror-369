# HV-BIE

HV Battle Intelligence Extractor parses a HentaiVerse battle HTML string into structured Python dataclasses.

- Python 3.13+
- Dependency: beautifulsoup4

## Public API

```python
from hv_bie import parse_snapshot
from hv_bie.types import BattleSnapshot

snap = parse_snapshot(html)
print(snap.player.hp_percent)
```

See [`SRS.md`](/SRS.md) for detailed requirements and data model.
