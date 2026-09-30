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

# 完整性檢查：slug 不得重複，必要欄位不得缺漏
_seen = {}
for _p in PAGES:
    assert "slug" in _p, _p.get("h1")
    _key = (_p.get("lang", "zh"), _p["slug"])
    assert _key not in _seen, f"slug 重複：{_key}"
    _seen[_key] = _p["h1"]
    for _k in ("title","desc","h1","answer"):
        assert _p.get(_k), f"{_p['slug']} 缺少 {_k}"
