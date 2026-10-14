# -*- coding: utf-8 -*-
from .c_core import PAGES as _core
from .c_services_a import PAGES as _sa
from .c_services_b import PAGES as _sb
from .c_dot import PAGES as _dot
from .c_insurance import PAGES as _ins
from .c_trust import PAGES as _trust
from .en_core import PAGES as _en_core
from .en_services import PAGES as _en_svc
from .en_trust import PAGES as _en_trust

_ZH = _core + _sa + _sb + _dot + _ins + _trust
for _p in _ZH: _p.setdefault("lang", "zh")

_EN = _en_core + _en_svc + _en_trust
for _p in _EN: _p["lang"] = "en"

PAGES = _ZH + _EN

# 2026-10-14 暫時下架：客戶表示團隊成員多已離職，頁面上的姓名、年資與語言
# 不再正確。內容完整保留在 c_core.TEAM 與 en_core，等客戶要恢復時把 slug
# 從下面這個集合移除、並把內容更新成現職同仁即可。
# 下架同時也移除了所有指向它的站內連結（頁尾導覽、相關連結、FAQ）。
HIDDEN_SLUGS = {"about/team"}
PAGES = [_p for _p in PAGES if _p["slug"] not in HIDDEN_SLUGS]

# 完整性檢查：slug 不得重複，必要欄位不得缺漏
_seen = {}
for _p in PAGES:
    assert "slug" in _p, _p.get("h1")
    _key = (_p.get("lang", "zh"), _p["slug"])
    assert _key not in _seen, f"slug 重複：{_key}"
    _seen[_key] = _p["h1"]
    for _k in ("title","desc","h1","answer"):
        assert _p.get(_k), f"{_p['slug']} 缺少 {_k}"
