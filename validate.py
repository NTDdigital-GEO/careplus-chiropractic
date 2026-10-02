# -*- coding: utf-8 -*-
"""產出驗證：連結、H1、schema、title 唯一性、直答長度"""
import os,re,json,html,sys,glob
from collections import Counter
OUT="dist"; fails=[]; warns=[]
# 建置時若有子路徑（GitHub Pages 專案網站），檢查連結前要先把前綴拿掉
BASE = "/" + os.environ.get("BASE_PATH","").strip("/") if os.environ.get("BASE_PATH","").strip("/") else ""
def unbase(h):
    if BASE and h.startswith(BASE + "/"): return h[len(BASE):]
    if BASE and h == BASE: return "/"
    return h
if BASE: print(f"（子路徑模式：{BASE}）")

pages={}   # 正式頁面
devpages={}  # 審稿用（_pages），不納入 title/desc 唯一性等檢查
for f in glob.glob(OUT+"/**/index.html",recursive=True):
    rel=os.path.relpath(os.path.dirname(f),OUT)
    url="/" if rel=="." else "/"+rel.replace(os.sep,"/")+"/"
    (devpages if url.startswith("/_") else pages)[url]=open(f,encoding="utf-8").read()
print(f"正式頁面：{len(pages)}   審稿頁（不檢查）：{len(devpages)}")

# 審稿頁必須有 noindex，且不得出現在 sitemap
for u,s_ in devpages.items():
    if 'noindex' not in s_: fails.append(f"{u} 缺 noindex")
sm=open(os.path.join(OUT,"sitemap.xml"),encoding="utf-8").read()
for u in devpages:
    if u in sm: fails.append(f"{u} 不應出現在 sitemap")
print("✓ 審稿頁：有 noindex 且不在 sitemap" if not fails else "")

# 1) 內部連結是否都指向真實頁面
alllinks=Counter(); broken=[]
for url,s in pages.items():
    for href0 in set(re.findall(r'href="(/[^"#?]*)"',s)):
        href = unbase(href0)
        if href.startswith("/assets/"): continue
        alllinks[href]+=1
        if href not in pages and href not in devpages:
            p=os.path.join(OUT,href.strip("/"))
            if not (os.path.isfile(p) or os.path.isfile(p+"/index.html")):
                broken.append((url,href))
if broken:
    fails.append(f"{len(broken)} 個失效內部連結")
    for u,h in sorted(set(broken))[:20]: print(f"  ✗ {u} → {h}")
else: print("✓ 內部連結：全部指向真實頁面（0 個 404）")

# 2) 麵包屑父層是否存在
bc_bad=[]
for url,s in pages.items():
    m=re.search(r'<nav class="crumb".*?</nav>',s,re.S)
    if m:
        for href0 in re.findall(r'href="(/[^"]*)"',m.group()):
            href = unbase(href0)
            if href not in pages: bc_bad.append((url,href))
if bc_bad:
    fails.append("麵包屑指向不存在的頁面")
    for u,h in bc_bad[:10]: print(f"  ✗ 麵包屑 {u} → {h}")
else: print("✓ 麵包屑：所有父層都真實存在")

# 3) 單一 H1
bad=[u for u,s in pages.items() if len(re.findall(r'<h1[ >]',s))!=1]
if bad: fails.append(f"{len(bad)} 頁 H1 數量不是 1"); print("  ✗",bad[:5])
else: print("✓ H1：每頁剛好 1 個")

# 4) JSON-LD 可解析 + 必備節點
schema_bad=[]; faq_total=0
for u,s in pages.items():
    blocks=re.findall(r'<script type="application/ld\+json">(.*?)</script>',s,re.S)
    if len(blocks)!=1: schema_bad.append((u,"區塊數 %d"%len(blocks))); continue
    try: d=json.loads(blocks[0])
    except Exception as ex: schema_bad.append((u,f"解析失敗 {ex}")); continue
    types=[n.get("@type") for n in d["@graph"]]
    flat=[t for x in types for t in (x if isinstance(x,list) else [x])]
    if "WebPage" not in flat: schema_bad.append((u,"缺 WebPage"))
    if not any("Chiropractic"==t or "MedicalBusiness"==t for t in flat):
        schema_bad.append((u,"缺 MedicalBusiness"))
    for n in d["@graph"]:
        if n.get("@type")=="FAQPage": faq_total+=len(n["mainEntity"])
    bc=[n for n in d["@graph"] if n.get("@type")=="WebPage"][0].get("breadcrumb")
    if not bc: schema_bad.append((u,"缺 BreadcrumbList"))
if schema_bad:
    fails.append("schema 問題")
    for u,r in schema_bad[:10]: print(f"  ✗ {u}: {r}")
else: print(f"✓ Schema：{len(pages)} 頁全部可解析，含 WebPage/BreadcrumbList/MedicalBusiness；FAQ 共 {faq_total} 題")

# 5) title / description 唯一
for field,pat in [("title",r'<title>(.*?)</title>'),("description",r'<meta name="description" content="([^"]*)"')]:
    vals=[re.search(pat,s,re.S).group(1) for s in pages.values()]
    dup=[v for v,c in Counter(vals).items() if c>1]
    if dup: fails.append(f"{field} 重複"); print(f"  ✗ {field} 重複：{dup[:3]}")
    else: print(f"✓ {field}：{len(pages)} 頁全部唯一")

# 6) 直答段落長度（中文字元）
short=[]
for u,s in pages.items():
    m=re.search(r'<p class="answer">(.*?)</p>',s,re.S)
    t=re.sub(r'<[^>]+>','',m.group(1)).strip() if m else ""
    if u.startswith("/zh/") or u == "/zh/":
        n = len(re.findall(r'[一-鿿]', t)); lo, hi, unit = 40, 160, "中文字"
    else:
        n = len(t.split()); lo, hi, unit = 25, 95, "英文字"
    if n < lo or n > hi: short.append((u, f"{n} {unit}"))
if short: warns.append("直答段落長度需留意"); [print(f"  ! {u} 直答 {n}") for u,n in short[:8]]
else: print("✓ 直答段落：長度皆在合理範圍")

# 7) 外部資源（速度）
ext=set()
for s in pages.values():
    ext|=set(re.findall(r'<script[^>]+src="(https?://[^"]+)"',s))
    ext|=set(re.findall(r'<link[^>]+rel="stylesheet"[^>]*href="(https?://[^"]+)"',s))
    ext|=set(re.findall(r'<link[^>]+href="(https?://[^"]+)"[^>]*rel="stylesheet"',s))
print(f"✓ 外部阻塞資源：{len(ext)} 個" + (f" {sorted(ext)}" if ext else "（零 CDN，canonical/hreflang 不計）"))
if ext: fails.append("有外部阻塞資源")

# 8) frontlinks 覆蓋率
noext=[u for u,s in pages.items() if 'class="ext"' not in s]
print(f"✓ 外部引用：{len(pages)-len(noext)}/{len(pages)} 頁有 frontlink" + (f"；缺：{noext}" if noext else ""))

# 8b) 圖片：檔案存在、路徑不重複 BASE
BASE_V = os.environ.get("BASE_PATH","").strip("/")
imgrefs=set()
for u,s_ in pages.items():
    for m in re.finditer(r'src="([^"]*/assets/img/[^"]+)"', s_): imgrefs.add(m.group(1))
    for m in re.finditer(r'srcset="([^"]+)"', s_):
        for cand in m.group(1).split(","):
            c=cand.strip().split(" ")[0]
            if "/assets/img/" in c: imgrefs.add(c)
dupe=[u for u in imgrefs if BASE_V and u.count("/"+BASE_V+"/")>1]
missing=[]
for u in imgrefs:
    rel=u
    if BASE_V and rel.startswith("/"+BASE_V+"/"): rel=rel[len(BASE_V)+1:]
    if not os.path.exists(os.path.join(OUT, rel.lstrip("/"))): missing.append(u)
if dupe:
    print(f"✗ 圖片路徑重複了 BASE：{len(dupe)} 個"); [print("    "+u) for u in sorted(dupe)[:5]]
    fails.append("圖片路徑重複 BASE")
if missing:
    print(f"✗ 圖片檔不存在：{len(missing)} 個"); [print("    "+u) for u in sorted(missing)[:5]]
    fails.append("圖片檔不存在")
if imgrefs and not dupe and not missing:
    print(f"✓ 圖片：{len(imgrefs)} 個路徑全部存在且未重複 BASE")

# 8c) 內嵌 JS 必須能被解析
#     英文的成功訊息含有 We'll，曾經把手寫的單引號字串咬斷，
#     整段腳本語法錯誤、表單退回原生送出。本機沒有 node 時會跳過，
#     CI 的 runner 有，所以壞掉的腳本推不上去。
import shutil as _sh, subprocess as _sp, tempfile as _tf
if _sh.which("node"):
    jsbad = []
    for u, s_ in pages.items():
        for m in re.finditer(r'<script>(.*?)</script>', s_, re.S):
            code = m.group(1)
            with _tf.NamedTemporaryFile("w", suffix=".js", delete=False, encoding="utf-8") as fh:
                fh.write(code); tmp = fh.name
            r = _sp.run(["node", "--check", tmp], capture_output=True, text=True)
            os.unlink(tmp)
            if r.returncode != 0:
                first = (r.stderr.strip().splitlines() or [""])[-1][:110]
                jsbad.append((u, first))
                break
    if jsbad:
        print(f"✗ 內嵌 JS 有語法錯誤：{len(jsbad)} 頁")
        for u, e in jsbad[:5]: print(f"    {u}  {e}")
        fails.append("內嵌 JS 語法錯誤")
    else:
        print(f"✓ 內嵌 JS：{len(pages)} 頁全部可解析")
else:
    print("! 內嵌 JS 未檢查（本機沒有 node；CI 會檢查）")

# 9) 上線前把關：表單收件信箱必須已經換成客戶的
#    開發期間常先用內部信箱測試，這道檢查避免帶著暫用信箱上線。
#    確認換成客戶信箱後，在 workflow 加上 FORM_RECIPIENT_CONFIRMED=1 即可通過。
# 與 build.py 同一條規則：未設定視為 noindex，要公開必須明確 NOINDEX=0
live = os.environ.get("NOINDEX", "1") == "0"
has_key = bool(os.environ.get("FORM_ACCESS_KEY", "").strip())
confirmed = os.environ.get("FORM_RECIPIENT_CONFIRMED", "") == "1"
if live:
    if not has_key:
        print("✗ 正式站的表單沒有收件金鑰，送出會沒有人收到")
        fails.append("表單未設定 FORM_ACCESS_KEY")
    elif not confirmed:
        print("✗ 表單收件信箱尚未確認是客戶的")
        print("    開發期間可能先用了內部信箱。確認已換成診所的信箱後，")
        print("    在 deploy.yml 的建置步驟加上 FORM_RECIPIENT_CONFIRMED=1。")
        fails.append("表單收件信箱未確認")
    else:
        print("✓ 表單：已設定金鑰，且收件信箱已確認")
elif has_key:
    print("! 表單已設金鑰（目前 NOINDEX=1，未公開）"
          + ("" if confirmed else " — 收件信箱尚未確認是客戶的"))
    if not confirmed:
        warns.append("表單收件信箱待換成客戶的")
else:
    print("! 表單尚未接上收件信箱（目前 NOINDEX=1，送出不會真的寄出）")

print("\n"+("✗ 有 %d 類問題"%len(fails) if fails else "✓ 全部驗證通過")+(f"（{len(warns)} 項提醒）" if warns else ""))
sys.exit(1 if fails else 0)
