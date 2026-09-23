#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""產出「可存成 PDF」的版本 → CarePlus-網站全文.html

為什麼需要：
  iPhone 打不開本機 HTML 檔（iOS 限制），微信也不會開 .html。
  但 PDF 在 iPhone 上原生就能開、能在微信傳、還能直接用 Markup 畫線標註。
  審稿的同事要做的是「讀文字、提意見」，PDF 比互動網頁更合適。

用法：
  python3 make_printable.py
  然後用 Chrome 打開產出的檔案 → Cmd+P → 目的地選「儲存為 PDF」→ 儲存
"""
import os, re, glob, html as H

SRC = "dist"
OUT = "../CarePlus-網站全文.html"

def slug_of(p):
    rel = os.path.relpath(os.path.dirname(p), SRC)
    return "/" if rel == "." else "/" + rel.replace(os.sep, "/") + "/"

def main():
    css = open(os.path.join(SRC, "assets", "site.css"), encoding="utf-8").read()

    pages = {}
    for f in sorted(glob.glob(SRC + "/**/index.html", recursive=True)):
        s = slug_of(f)
        if s.startswith("/_"): continue
        pages[s] = open(f, encoding="utf-8").read()

    order = ["/", "/about/", "/about/dr-stewart-chen/", "/about/team/", "/contact/"]
    order += ["/services/"] + sorted(x for x in pages if x.startswith("/services/") and x != "/services/")
    order += ["/dot-physical/", "/dot-physical/checklist/", "/dot-physical/faq/"]
    order += ["/insurance/"] + sorted(x for x in pages if x.startswith("/insurance/") and x != "/insurance/")
    order += ["/pricing/", "/reviews/", "/media/", "/faq/", "/new-patient/"]
    order += [x for x in pages if x not in order]

    blocks, toc = [], []
    n = 0
    for s in order:
        if s not in pages: continue
        n += 1
        doc = pages[s]
        body = re.search(r"<body[^>]*>(.*)</body>", doc, re.S).group(1)
        body = re.sub(r"<script.*?</script>", "", body, flags=re.S)
        body = re.sub(r"<header class=\"top\".*?</header>", "", body, flags=re.S)  # 每頁的固定頁首
        body = re.sub(r"<nav class=\"crumb\".*?</nav>", "", body, flags=re.S)
        body = re.sub(r"<footer>.*?</footer>", "", body, flags=re.S)              # 頁尾（每頁重複）
        body = re.sub(r'href="(/[^"]*)"', lambda m: 'href="#pg%s"' % re.sub(r"[^a-z0-9]+","-",m.group(1).strip("/") or "home"), body)
        h1 = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        title = H.unescape(re.sub(r"<[^>]+>", "", h1.group(1))).strip() if h1 else s
        pid = "pg" + re.sub(r"[^a-z0-9]+", "-", s.strip("/") or "home")
        toc.append(f'<li><a href="#{pid}"><span class="tn">{n:02d}</span>'
                   f'<span class="tt">{H.escape(title)}</span>'
                   f'<span class="tu">{H.escape(s)}</span></a></li>')
        blocks.append(
            f'<section class="pp" id="{pid}">'
            f'<div class="pp-h"><span class="pp-n">第 {n} / {len(pages)} 頁</span>'
            f'<span class="pp-u">{H.escape(s)}</span></div>{body}</section>')

    out = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>CarePlus 中文網站・全文（可存成 PDF）</title>
<style>
{css}
.cover{{padding:60px 0 40px;border-bottom:3px solid var(--ink);margin-bottom:40px}}
.cover h1{{max-width:none;font-size:38px;margin-bottom:14px}}
.cover p{{font-size:18px;color:var(--ink-2);max-width:60ch}}
.howto{{background:var(--brand-soft);border:1px solid var(--brand);border-left:6px solid var(--brand);
  border-radius:12px;padding:22px 26px;margin:28px 0}}
.howto .h{{font-weight:700;color:var(--brand);margin-bottom:8px;font-size:17px}}
.howto ol{{margin:0;padding-left:1.3em}}
.toc{{margin:0 0 50px}}
.toc h2{{font-size:20px;margin:0 0 16px;padding:0;border:none}}
.toc ol{{list-style:none;padding:0;margin:0;columns:2;column-gap:36px}}
@media(max-width:640px){{.toc ol{{columns:1}}}}
.toc li{{margin-bottom:7px;break-inside:avoid}}
.toc a{{display:flex;gap:10px;align-items:baseline;text-decoration:none;color:var(--ink);font-size:14.5px}}
.toc .tn{{font-family:ui-monospace,Menlo,monospace;color:var(--ink-3);font-size:12.5px;flex:none}}
.toc .tt{{font-weight:600}}
.toc .tu{{color:var(--ink-3);font-size:12px;font-family:ui-monospace,Menlo,monospace;margin-left:auto}}
.pp{{padding:0 0 46px;margin-bottom:46px;border-bottom:2px solid var(--line)}}
.pp-h{{display:flex;justify-content:space-between;gap:16px;align-items:baseline;
  background:var(--bg-2);border:1px solid var(--line);border-radius:9px;
  padding:9px 16px;margin-bottom:22px;font-size:13px;color:var(--ink-3)}}
.pp-n{{font-weight:700;color:var(--brand)}}
.pp-u{{font-family:ui-monospace,Menlo,monospace}}
.pp .phead{{background:none;border:none;padding:22px 0 10px}}
.pp section{{padding:26px 0;border:none;background:none!important}}
.pp .wrap{{padding:0;max-width:none}}
.pp .napbar{{margin:0;box-shadow:none}}
.pp details{{border-color:var(--line)}}
.pp details > summary{{list-style:none}}
.pp .formwrap{{display:none}}
@media print{{
  @page{{margin:14mm 12mm}}
  body{{font-size:11.5pt;line-height:1.7}}
  .noprint{{display:none!important}}
  .pp{{break-before:page;border-bottom:none;padding-bottom:0;margin-bottom:0}}
  .cover{{break-after:page}}
  .toc{{break-after:page}}
  h1{{font-size:22pt}} h2{{font-size:16pt;break-after:avoid}} h3{{font-size:13pt;break-after:avoid}}
  .pp-h{{background:#eef2f6!important;-webkit-print-color-adjust:exact;print-color-adjust:exact}}
  .route,.fact,.rev,.person,.price,.note,.band,.chip,table,details{{break-inside:avoid}}
  a{{text-decoration:none;color:inherit}}
  a.ext:after{{content:" ⟨" attr(href) "⟩";font-size:8pt;color:#666;word-break:break-all}}
  .cta-row,.openpill{{display:none}}
}}
</style></head>
<body>
<div class="wrap">

<div class="cover">
  <p class="eyebrow" style="font-size:12px;letter-spacing:.2em;text-transform:uppercase;color:var(--brand);font-weight:700;margin:0 0 16px">CarePlus 中文網站 · 全文審稿版</p>
  <h1>莊錦鎮脊椎治療中心<br>網站全文（{len(pages)} 頁）</h1>
  <p>這一份把整個網站的 {len(pages)} 頁文字依序排在一起，方便從頭讀到尾、標出要改的地方。
  版面與實際網站略有不同（拿掉了重複的頁首頁尾與表單），但<strong>文字內容完全一致</strong>。</p>
</div>

<div class="howto noprint">
  <div class="h">要存成 PDF 傳給別人？</div>
  <ol>
    <li>用 <strong>Chrome</strong> 打開這個檔案</li>
    <li>按 <strong>Cmd + P</strong>（Windows 是 Ctrl + P）</li>
    <li>「目的地」選 <strong>儲存為 PDF</strong></li>
    <li>建議勾選「背景圖形」，顏色才會保留</li>
    <li>按儲存 — 產出的 PDF 可以用微信傳，iPhone 直接就能開、也能畫線標註</li>
  </ol>
</div>

<div class="toc">
  <h2>目錄</h2>
  <ol>{"".join(toc)}</ol>
</div>

{"".join(blocks)}

<div style="padding:30px 0;color:var(--ink-3);font-size:13.5px;border-top:1px solid var(--line)">
NTD Digital · 莊錦鎮脊椎治療中心中文網站全文 · 共 {len(pages)} 頁<br>
看到要改的地方，請記下「頁碼／網址 ＋ 現在寫的那句話 ＋ 想改成什麼」，交給架站的同事。
</div>

</div></body></html>"""
    open(OUT, "w", encoding="utf-8").write(out)
    print(f"✓ 全文版完成：{os.path.basename(OUT)}  （{len(pages)} 頁，{os.path.getsize(OUT)//1024} KB）")
    print("  用 Chrome 開 → Cmd+P → 儲存為 PDF")

if __name__ == "__main__":
    main()
