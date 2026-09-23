#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""把 dist/ 轉成「雙擊就能看」的可攜版 → dist-portable/

為什麼需要這個：
  正式網站用絕對路徑（/assets/site.css、/services/…），上線後完全正確，
  但在自己電腦上雙擊開檔時，file:// 會把 / 解析成硬碟根目錄，樣式與連結全失效。
  這個腳本把它改成相對路徑並內嵌 CSS，讓不懂技術的同事可以直接點開來看。

  ⚠️ 可攜版只用來「看」與「審稿」，正式上線請用 dist/。

用法： python3 make_portable.py
"""
import os, re, shutil, glob

SRC, OUT = "dist", "dist-portable"

def depth_of(rel_dir):
    return 0 if rel_dir == "." else rel_dir.count(os.sep) + 1

def main():
    if not os.path.isdir(SRC):
        print("找不到 dist/，請先執行 python3 build.py"); return
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    shutil.copytree(SRC, OUT)

    css = open(os.path.join(SRC, "assets", "site.css"), encoding="utf-8").read()
    n = 0
    for f in glob.glob(OUT + "/**/*.html", recursive=True):
        rel_dir = os.path.relpath(os.path.dirname(f), OUT)
        up = "../" * depth_of(rel_dir)
        s = open(f, encoding="utf-8").read()

        # 1) CSS 直接內嵌，省掉一個外部請求，也不怕路徑錯
        s = s.replace('<link rel="stylesheet" href="/assets/site.css">',
                      "<style>\n" + css + "\n</style>")

        # 2) 站內連結改成相對路徑，並補上 index.html（file:// 不會自動找 index）
        def fix(m):
            href = m.group(1)
            if href.startswith("//") or href.startswith("/assets/"):
                return m.group(0)
            path = href.strip("/")
            target = (up + path + "/index.html") if path else (up + "index.html")
            if path.endswith(".html") or path.endswith(".xml") or path.endswith(".txt"):
                target = up + path
            return 'href="' + target.replace("//", "/") + '"'
        s = re.sub(r'href="(/[^"]*)"', fix, s)

        open(f, "w", encoding="utf-8").write(s)
        n += 1

    shutil.rmtree(os.path.join(OUT, "assets"), ignore_errors=True)
    for junk in ("sitemap.xml", "robots.txt"):
        p = os.path.join(OUT, junk)
        if os.path.isfile(p): os.remove(p)

    # 審稿目錄裡指向 sitemap/robots 的連結在離線版沒有意義，改成說明文字
    ip = os.path.join(OUT, "_pages", "index.html")
    if os.path.isfile(ip):
        s2 = open(ip, encoding="utf-8").read()
        s2 = re.sub(
            r'<div class="note ok"><div class="h">其他產出</div>.*?</div>',
            '<div class="note ok"><div class="h">離線預覽版</div>'
            '<p>這是可以雙擊開啟的離線版，用來審稿。'
            '<a href="../404.html">看 404 頁</a> · '
            '<a href="../thanks.html">看表單送出後的感謝頁</a><br>'
            'sitemap.xml 與 robots.txt 只在正式上線版才有作用，離線版已移除。</p></div>',
            s2, flags=re.S)
        open(ip, "w", encoding="utf-8").write(s2)

    # 放一個中文說明在最上層
    with open(os.path.join(OUT, "從這裡開始.html"), "w", encoding="utf-8") as fh:
        fh.write(f"""<!doctype html><html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>從這裡開始</title>
<style>{css}
body{{display:grid;place-items:center;min-height:100vh}}
.box{{max-width:640px;padding:40px 24px;text-align:center}}</style></head>
<body><div class="box">
<h1 style="max-width:none">CarePlus 中文網站・預覽版</h1>
<p class="answer" style="margin-inline:auto">這是離線預覽版，<strong>不用網路、不用安裝任何東西</strong>。
點下面的按鈕就可以像逛真的網站一樣，把 35 頁全部點過一遍。</p>
<div class="cta-row" style="justify-content:center;margin-bottom:34px">
<a class="btn btn-p" href="index.html">從首頁開始逛</a>
<a class="btn btn-s" href="_pages/index.html">看全部 35 頁的目錄</a></div>
<div class="note"><div class="h">給審稿的同事</div>
<p style="text-align:left">看到哪一句話要改，<strong>把頁面網址（瀏覽器上方那一行的最後一段）</strong>
和要改的句子記下來就好，例如「坐骨神經痛那一頁，第二段想改成…」。不需要自己動手改檔案。</p></div>
<p style="color:var(--ink-3);font-size:14px;margin-top:30px">
這是預覽版，網址列看起來會是一長串本機路徑，這是正常的。<br>
正式上線的版本網址會是 stewartchenchiro.com/services/sciatica/ 這種乾淨的樣子。</p>
</div></body></html>""")
    print(f"✓ 可攜版完成：{OUT}/  （{n} 個 HTML，CSS 已內嵌）")
    print(f"  → 雙擊 {OUT}/從這裡開始.html 即可瀏覽，不需要伺服器")

if __name__ == "__main__":
    main()
