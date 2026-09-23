#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把整個網站包成「單一 HTML 檔」→ CarePlus-網站預覽.html

為什麼需要這個：
  macOS 會保護 ~/Documents、~/Desktop、~/Downloads。用 file:// 開網頁時，
  瀏覽器從一個檔案「跳到另一個檔案」會被系統擋下來（ERR_ACCESS_DENIED）。
  把 35 頁全部塞進同一個檔案，頁面切換只是在同一份文件裡換區塊，
  完全不會跨檔案讀取，所以不會觸發這個限制。

  → 產出一個檔案，雙擊就能逛完 35 頁。可以直接用 email 或微信傳給別人。

用法： python3 make_singlefile.py
"""
import os, re, glob, html as H

SRC = "dist"
OUT = "../CarePlus-網站預覽.html"

def slug_of(path):
    rel = os.path.relpath(os.path.dirname(path), SRC)
    return "/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/"

def main():
    if not os.path.isdir(SRC):
        print("找不到 dist/，請先執行 python3 build.py"); return

    css = open(os.path.join(SRC, "assets", "site.css"), encoding="utf-8").read()

    pages = {}
    for f in sorted(glob.glob(SRC + "/**/index.html", recursive=True)):
        sl = slug_of(f)
        if sl.startswith("/_"):      # 審稿目錄在單檔版用不到（上方已有下拉選單）
            continue
        pages[sl] = open(f, encoding="utf-8").read()
    for extra, name in (("404.html", "/404"), ("thanks.html", "/thanks")):
        p = os.path.join(SRC, extra)
        if os.path.isfile(p):
            pages[name] = open(p, encoding="utf-8").read()

    order = ["/", "/about/", "/about/dr-stewart-chen/", "/about/team/", "/contact/"]
    order += ["/services/"] + sorted(s for s in pages if s.startswith("/services/") and s != "/services/")
    order += ["/dot-physical/", "/dot-physical/checklist/", "/dot-physical/faq/"]
    order += ["/insurance/"] + sorted(s for s in pages if s.startswith("/insurance/") and s != "/insurance/")
    order += ["/pricing/", "/reviews/", "/media/", "/faq/", "/new-patient/"]
    order += [s for s in pages if s not in order]

    def page_id(s):
        return "p" + re.sub(r"[^a-z0-9]+", "-", s.strip("/").lower() or "home")

    blocks, titles = [], {}
    for s in order:
        if s not in pages: continue
        doc = pages[s]
        m = re.search(r"<body[^>]*>(.*)</body>", doc, re.S)
        body = m.group(1) if m else doc
        # 移除各頁自己的 script（合併後由外層統一處理）
        body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
        # 站內連結 → 改成同檔內的錨點
        def fix(mm):
            href = mm.group(1)
            if href.startswith("/assets/") or href.endswith((".xml", ".txt")):
                return 'href="#" data-noop="1"'
            if href in ("/404.html",): return 'href="#/404"'
            if href in ("/thanks.html",): return 'href="#/thanks"'
            return 'href="#%s"' % href
        body = re.sub(r'href="(/[^"]*)"', fix, body)
        t = re.search(r"<title>(.*?)</title>", doc, re.S)
        titles[s] = H.unescape(t.group(1)).split("｜")[0].strip() if t else s
        blocks.append(f'<div class="vpage" id="{page_id(s)}" data-slug="{H.escape(s)}" hidden>{body}</div>')

    nav = "".join(
        f'<option value="{H.escape(s)}">{H.escape(titles[s])} — {H.escape(s)}</option>'
        for s in order if s in pages)

    out = f"""<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>CarePlus 中文網站 · 完整預覽（單一檔案）</title>
<style>
{css}
/* ── 預覽模式專用 ── */
.vbar{{position:sticky;top:0;z-index:900;background:#14506e;color:#fff;
  padding:9px 0;font-size:14px;box-shadow:0 2px 10px rgba(0,0,0,.18)}}
.vbar .wrap{{display:flex;gap:12px;align-items:center;flex-wrap:wrap}}
.vbar b{{font-weight:700;letter-spacing:.04em;white-space:nowrap}}
.vbar select{{flex:1;min-width:230px;margin:0;padding:8px 11px;border-radius:8px;
  border:1px solid rgba(255,255,255,.35);background:#fff;color:#17171a;font-size:14.5px;
  font-family:inherit;max-width:520px}}
.vbar .vnav{{display:flex;gap:6px}}
.vbar button{{width:auto;padding:8px 14px;font-size:14px;border-radius:8px;
  background:rgba(255,255,255,.16);border:1px solid rgba(255,255,255,.3);color:#fff;font-weight:650}}
.vbar button:hover{{background:rgba(255,255,255,.28)}}
.vbar .pos{{font-size:13px;opacity:.85;white-space:nowrap}}
.vpage[hidden]{{display:none}}
.vpage header.top{{top:46px}}
/* 手機：控制項加大到好點的尺寸，並縮短高度 */
@media(max-width:700px){{
  .vbar{{padding:7px 0}}
  .vbar .wrap{{gap:8px}}
  .vbar b{{font-size:12.5px;letter-spacing:.02em}}
  .vbar .pos{{font-size:12px;order:3;margin-left:auto}}
  .vbar select{{flex:1 1 100%;order:4;min-height:46px;font-size:16px;padding:10px 12px;margin:0}}
  .vbar .vnav{{order:2;gap:8px}}
  .vbar button{{min-height:44px;min-width:92px;font-size:15px;padding:10px 14px}}
}}
@media(max-width:380px){{
  .vbar button{{min-width:0;flex:1;padding:10px 8px}}
  .vbar .vnav{{flex:1 1 auto}}
}}
</style>
</head>
<body>

<div class="vbar"><div class="wrap">
  <b>預覽模式</b>
  <select id="vsel" aria-label="選擇頁面">{nav}</select>
  <span class="vnav">
    <button id="vprev" type="button">← 上一頁</button>
    <button id="vnext" type="button">下一頁 →</button>
  </span>
  <span class="pos" id="vpos"></span>
</div></div>

{"".join(blocks)}

<script>
(function(){{
  var pages = Array.prototype.slice.call(document.querySelectorAll('.vpage'));
  var slugs = pages.map(function(p){{ return p.dataset.slug; }});
  var sel = document.getElementById('vsel');
  var pos = document.getElementById('vpos');

  function show(slug, push){{
    var i = slugs.indexOf(slug);
    if (i < 0) {{ i = 0; slug = slugs[0]; }}
    pages.forEach(function(p, n){{ p.hidden = (n !== i); }});
    sel.value = slug;
    pos.textContent = '第 ' + (i + 1) + ' / ' + pages.length + ' 頁';
    document.title = '預覽 · ' + (sel.options[sel.selectedIndex] ? sel.options[sel.selectedIndex].text : slug);
    window.scrollTo(0, 0);
    if (push && location.hash !== '#' + slug) {{
      history.replaceState(null, '', '#' + slug);
    }}
  }}

  function fromHash(){{
    var h = decodeURIComponent(location.hash.replace(/^#/, ''));
    show(h || '/', false);
  }}

  sel.addEventListener('change', function(){{ show(sel.value, true); }});
  document.getElementById('vprev').addEventListener('click', function(){{
    var i = slugs.indexOf(sel.value); show(slugs[(i - 1 + slugs.length) % slugs.length], true);
  }});
  document.getElementById('vnext').addEventListener('click', function(){{
    var i = slugs.indexOf(sel.value); show(slugs[(i + 1) % slugs.length], true);
  }});

  // 攔截站內連結，改成切換區塊（完全不跨檔案）
  document.addEventListener('click', function(e){{
    var a = e.target.closest ? e.target.closest('a') : null;
    if (!a) return;
    var href = a.getAttribute('href') || '';
    if (a.dataset.noop) {{ e.preventDefault(); return; }}
    if (href.charAt(0) !== '#') return;          // 外部連結、tel: 照常
    var slug = decodeURIComponent(href.slice(1));
    if (slug && slugs.indexOf(slug) >= 0) {{ e.preventDefault(); show(slug, true); }}
  }});

  // 表單在預覽模式不送出
  document.addEventListener('submit', function(e){{
    e.preventDefault();
    alert('這是預覽版，表單不會真的送出。\\n\\n正式上線後，送出的資料會寄到診所的信箱。');
  }});

  window.addEventListener('hashchange', fromHash);
  fromHash();
}})();
</script>
</body></html>"""

    with open(OUT, "w", encoding="utf-8") as f:
        f.write(out)
    kb = os.path.getsize(OUT) // 1024
    print(f"✓ 單一檔案完成：{os.path.basename(OUT)}  （{len(blocks)} 頁，{kb} KB）")
    print("  雙擊就能逛完全站，不會有 macOS 的檔案權限問題，也可以直接用 email 傳。")

if __name__ == "__main__":
    main()
