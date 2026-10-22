# -*- coding: utf-8 -*-
"""外部權威連結健檢。

為什麼要有這支：2026-10-22 稽核時發現
https://www.fmcsa.dot.gov/regulations/title49/section/391.41 已經 404，
而它被 6 個頁面引用。外部連結是這個站 GEO 最強的一塊，但它會在我們
什麼都沒做的情況下腐爛——政府網站改版不會通知任何人。

刻意不放進 build.py：建置需要離線也能跑，而且 CI 因為外部網站暫時
抽風而失敗，只會讓人學會忽略紅燈。這支要手動跑，建議每季一次。

用法：python3 check_links.py [--live]
      預設檢查 dist/；--live 改抓線上版（才是真正要信的對象）。

注意 403 不等於死連結：fmcsa.dot.gov 會擋掉非瀏覽器的請求。腳本會
標成「需人工確認」而不是直接判死，人工用瀏覽器開一次才算數。
"""
import os, re, sys, collections, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

LIVE = "--live" in sys.argv
SITE = "https://carepluschiropractichealthcenter.com"
UA = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
      "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
      "Accept-Language": "en-US,en;q=0.9"}

def fetch(url, timeout=30, method="GET"):
    req = urllib.request.Request(url, headers=UA, method=method)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.status, r.geturl(), r.read(4096).decode("utf-8", "replace")

def collect_from_live():
    _, _, sm = fetch(SITE + "/sitemap.xml")
    # sitemap 可能超過 4096 bytes，重抓完整內容
    with urllib.request.urlopen(urllib.request.Request(SITE + "/sitemap.xml", headers=UA), timeout=30) as r:
        sm = r.read().decode("utf-8", "replace")
    urls = re.findall(r"<loc>(.*?)</loc>", sm)
    pages = {}
    def g(u):
        try:
            with urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=30) as r:
                return u, r.read().decode("utf-8", "replace")
        except Exception:
            return u, ""
    with ThreadPoolExecutor(max_workers=8) as ex:
        for u, h in ex.map(g, urls):
            pages[u[len(SITE):] or "/"] = h
    assert len(pages) == len(urls), f"抓取數不符 {len(pages)} != {len(urls)}"
    return pages

def collect_from_dist():
    pages = {}
    for dp, _, fs in os.walk("dist"):
        for f in fs:
            if f.endswith(".html"):
                rel = os.path.relpath(os.path.join(dp, f), "dist")
                pages[rel] = open(os.path.join(dp, f), encoding="utf-8", errors="replace").read()
    return pages

pages = collect_from_live() if LIVE else collect_from_dist()
print(f"來源：{'線上版' if LIVE else 'dist/'}　頁數 {len(pages)}")

links = collections.defaultdict(set)
for p, h in pages.items():
    for u in re.findall(r'href="(https?://[^"]+)"', h):
        if "carepluschiropractichealthcenter.com" in u:
            continue
        if "example.invalid" in u:          # 本機建置的佔位網域，不是真連結
            continue
        links[u].add(p)
print(f"外部連結去重 {len(links)} 個\n")

def check(u):
    try:
        code, final, body = fetch(u)
        # 有些站回 200 卻把你送到 404 頁
        looks404 = "/404" in final or re.search(r"<title[^>]*>[^<]*(404|not found)", body, re.I)
        return u, code, final, bool(looks404)
    except urllib.error.HTTPError as e:
        return u, e.code, u, False
    except Exception as e:
        return u, 0, str(e)[:60], False

with ThreadPoolExecutor(max_workers=6) as ex:
    res = list(ex.map(check, links))
assert len(res) == len(links), f"檢查數不符 {len(res)} != {len(links)}"
print(f"實際檢查 {len(res)} 個（應為 {len(links)}）\n")

dead  = [r for r in res if r[1] == 404 or r[3]]
manual= [r for r in res if r[1] in (401, 403, 429) or r[1] == 0]
ok    = [r for r in res if r not in dead and r not in manual]

print(f"✓ 正常                {len(ok)}")
print(f"✗ 死連結              {len(dead)}")
for u, c, f, _ in dead:
    print(f"    [{c}] {u}")
    print(f"         引用於 {len(links[u])} 頁：{sorted(links[u])[:4]}")
print(f"? 需人工用瀏覽器確認   {len(manual)}   （403/429 多半是擋機器人，不代表死）")
for u, c, f, _ in manual:
    print(f"    [{c}] {u}   （{len(links[u])} 頁）")

if dead:
    sys.exit(f"\n發現 {len(dead)} 個死連結，請修正後重新建置。")
print("\n✓ 無死連結")
