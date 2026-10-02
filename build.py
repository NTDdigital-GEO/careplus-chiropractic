#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
莊錦鎮脊椎治療中心 — 靜態網站產生器
用法：python3 build.py        → 產出到 dist/
設計原則（依 GEO 策略藍圖）：
  · 每頁單一 H1、40–60 字直答段落
  · 每頁都有 BreadcrumbList，且父層一定真實存在
  · 每頁 FAQ 都上 FAQPage schema
  · 引用分外部（.ext 紫）／內部（.int 橘）
  · 零外部 CDN、零阻塞資源
"""
import os, json, html, shutil, re, datetime

OUT = "dist"
# ── 可用環境變數覆寫，不改程式碼 ──
#   SITE_URL   完整網域，寫進 canonical / schema / sitemap
#   BASE_PATH  子路徑。GitHub Pages 專案網站要填 "/repo名稱"；自訂網域留空
# 預設一律 noindex。要公開必須明確設 NOINDEX=0——忘記設定的後果
# （整站被搜尋引擎收錄）比誤擋嚴重得多，所以預設值往安全的那邊倒。
NOINDEX = os.environ.get("NOINDEX", "1") != "0"

_SITE_FALLBACK = "https://example.invalid"
SITE = os.environ.get("SITE_URL", _SITE_FALLBACK).rstrip("/")
BASE = "/" + os.environ.get("BASE_PATH", "").strip("/") if os.environ.get("BASE_PATH", "").strip("/") else ""

# canonical、hreflang、og:url 與 sitemap 全都建立在 SITE 之上。沒設對的話，
# 這些標籤會把搜尋引擎指到別的網站去——曾經就指到 stewartchenchiro.com，
# 那是一個內容完全不同、而且對任何路徑都回首頁的舊站。
if SITE == _SITE_FALLBACK and not NOINDEX:
    raise SystemExit(
        "✗ 要產出可被索引的網站（NOINDEX=0），必須同時設定 SITE_URL。\n"
        "  否則 canonical／hreflang／og:url／sitemap 會指向錯誤的網域。\n"
        "  例：SITE_URL=https://www.carepluschiropractic.org NOINDEX=0 python3 build.py")

# Google Tag Manager 容器。GA4（G-G92YRT6DVC）設定在 GTM 容器「裡面」，
# 所以這裡只裝 GTM，不要再直接裝一次 GA4，否則流量會被重複計算。
# 本機測試若不想送資料，執行前加 GTM_ID="" 即可。
GTM_ID = os.environ.get("GTM_ID", "GTM-PFJXXHJN")

# 回電表單的收件服務（Web3Forms）。金鑰放環境變數，不進版本庫。
# 沒設定時表單會顯示提示且不送出，不會變成壞掉的 404。
FORM_KEY = os.environ.get("FORM_ACCESS_KEY", "").strip()
FORM_ENDPOINT = "https://api.web3forms.com/submit"

def gtm_head():
    if not GTM_ID: return ""
    return ("""<!-- Google Tag Manager -->
<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':
new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],
j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
})(window,document,'script','dataLayer','""" + GTM_ID + """');</script>
<!-- End Google Tag Manager -->""")

def gtm_body():
    if not GTM_ID: return ""
    return ('<!-- Google Tag Manager (noscript) -->\n'
            '<noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM_ID + '"\n'
            'height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
            '<!-- End Google Tag Manager (noscript) -->')
EN_SITE = "https://www.carepluschiropractic.org"
TODAY = "2026-09-21"

BIZ = dict(
    zh="莊錦鎮脊椎治療中心", en="CarePlus Chiropractic Health Center",
    street="212 9th Street, Suite 103", city="Oakland", region="CA", zip="94607",
    tel_display="510-465-7982", tel_href="5104657982", tel_e164="+1-510-465-7982",
    founded="1988", years="38",
    hours_zh="週一至週五 9:00–18:00 · 週六 9:00–12:00",
    bart="Lake Merritt BART 步行約 5 分鐘",
    langs="粵語・國語・台語・閩南話・English",
    rating="5.0", reviews="39", dot_price="95",
)

# ── 外部權威來源庫（frontlinks）──
SRC = {
 "fmcsa_reg":  ("ext","https://www.fmcsa.dot.gov/regulations/medical","FMCSA 體檢法規"),
 "fmcsa_reg2": ("ext","https://www.fmcsa.dot.gov/regulations/title49/section/391.41","FMCSA 49 CFR 391.41 體檢標準"),
 "fmcsa_reg3": ("ext","https://www.fmcsa.dot.gov/registration/commercial-drivers-license","FMCSA 商業駕照規定"),
 "fmcsa_nr":   ("ext","https://nationalregistry.fmcsa.dot.gov/","FMCSA 國家體檢醫師名冊"),
 "fmcsa_srch": ("ext","https://nationalregistry.fmcsa.dot.gov/search-medical-examiners","FMCSA 名冊・醫師查詢"),
 "chiro_ca":   ("ext","https://www.chiro.ca.gov/consumers/lic_lookup.shtml","加州脊骨神經醫學委員會・執照查詢"),
 "dca_search": ("ext","https://search.dca.ca.gov/","加州消費者事務部・執照查詢系統"),
 "dwc_main":   ("ext","https://www.dir.ca.gov/dwc/","加州勞工賠償局（DWC）"),
 "medicare_ch":("ext","https://www.medicare.gov/coverage/chiropractic-services","Medicare.gov · Chiropractic coverage"),
 "cdi_auto":   ("ext","https://www.insurance.ca.gov/01-consumers/105-type/95-guides/01-auto/","California Dept. of Insurance · Auto insurance guide"),
 "nccih_chiro":("ext","https://www.nccih.nih.gov/health/chiropractic-in-depth","NIH NCCIH · Chiropractic in depth"),
 "dwc_injured":("ext","https://www.dir.ca.gov/InjuredWorkerGuidebook/InjuredWorkerGuidebook.html","加州受傷勞工指南"),
 "aca":        ("ext","https://www.acatoday.org/","ACA 美國脊骨神經醫學會"),
 "nccih_back": ("ext","https://www.nccih.nih.gov/health/spinal-manipulation-what-you-need-to-know","NIH NCCIH・脊椎手法治療"),
 "nih_back":   ("ext","https://www.ninds.nih.gov/health-information/disorders/back-pain","NIH NINDS・下背痛"),
 "nih_sciatica":("ext","https://medlineplus.gov/sciatica.html","MedlinePlus・坐骨神經痛"),
 "nih_disc":   ("ext","https://medlineplus.gov/herniateddisk.html","MedlinePlus・椎間盤突出"),
 "nih_scoli":  ("ext","https://www.niams.nih.gov/health-topics/scoliosis","NIH NIAMS・脊椎側彎"),
 "nih_headache":("ext","https://www.ninds.nih.gov/health-information/disorders/headache","NIH NINDS・頭痛"),
 "nih_neck":   ("ext","https://medlineplus.gov/neckinjuriesanddisorders.html","MedlinePlus・頸部問題"),
 "nih_acu":    ("ext","https://www.nccih.nih.gov/health/acupuncture-what-you-need-to-know","NIH NCCIH・針灸"),
 "dmv_cdl":    ("ext","https://www.dmv.ca.gov/portal/driver-licenses-identification-cards/commercial-driver-licenses-cdl/","加州 DMV・商業駕照"),
 "medicare_ch":("ext","https://www.medicare.gov/coverage/chiropractic-services","Medicare・脊骨神經治療給付"),
 "ca_ins":     ("ext","https://www.insurance.ca.gov/01-consumers/105-type/9-auto/","加州保險廳・車險權益"),
 "palmer":     ("ext","https://www.palmer.edu/","Palmer College of Chiropractic"),
 "gbp":        ("ext","https://www.google.com/maps","Google 商家檔案評論"),
 "en_site":    ("ext", EN_SITE, "English Site"),
 "bart":       ("ext","https://www.bart.gov/stations/lake","BART・Lake Merritt 站資訊"),
 "actransit":  ("ext","https://www.actransit.org/","AC Transit 公車路線"),
}

# 頂部主導覽（每頁都會出現）
# ─────────────────── 雙語 ───────────────────
# 根目錄＝英文，/zh/＝中文。CURLANG 由 render() 設定，讓 blk()/src_line() 不必層層傳參數。
CURLANG = ["zh"]
# 哪些 slug 有哪個語言的版本，供 hreflang 與語言切換鈕配對；main() 建立。
HAVE = {"zh": set(), "en": set()}
LANGMARK = "%%LANGHREF%%"   # 語言切換鈕的網址不套用 /zh 前綴，用哨符避開

T = {
 "zh": dict(
   htmllang="zh-Hant", oglocale="zh_TW", name=BIZ["zh"], brandname=BIZ["zh"], other="English", otherlang="en",
   skip="跳到主要內容", nav="主選單", crumb="麵包屑", home="首頁",
   call="致電", callcta="致電預約", callback="請診所回電",
   hours=BIZ["hours_zh"], closed="週日休診",
   faq_eyebrow="常見問題", faq_h2="常見問題",
   rel_eyebrow="相關頁面", rel_h2="你可能也需要看這些",
   cta_eyebrow="回電預約", cta_h2="不方便現在打電話？留下時段，我們回電給您",
   cta_p="本中心採電話預約。若您現在不方便通話，填寫下方表單，我們會在門診時間內主動致電。",
   src_label="參考來源：",
   nap=("地址","交通","看診語言","電話"),
   nap_bart="Lake Merritt BART<br>步行約 5 分鐘",
   nap_langs="粵語・國語・台語<br>閩南話・English",
   disclaimer="本網站內容僅供一般健康資訊參考，不能取代專業醫療診斷或治療建議。個別狀況請親自到診評估。",
   footline="奧克蘭中國城執業 %s 年" % BIZ["years"],
   hoursline="營業時間：",
   nf_h="找不到這個頁面", nf_t="找不到頁面",
   nf_p="您要找的頁面可能已移除或網址有誤。需要預約或有任何問題，歡迎直接來電。",
   ty_t="已收到您的回電需求", ty_h="已收到，我們會主動致電",
   ty_p="感謝您的來信。我們會在門診時間內依您選擇的時段主動致電。若急需就診，也歡迎直接來電。",
   preview_alert="這是預覽版，表單還沒接上收件信箱，所以不會真的送出。\\n\\n正式上線後，送出的內容會寄到診所的信箱。\\n現在要預約請直接致電 510-465-7982。",
   f_sending="送出中…", f_btn="送出，請診所回電",
   f_ok="已收到，我們會在門診時間內主動致電。急需就診請直接撥 510-465-7982。",
   f_err="送出失敗，可能是網路問題。麻煩直接致電 510-465-7982，或稍後再試一次。",
   f_subject="網站回電需求（中文站）",
   preview_alert_inline="這是預覽版，表單還沒接上收件信箱，所以不會真的送出。要預約請直接致電 510-465-7982。",
 ),
 "en": dict(
   htmllang="en", oglocale="en_US", name=BIZ["en"], brandname="CarePlus Chiropractic", other="中文", otherlang="zh-Hant",
   skip="Skip to main content", nav="Main menu", crumb="Breadcrumb", home="Home",
   call="Call", callcta="Call to book", callback="Request a call back",
   hours="Mon–Fri 9:00–18:00 · Sat 9:00–12:00", closed="Closed Sunday",
   faq_eyebrow="FAQ", faq_h2="Frequently asked questions",
   rel_eyebrow="Related", rel_h2="You may also need these",
   cta_eyebrow="Request a call", cta_h2="Can't call right now? Leave a time and we'll call you",
   cta_p="We book by phone. If now isn't a good time, fill in the form below and we'll call you during clinic hours.",
   src_label="Sources: ",
   nap=("Address","Transit","Languages","Phone"),
   nap_bart="Lake Merritt BART<br>5-minute walk",
   nap_langs="Cantonese · Mandarin<br>Taiwanese · English",
   disclaimer="This site provides general health information only. It is not a substitute for professional diagnosis or treatment. Please come in for an assessment of your individual situation.",
   footline="%s years in Oakland Chinatown" % BIZ["years"],
   hoursline="Hours: ",
   nf_h="We can't find that page", nf_t="Page not found",
   nf_p="The page may have been moved or the address may be wrong. To book an appointment or ask a question, please call us.",
   ty_t="We've received your request", ty_h="Got it — we'll call you",
   ty_p="Thank you. We'll call you during clinic hours in the time slot you chose. If you need to be seen urgently, please call us directly.",
   preview_alert="This is a preview. The form is not connected to an inbox yet, so nothing is sent.\\n\\nOnce live, submissions will go to the clinic's email.\\nTo book now, please call 510-465-7982.",
   f_sending="Sending…", f_btn="Send — please call me back",
   f_ok="Received. We'll call you during clinic hours. If you need to be seen urgently, please call 510-465-7982.",
   f_err="Could not send — possibly a network problem. Please call 510-465-7982, or try again shortly.",
   f_subject="Website call-back request (English site)",
   preview_alert_inline="This is a preview — the form is not connected to an inbox yet, so nothing is sent. To book, please call 510-465-7982.",
 ),
}
def t(k): return T[CURLANG[0]][k]

def js(v):
    """把文字轉成安全的 JS 字面值。手動用引號包會被字串裡的單引號、
    反斜線或 </script> 咬到（英文的 We'll 就踩過一次），交給 json 處理。"""
    return json.dumps(str(v), ensure_ascii=False).replace("</", "<\\/")
def pfx(lg=None): return "/zh" if (lg or CURLANG[0]) == "zh" else ""

NAV_MAIN_ZH = [
    ("/services/",      "治療項目"),
    ("/dot-physical/",  "DOT 體檢"),
    ("/insurance/",     "費用與保險"),
    ("/about/",         "關於我們"),
    ("/faq/",           "常見問題"),
    ("/contact/",       "交通與預約"),
]
NAV_MAIN_EN = [
    ("/services/",      "Services"),
    ("/dot-physical/",  "DOT Physical"),
    ("/insurance/",     "Fees & Insurance"),
    ("/about/",         "About"),
    ("/faq/",           "FAQ"),
    ("/contact/",       "Visit Us"),
]
NAV_MAIN = {"zh": NAV_MAIN_ZH, "en": NAV_MAIN_EN}

NAV_FOOT_ZH = [
 ("治療項目", [("/services/auto-injury/","車禍受傷復健"),("/services/lower-back-pain/","腰背疼痛"),
   ("/services/neck-shoulder-pain/","頸肩疼痛"),("/services/sciatica/","坐骨神經痛"),
   ("/services/work-injury/","工傷評估與治療"),("/services/","全部服務項目")]),
 ("費用與保險", [("/insurance/auto-accident/","車禍理賠"),("/insurance/workers-comp/","工傷理賠"),
   ("/insurance/medicare/","Medicare"),("/insurance/self-pay/","自費價目"),
   ("/pricing/","價目總表"),("/dot-physical/","DOT 體檢 $95")]),
 ("關於我們", [("/","首頁"),("/about/dr-stewart-chen/","莊錦鎮醫師"),("/about/team/","醫療團隊"),
   ("/about/","中心介紹"),("/reviews/","病人評價"),("/media/","媒體報導"),
   ("/faq/","常見問題"),("/new-patient/","初診須知"),("/contact/","交通與停車")]),
]

NAV_FOOT_EN = [
 ("Services", [("/services/auto-injury/","Auto accident injury"),("/services/lower-back-pain/","Low back pain"),
   ("/services/neck-shoulder-pain/","Neck & shoulder pain"),("/services/sciatica/","Sciatica"),
   ("/services/work-injury/","Work injury"),("/services/","All services")]),
 ("Fees & Insurance", [("/insurance/auto-accident/","Auto accident claims"),("/insurance/workers-comp/","Workers' compensation"),
   ("/insurance/medicare/","Medicare"),("/insurance/self-pay/","Self-pay rates"),
   ("/pricing/","Full price list"),("/dot-physical/","DOT physical $95")]),
 ("About", [("/","Home"),("/about/dr-stewart-chen/","Dr. Stewart Chen"),("/about/team/","Our team"),
   ("/about/","About the clinic"),("/reviews/","Patient reviews"),("/media/","In the media"),
   ("/faq/","FAQ"),("/new-patient/","New patients"),("/contact/","Visit us")]),
]
NAV_FOOT = {"zh": NAV_FOOT_ZH, "en": NAV_FOOT_EN}

def e(s): return html.escape(str(s), quote=True)

def css_version():
    """用 CSS 內容算出短指紋。內容一改，網址就變，瀏覽器不會拿到舊快取。"""
    import hashlib
    try:
        with open(os.path.join("assets", "site.css"), "rb") as fh:
            return hashlib.sha1(fh.read()).hexdigest()[:8]
    except OSError:
        return "0"

CSSV = css_version()

def src_line(keys, label=None):
    label = label or T[CURLANG[0]]["src_label"]
    if not keys: return ""
    out = []
    for k in keys:
        if isinstance(k, tuple):
            kind, url, txt = k
        else:
            kind, url, txt = SRC[k]
        cls = "ext" if kind == "ext" else "int"
        rel = ' rel="noopener"' if kind == "ext" else ""
        out.append(f'<a class="{cls}" href="{e(url)}"{rel}>{e(txt)}</a>')
    return f'<div class="sources"><b>{e(label)}</b>{"".join(out)}</div>'

# ─────────────────── 圖片 ───────────────────
def _load_img_meta():
    fp = os.path.join("assets", "img", "_meta.json")
    if not os.path.exists(fp): return {}
    with open(fp, encoding="utf-8") as fh:
        return json.load(fh)
IMG = _load_img_meta()

def img_tag(slug, alt, sizes="(max-width:720px) 100vw, 640px", eager=False, cls="ph"):
    """輸出帶 srcset / 尺寸 / 延遲載入的 <img>。找不到圖就回空字串，不讓建置中斷。"""
    m = IMG.get(slug)
    if not m:
        return ""
    if not alt:
        raise ValueError("圖片 %s 缺少 alt 文字" % slug)
    # 不要在這裡加 BASE：apply_base() 會統一把 src="/… 改寫成子路徑，
    # 兩邊都加會變成 /repo/repo/assets/…
    srcset = ", ".join("/assets/img/%s-%d.jpg %dw" % (slug, w, w) for w in m["sizes"])
    src = "/assets/img/%s-%d.jpg" % (slug, m["sizes"][-1])
    load = 'loading="eager" fetchpriority="high"' if eager else 'loading="lazy"'
    return ('<img class="%s" src="%s" srcset="%s" sizes="%s" width="%d" height="%d" '
            'alt="%s" %s decoding="async">'
            % (cls, e(src), e(srcset), e(sizes), m["w"], m["h"], e(alt), load))

def figure_tag(slug, alt, caption=None, **kw):
    t = img_tag(slug, alt, **kw)
    if not t: return ""
    cap = '<figcaption>%s</figcaption>' % caption if caption else ""
    return '<figure class="ph-f">%s%s</figure>' % (t, cap)

# ─────────────────── 區塊渲染 ───────────────────
def blk(b):
    t = b["t"]
    head = ""
    if b.get("eyebrow") or b.get("h2"):
        head = '<div class="sechead">'
        if b.get("eyebrow"): head += f'<p class="eyebrow">{e(b["eyebrow"])}</p>'
        if b.get("h2"): head += f'<h2>{e(b["h2"])}</h2>'
        if b.get("lede"): head += f'<p>{b["lede"]}</p>'
        head += '</div>'
    body = ""

    if t == "prose":
        body = f'<div class="prose">{b["html"]}</div>'
    elif t == "steps":
        li = "".join(f'<li><span class="t">{e(x[0])}</span><span class="d">{x[1]}</span></li>' for x in b["items"])
        body = f'<ol class="steps">{li}</ol>'
    elif t == "checklist":
        cls = "checklist box" if b.get("box") else "checklist"
        li = "".join(f"<li>{x}</li>" for x in b["items"])
        body = f'<ul class="{cls}">{li}</ul>'
    elif t == "facts":
        c = "".join(
            f'<div class="fact{" gov" if x[3] else ""}"><div class="tag">{e(x[0])}</div>'
            f'<h3>{e(x[1])}</h3><p>{x[2]}</p></div>' for x in b["items"])
        body = f'<div class="factgrid">{c}</div>'
    elif t == "routes":
        c = "".join(
            f'<a class="route" href="{e(x[0])}"><h3>{e(x[1])}</h3><p>{x[2]}</p>'
            f'<span class="go">{e(x[3])}</span></a>' for x in b["items"])
        body = f'<div class="routes">{c}</div>'
    elif t == "price":
        li = "".join(f"<li>{x}</li>" for x in b["items"])
        extra = f'<p style="margin:0;font-size:15.5px;color:var(--ink-2)">{b["note"]}</p>' if b.get("note") else ""
        body = (f'<div class="price"><div><span class="amt">{e(b["amount"])}</span>'
                f'<span class="amtsub">{e(b.get("unit",""))}</span></div><ul>{li}</ul>{extra}'
                f'{src_line(b.get("sources"))}<p class="stamp">{b.get("stamp","")}</p></div>')
        return f'<section class="{b.get("bg","")}"><div class="wrap">{head}{body}</div></section>'
    elif t == "table":
        th = "".join(f"<th>{e(x)}</th>" for x in b["head"])
        tr = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in b["rows"])
        body = f'<div class="tw"><table><thead><tr>{th}</tr></thead><tbody>{tr}</tbody></table></div>'
    elif t == "note":
        k = b.get("kind", "")
        h = f'<div class="h">{e(b["h"])}</div>' if b.get("h") else ""
        body = f'<div class="note {k}">{h}{b["html"]}</div>'
    elif t == "equip":
        body = '<div class="equip">' + "".join(f'<span class="chip">{e(x)}</span>' for x in b["items"]) + "</div>"
    elif t == "people":
        c = "".join(f'<div class="person"><div class="role">{e(x[0])}</div><h3>{e(x[1])}</h3><p>{x[2]}</p></div>'
                    for x in b["items"])
        body = f'<div class="people">{c}</div>'
    elif t == "reviews":
        c = "".join(f'<div class="rev"><p>「{x[0]}」</p><div class="who">{e(x[1])}</div></div>' for x in b["items"])
        body = (f'<div class="revhead"><span class="revscore">{BIZ["rating"]}</span>'
                f'<span class="stars" aria-label="五顆星">★★★★★</span>'
                f'<span class="revmeta">{BIZ["reviews"]} 則 Google 評論 · '
                f'<a class="ext" href="https://www.google.com/maps" rel="noopener">在 Google 上查看全部</a></span></div>'
                f'<div class="revgrid">{c}</div>')
    elif t == "related":
        c = "".join(f'<a class="rel" href="{e(x[0])}">{e(x[1])}<span>{e(x[2])}</span></a>' for x in b["items"])
        body = f'<div class="related">{c}</div>'
    elif t == "photos":
        cols = b.get("cols", 0)
        doc  = " doc" if b.get("doc") else ""
        cls  = "phgrid" + (" cols-%d" % cols if cols else "") + doc
        n    = max(1, len(b["items"]))
        sizes = b.get("sizes") or ("(max-width:720px) 100vw, %dpx" % (1040 // min(n, 3)))
        cards = "".join(figure_tag(x[0], x[1], x[2] if len(x) > 2 else None, sizes=sizes)
                        for x in b["items"])
        body = '<div class="%s">%s</div>' % (cls, cards)
    elif t == "byline":
        t_ = img_tag("dr-chen", b.get("alt", "莊錦鎮醫師"), sizes="60px", cls="")
        body = ('<div class="byline">%s<div class="bt"><b>%s</b><span>%s</span></div></div>'
                % (t_, e(b.get("name", "莊錦鎮醫師 Dr. Stewart Chen, D.C.")), b.get("note", "")))
    elif t == "form":
        body = FORM[CURLANG[0]]
    elif t == "raw":
        body = b["html"]

    if b.get("sources") and t != "price":
        body += src_line(b["sources"])
    return f'<section class="{b.get("bg","")}"><div class="wrap">{head}{body}</div></section>'

FORM_ZH = f'''<form class="formwrap" id="cbForm" method="POST" action="{FORM_ENDPOINT}" novalidate>
<div style="position:absolute;left:-9999px" aria-hidden="true"><label>請勿填寫<input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label></div>
<input type="hidden" name="access_key" value="{FORM_KEY}">
<input type="hidden" name="subject" value="{T['zh']['f_subject']}">
<input type="hidden" name="from_name" value="{BIZ["en"]}">
<label for="n">稱呼 <span style="color:var(--accent)">*</span></label>
<input id="n" name="name" type="text" required autocomplete="name" placeholder="例：陳先生">
<label for="t">回電號碼 <span style="color:var(--accent)">*</span></label>
<input id="t" name="phone" type="tel" required autocomplete="tel" inputmode="tel" placeholder="510-000-0000">
<label for="r">想處理的問題</label>
<select id="r" name="reason"><option value="">請選擇（可略過）</option>
<option>車禍受傷</option><option>工傷</option><option>腰背・頸肩疼痛</option>
<option>坐骨神經痛・手腳麻木</option><option>DOT／CDL 商業司機體檢</option><option>針灸或推拿</option>
<option>其他／不確定</option></select>
<label for="w">方便接電話的時段</label>
<select id="w" name="best_time"><option>上午 9:00–12:00</option><option>下午 12:00–15:00</option>
<option>下午 15:00–18:00</option><option>都可以</option></select>
<label for="l">希望用哪種語言溝通</label>
<select id="l" name="language"><option>粵語</option><option>國語／普通話</option><option>台語／閩南話</option><option>English</option></select>
<button type="submit">送出，請診所回電</button>
<p class="formstatus" id="cbStatus" role="status" aria-live="polite" hidden></p>
<p class="formnote">我們只會用這個號碼與您聯繫預約事宜。<br>急需就診請直接致電 <a href="tel:{BIZ["tel_href"]}">{BIZ["tel_display"]}</a>。</p>
</form>'''

FORM_EN = f'''<form class="formwrap" id="cbForm" method="POST" action="{FORM_ENDPOINT}" novalidate>
<div style="position:absolute;left:-9999px" aria-hidden="true"><label>Leave blank<input type="checkbox" name="botcheck" tabindex="-1" autocomplete="off"></label></div>
<input type="hidden" name="access_key" value="{FORM_KEY}">
<input type="hidden" name="subject" value="{T['en']['f_subject']}">
<input type="hidden" name="from_name" value="{BIZ["en"]}">
<label for="n">Your name <span style="color:var(--accent)">*</span></label>
<input id="n" name="name" type="text" required autocomplete="name" placeholder="e.g. Mr. Chen">
<label for="t">Phone to call back <span style="color:var(--accent)">*</span></label>
<input id="t" name="phone" type="tel" required autocomplete="tel" inputmode="tel" placeholder="510-000-0000">
<label for="r">What would you like help with?</label>
<select id="r" name="reason"><option value="">Select (optional)</option>
<option>Auto accident injury</option><option>Work injury</option><option>Back, neck or shoulder pain</option>
<option>Sciatica / numbness or tingling</option><option>DOT / CDL driver physical</option><option>Acupuncture or massage therapy</option>
<option>Something else / not sure</option></select>
<label for="w">Best time to reach you</label>
<select id="w" name="best_time"><option>Morning 9:00–12:00</option><option>Early afternoon 12:00–15:00</option>
<option>Late afternoon 15:00–18:00</option><option>Any time</option></select>
<label for="l">Preferred language</label>
<select id="l" name="language"><option>English</option><option>Cantonese</option><option>Mandarin</option><option>Taiwanese</option></select>
<button type="submit">Send — please call me back</button>
<p class="formstatus" id="cbStatus" role="status" aria-live="polite" hidden></p>
<p class="formnote">We'll only use this number to arrange your appointment.<br>If you need to be seen urgently, please call <a href="tel:{BIZ["tel_href"]}">{BIZ["tel_display"]}</a>.</p>
</form>'''

FORM = {"zh": FORM_ZH, "en": FORM_EN}

# ─────────────────── Schema ───────────────────
def clinic_node():
    return {
      "@type": ["MedicalBusiness", "Chiropractic"],
      "@id": f"{SITE}/#clinic",
      "name": BIZ["en"], "alternateName": [BIZ["zh"], "Dr. Stewart Chen Chiropractic"],
      "url": SITE + "/", "telephone": BIZ["tel_e164"], "foundingDate": BIZ["founded"],
      "priceRange": "$$", "currenciesAccepted": "USD", "medicalSpecialty": "Chiropractic",
      "address": {"@type":"PostalAddress","streetAddress":BIZ["street"],"addressLocality":BIZ["city"],
                  "addressRegion":BIZ["region"],"postalCode":BIZ["zip"],"addressCountry":"US"},
      "geo": {"@type":"GeoCoordinates","latitude":37.7975,"longitude":-122.2715},
      "areaServed": [{"@type":"City","name":"Oakland"},{"@type":"City","name":"Alameda"},
                     {"@type":"City","name":"San Leandro"},
                     {"@type":"GeoShape","address":{"@type":"PostalAddress","postalCode":"94607",
                      "addressLocality":"Oakland Chinatown"}}],
      "availableLanguage":[{"@type":"Language","name":"Chinese (Cantonese)"},
                           {"@type":"Language","name":"Chinese (Mandarin)"},
                           {"@type":"Language","name":"Taiwanese Hokkien"},
                           {"@type":"Language","name":"English"}],
      "openingHoursSpecification":[
        {"@type":"OpeningHoursSpecification","dayOfWeek":["Monday","Tuesday","Wednesday","Thursday","Friday"],
         "opens":"09:00","closes":"18:00"},
        {"@type":"OpeningHoursSpecification","dayOfWeek":"Saturday","opens":"09:00","closes":"12:00"}],
      "sameAs":[EN_SITE+"/","https://www.yelp.com/biz/careplus-chiropractic-health-center-oakland",
                "https://www.youtube.com/@Dr.StewartChen"],
      "employee":{"@id":f"{SITE}/#drchen"},
    }

def physician_node(lg="zh"):
    # QME：2026-09-30 客戶確認證書已失效、服務已停止，全站不再輸出這項資格。
    return {
      "@type":"Physician","@id":f"{SITE}/#drchen","name":"Dr. Stewart Chen, D.C.",
      "alternateName":"莊錦鎮","medicalSpecialty":"Chiropractic",
      "url":f"{SITE}/about/dr-stewart-chen/","worksFor":{"@id":f"{SITE}/#clinic"},
      "knowsLanguage":["yue","cmn","nan","en"],
      "alumniOf":{"@type":"CollegeOrUniversity","name":"Palmer College of Chiropractic"},
      "hasCredential":[
        {"@type":"EducationalOccupationalCredential","credentialCategory":"Doctor of Chiropractic",
         "educationalLevel":"Doctorate","dateCreated":"1987",
         "recognizedBy":{"@type":"CollegeOrUniversity","name":"Palmer College of Chiropractic"}},
        {"@type":"EducationalOccupationalCredential","credentialCategory":"license",
         "name":"California Chiropractic License","identifier":"18759","validThrough":"2027-03-31",
         "recognizedBy":{"@type":"GovernmentOrganization",
           "name":"California Board of Chiropractic Examiners","url":"https://www.chiro.ca.gov/"}},
        ] + [
        {"@type":"EducationalOccupationalCredential","credentialCategory":"Certified Medical Examiner",
         "name":"FMCSA National Registry of Certified Medical Examiners",
         "identifier":"5497424313","dateCreated":"2019-07-22","validThrough":"2029-07-22",
         "recognizedBy":{"@type":"GovernmentOrganization",
           "name":"U.S. Department of Transportation, FMCSA National Registry",
           "url":"https://nationalregistry.fmcsa.dot.gov/"}}],
    }

def build_schema(p):
    url = SITE + "/" + (p["slug"] + "/" if p["slug"] else "")
    url = url.replace("//", "/").replace("https:/", "https://")
    g = []
    if p["slug"] == "":
        g.append(clinic_node()); g.append(physician_node(p.get("lang","zh")))
    else:
        g.append({"@type":["MedicalBusiness","Chiropractic"],"@id":f"{SITE}/#clinic",
                  "name":BIZ["en"],"alternateName":[BIZ["zh"]],"url":SITE+"/",
                  "telephone":BIZ["tel_e164"],
                  "address":{"@type":"PostalAddress","streetAddress":BIZ["street"],
                    "addressLocality":BIZ["city"],"addressRegion":BIZ["region"],
                    "postalCode":BIZ["zip"],"addressCountry":"US"}})
    if p.get("service"):
        s = {"@type": p["service"].get("type","Service"),
             "name": p["service"]["name"],
             "description": p["service"]["desc"],
             "provider": {"@id": f"{SITE}/#clinic"},
             "areaServed":[{"@type":"City","name":"Oakland"},
                           {"@type":"GeoShape","address":{"@type":"PostalAddress","postalCode":"94607",
                            "addressLocality":"Oakland Chinatown"}}]}
        if p["service"].get("offers"): s["offers"] = p["service"]["offers"]
        if p["service"].get("procedureType"): s["procedureType"] = p["service"]["procedureType"]
        g.append(s)
    if p.get("person_schema"): g.append(physician_node(p.get("lang","zh")))
    if p.get("faqs"):
        g.append({"@type":"FAQPage","@id":url+"#faq","mainEntity":[
            {"@type":"Question","name":q,
             "acceptedAnswer":{"@type":"Answer","text":re.sub(r'<[^>]+>','',a).strip()}}
            for q,a,_ in p["faqs"]]})
    if p["slug"] == "":
        g.append({"@type":"WebSite","@id":f"{SITE}/#website","url":SITE+"/",
                  "name":f'{BIZ["zh"]} {BIZ["en"]}',"inLanguage":"zh-Hant",
                  "publisher":{"@id":f"{SITE}/#clinic"}})
    crumbs = [("首頁","/")] + list(p.get("crumbs",[])) + [(p.get("crumb_self") or p["h1"], "/"+p["slug"]+"/" if p["slug"] else "/")]
    seen, cl = set(), []
    for n,u in crumbs:
        if u in seen: continue
        seen.add(u); cl.append((n,u))
    hero = p.get("hero")
    if hero and hero[0] in IMG:
        m = IMG[hero[0]]
        g.append({"@type":"ImageObject","@id":url+"#primaryimage",
                  "url":f"{SITE}/assets/img/{hero[0]}-{m['sizes'][-1]}.jpg",
                  "contentUrl":f"{SITE}/assets/img/{hero[0]}-{m['sizes'][-1]}.jpg",
                  "width":m["w"],"height":m["h"],"caption":hero[1]})
    _wp = {"@type":"WebPage","@id":url+"#webpage","url":url,"name":p["title"],
           "description":p["desc"],"inLanguage":"zh-Hant",
           "isPartOf":{"@id":f"{SITE}/#website"},"about":{"@id":f"{SITE}/#clinic"},
           "breadcrumb":{"@type":"BreadcrumbList","itemListElement":[
             {"@type":"ListItem","position":i+1,"name":n,"item":SITE+u}
             for i,(n,u) in enumerate(cl)]}}
    if hero and hero[0] in IMG:
        _wp["primaryImageOfPage"] = {"@id": url + "#primaryimage"}
    g.append(_wp)
    return json.dumps({"@context":"https://schema.org","@graph":g}, ensure_ascii=False, indent=1)

# ─────────────────── 頁面組裝 ───────────────────
def render(p):
    lg = p.get("lang", "zh")
    CURLANG[0] = lg
    P = pfx(lg)                      # 中文頁在 /zh 底下，英文頁在根目錄
    slug = p["slug"]
    url = SITE + P + "/" + (slug + "/" if slug else "")
    depth_prefix = "/"
    crumb_items = [(t("home"), "/")] + list(p.get("crumbs", []))
    crumb_html = "".join(f'<a href="{e(u)}">{e(n)}</a><span>›</span>' for n,u in crumb_items)
    crumb_html += f'<strong style="color:var(--ink-2);font-weight:600">{e(p.get("crumb_self") or p["h1"])}</strong>'

    hero = p.get("hero")
    hero_html = ""
    if hero:
        hero_html = '<div class="hero-img">%s</div>' % img_tag(
            hero[0], hero[1], sizes="(max-width:1080px) 100vw, 1040px", eager=True)

    faq_html = ""
    if p.get("faqs"):
        items = ""
        for i,(q,a,s) in enumerate(p["faqs"]):
            op = " open" if i == 0 else ""
            items += (f'<details{op}><summary>{e(q)}</summary><div class="fa">{a}'
                      f'{src_line(s) if s else ""}</div></details>')
        faq_html = (f'<section class="{p.get("faq_bg","")}"><div class="wrap">'
                    f'<div class="sechead"><p class="eyebrow">{e(t("faq_eyebrow"))}</p>'
                    f'<h2>{e(p.get("faq_h2") or t("faq_h2"))}</h2></div>'
                    f'<div class="faq">{items}</div></div></section>')

    blocks_html = "".join(blk(b) for b in p.get("blocks", []))

    rel_html = ""
    if p.get("related"):
        rel_html = blk({"t":"related","bg":"alt","eyebrow":t("rel_eyebrow"),
                        "h2":p.get("related_h2") or t("rel_h2"),"items":p["related"]})

    cta_html = ""
    if p.get("cta", True):
        cta_html = (f'<section class="{p.get("cta_bg","")}" id="callback"><div class="wrap">'
                    f'<div class="sechead"><p class="eyebrow">{e(t("cta_eyebrow"))}</p>'
                    f'<h2>{e(t("cta_h2"))}</h2>'
                    f'<p>{e(t("cta_p"))}</p>'
                    f'</div>{FORM[lg]}</div></section>')

    nap = ""
    if p.get("nap"):
        nap = f'''<div class="napbar">
      <div class="napitem"><div class="k">{t("nap")[0]}</div><div class="v">{BIZ["street"]}<br>{BIZ["city"]}, {BIZ["region"]} {BIZ["zip"]}</div></div>
      <div class="napitem"><div class="k">{t("nap")[1]}</div><div class="v">{t("nap_bart")}</div></div>
      <div class="napitem"><div class="k">{t("nap")[2]}</div><div class="v">{t("nap_langs")}</div></div>
      <div class="napitem"><div class="k">{t("nap")[3]}</div><div class="v"><a href="tel:{BIZ["tel_href"]}">{BIZ["tel_display"]}</a><br><span style="color:var(--ink-3);font-size:13.5px">{t("closed")}</span></div></div>
    </div>'''

    cur = "/" + (slug + "/" if slug else "")
    def nav_active(href):
        if href == "/": return cur == "/"
        return cur.startswith(href)
    CUR_ATTR = ' aria-current="page"'
    nav_html = "".join(
        '<a href="%s"%s>%s</a>' % (e(u), CUR_ATTR if nav_active(u) else "", e(n))
        for u, n in NAV_MAIN[lg])

    foot_cols = "".join(
        f'<div><h4>{e(_t)}</h4><ul>' + "".join(f'<li><a href="{e(u)}">{e(n)}</a></li>' for u,n in ls) + "</ul></div>"
        for _t, ls in NAV_FOOT[lg])

    # 語言切換：同一個 slug 若另一語言也有，就指過去；沒有就指對方首頁
    other = "en" if lg == "zh" else "zh"
    other_slug = slug if slug in HAVE[other] else ""
    other_path = pfx(other) + "/" + (other_slug + "/" if other_slug else "")
    lang_btn = ('<a class="langsw" href="%s%s" hreflang="%s" lang="%s">%s</a>'
                % (LANGMARK, other_path, T[other]["htmllang"], T[other]["htmllang"], e(t("other"))))
    foot_lang = ('<a href="%s%s" hreflang="%s">%s</a>'
                 % (LANGMARK, other_path, T[other]["htmllang"], e(t("other"))))

    # hreflang：只在兩邊都有這一頁時才互指，避免指到不存在的網址
    al = ['<link rel="canonical" href="%s">' % e(url)]
    if slug in HAVE[other]:
        me, them = (SITE + P + "/" + (slug + "/" if slug else "")), (SITE + other_path)
        pair = {lg: me, other: them}
        al.append('<link rel="alternate" hreflang="zh-Hant" href="%s">' % e(pair["zh"]))
        al.append('<link rel="alternate" hreflang="en" href="%s">' % e(pair["en"]))
        al.append('<link rel="alternate" hreflang="x-default" href="%s">' % e(pair["en"]))
    alt_links = "\n".join(al)

    # 分享預覽圖（LINE／WhatsApp／微信／Facebook 轉傳時顯示）。
    # 有首圖就用首圖，沒有就退回店面照，不要讓任何一頁沒有預覽圖。
    og_slug = hero[0] if (hero and hero[0] in IMG) else ("storefront" if "storefront" in IMG else None)
    og_alt  = hero[1] if (hero and hero[0] in IMG) else BIZ["en"]
    og_tags = ""
    if og_slug:
        _m = IMG[og_slug]
        _w = max([x for x in _m["sizes"] if x <= 1280] or _m["sizes"][:1])
        _url = f"{SITE}/assets/img/{og_slug}-{_w}.jpg"
        _h = round(_m["h"] * _w / _m["w"])
        og_tags = ('<meta property="og:image" content="%s">\n'
                   '<meta property="og:image:width" content="%d">\n'
                   '<meta property="og:image:height" content="%d">\n'
                   '<meta property="og:image:alt" content="%s">\n'
                   '<meta name="twitter:image" content="%s">'
                   % (e(_url), _w, _h, e(og_alt), e(_url)))

    return f'''<!doctype html>
<html lang="{t("htmllang")}">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p["title"])}</title>
{gtm_head()}
<meta name="description" content="{e(p["desc"])}">
{alt_links}
<meta property="og:type" content="website">
<meta property="og:locale" content="{t("oglocale")}">
<meta property="og:site_name" content="{e(t("name"))}">
<meta property="og:title" content="{e(p["title"])}">
<meta property="og:description" content="{e(p["desc"])}">
<meta property="og:url" content="{e(url)}">
<meta name="twitter:card" content="summary_large_image">
{og_tags}
<link rel="stylesheet" href="/assets/site.css?v={CSSV}">
</head>
<body>
{gtm_body()}
<a href="#main" class="skip">{e(t("skip"))}</a>
<header class="top"><div class="wrap topbar">
  <a href="/" class="brand"><span class="mark" aria-hidden="true">莊</span>
  <span><span class="bname">{e(t("brandname"))}</span><br><span class="bsub">CAREPLUS CHIROPRACTIC · SINCE {BIZ["founded"]}</span></span></a>
  <span class="topright">{lang_btn}<a href="tel:{BIZ["tel_href"]}" class="callbtn">{e(t("call"))} {BIZ["tel_display"]}</a></span>
</div>
<nav class="mainnav" aria-label="{e(t("nav"))}"><div class="wrap">{nav_html}</div></nav>
</header>
<nav class="crumb" aria-label="{e(t("crumb"))}"><div class="wrap">{crumb_html}</div></nav>
<main id="main">
<div class="phead"><div class="wrap">
  <span class="openpill"><span class="dot" aria-hidden="true"></span>{e(t("hours"))}</span>
  <h1>{e(p["h1"])}</h1>
  <p class="answer">{p["answer"]}</p>
  <div class="cta-row">
    <a href="tel:{BIZ["tel_href"]}" class="btn btn-p">{e(t("callcta"))} {BIZ["tel_display"]}</a>
    <a href="#callback" class="btn btn-s">{e(t("callback"))}</a>
  </div>
  {hero_html}
  {nap}
</div></div>
{blocks_html}
{faq_html}
{rel_html}
{cta_html}
</main>
<footer><div class="wrap">
  <div class="fgrid">
    <div><h4>{e(t("name"))}</h4><p style="color:var(--ink-2);margin:0;line-height:1.75;font-size:14.8px">
      {BIZ["en"]}<br>{BIZ["street"]}<br>{BIZ["city"]}, {BIZ["region"]} {BIZ["zip"]}<br>
      <a href="tel:{BIZ["tel_href"]}" style="font-weight:650">{BIZ["tel_display"]}</a></p></div>
    {foot_cols}
  </div>
  <div class="fbot">
    {e(t("hoursline"))}{e(t("hours"))} · {e(t("closed"))}<br>
    {e(t("disclaimer"))}<br>
    © 2026 {BIZ["en"]} · {e(t("footline"))} · {foot_lang}
  </div>
</div></footer>
<script type="application/ld+json">
{build_schema(p)}
</script>
<script>
(function(){{window.dataLayer=window.dataLayer||[];
var f=document.getElementById('cbForm');
if(f){{
  var st=document.getElementById('cbStatus'), btn=f.querySelector('button[type=submit]');
  var HAS_KEY={"true" if FORM_KEY else "false"};
  function say(msg,kind){{ if(!st)return; st.hidden=false; st.textContent=msg;
    st.className='formstatus'+(kind?' '+kind:''); }}
  f.addEventListener('submit',function(e){{
    e.preventDefault();
    if(!f.reportValidity||!f.reportValidity()) return;
    var r=document.getElementById('r');
    if(!HAS_KEY){{ say({js(t('preview_alert_inline'))},'warn'); return; }}
    btn.disabled=true; var orig=btn.textContent; btn.textContent={js(t('f_sending'))};
    say('','');  st.hidden=true;
    var data=Object.fromEntries(new FormData(f).entries());
    fetch(f.action,{{method:'POST',
      headers:{{'Content-Type':'application/json','Accept':'application/json'}},
      body:JSON.stringify(data)}})
    .then(function(res){{ return res.json().catch(function(){{return{{success:res.ok}};}}); }})
    .then(function(j){{
      if(j && j.success){{
        f.reset(); say({js(t('f_ok'))},'ok');
        window.dataLayer.push({{event:'callback_submit',form_name:'callback_request',
          reason:r?r.value:'',page_path:location.pathname}});
      }} else {{ say({js(t('f_err'))},'err'); }}
    }})
    .catch(function(){{ say({js(t('f_err'))},'err'); }})
    .finally(function(){{ btn.disabled=false; btn.textContent=orig; }});
  }});
}}
document.querySelectorAll('a[href^="tel:"]').forEach(function(a){{a.addEventListener('click',function(){{
window.dataLayer.push({{event:'phone_click',phone_number:a.getAttribute('href').replace('tel:',''),page_path:location.pathname}});}});}});
}})();
</script>
</body></html>'''

def apply_lang(html_text, lg):
    """中文頁掛在 /zh 底下，內容裡寫的都是 /services/ 這種根相對路徑，
    在這裡統一補上前綴。/assets/ 是共用資源不動；帶 LANGMARK 的是語言切換鈕，
    要指向另一個語言，所以也不能補。"""
    if lg != "zh":
        return html_text.replace(LANGMARK, "")
    def rep(m):
        attr, path = m.group(1), m.group(2)
        if path.startswith("/assets/"):
            return m.group(0)
        return '%s="/zh%s' % (attr, path)
    html_text = re.sub(r'(href|src)="(/(?!/)[^"]*)', rep, html_text)
    # srcset 只會指向 /assets/，不需處理
    return html_text.replace(LANGMARK, "")

def apply_base(html_text):
    """把站內絕對路徑 /xxx 加上子路徑前綴，並視需要插入 noindex。
    只動 href="/ 與 src="/ ，不碰 http(s):// 與 //。"""
    if BASE:
        html_text = re.sub(r'(href|src)="/(?!/)', r'\1="' + BASE + "/", html_text)
        # srcset 是逗號分隔的「網址 寬度」清單，上面的規則涵蓋不到，要另外處理
        def _ss(m):
            parts = []
            for cand in m.group(1).split(","):
                cand = cand.strip()
                if cand.startswith("/") and not cand.startswith("//"):
                    cand = BASE + cand
                parts.append(cand)
            return 'srcset="' + ", ".join(parts) + '"'
        html_text = re.sub(r'srcset="([^"]+)"', _ss, html_text)
    if NOINDEX and "<head>" in html_text:
        html_text = html_text.replace(
            "<head>", '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    return html_text

def out_dir(p):
    parts = [OUT]
    if p.get("lang", "zh") == "zh": parts.append("zh")
    if p["slug"]: parts.append(p["slug"])
    return os.path.join(*parts)

def write(p):
    lg = p.get("lang", "zh")
    d = out_dir(p)
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(apply_base(apply_lang(render(p), lg)))
    return os.path.join(d, "index.html")

def main():
    from content import PAGES
    for _p in PAGES:
        HAVE[_p.get("lang", "zh")].add(_p["slug"])
    if os.path.isdir(OUT): shutil.rmtree(OUT)
    os.makedirs(OUT)
    shutil.copytree("assets", os.path.join(OUT, "assets"))
    n = 0
    for p in PAGES:
        write(p); n += 1
    # GitHub Pages：告訴它不要用 Jekyll 處理
    open(os.path.join(OUT, ".nojekyll"), "w").close()
    # robots.txt
    with open(os.path.join(OUT, "robots.txt"), "w") as f:
        if NOINDEX:
            f.write("User-agent: *\nDisallow: /\n")   # 預覽站：不要被收錄
        else:
            f.write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    # sitemap
    prio = {"":"1.0","dot-physical":"0.9","services":"0.9","insurance":"0.9","pricing":"0.8","contact":"0.8"}
    urls = "".join(
        f'  <url><loc>{SITE}{pfx(p.get("lang","zh"))}/{p["slug"]+"/" if p["slug"] else ""}</loc>'
        f'<lastmod>{TODAY}</lastmod>'
        f'<priority>{prio.get(p["slug"], "0.9" if p["slug"].count("/")==1 else "0.6")}</priority></url>\n'
        for p in PAGES)
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    # 404 與感謝頁（不進 sitemap、加 noindex）
    # 404 與感謝頁：GitHub Pages 全站只會用根目錄這一個 404，所以做成雙語一頁。
    def shell(lg, title, h, body):
        tt = T[lg]
        return f"""<!doctype html>
<html lang="{tt['htmllang']}"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title>
{gtm_head()}
<link rel="stylesheet" href="/assets/site.css?v={CSSV}"></head>
<body>
{gtm_body()}
<header class="top"><div class="wrap topbar">
<a href="{pfx(lg)}/" class="brand"><span class="mark" aria-hidden="true">莊</span>
<span><span class="bname">{tt['brandname']}</span><br><span class="bsub">CAREPLUS CHIROPRACTIC · SINCE {BIZ['founded']}</span></span></a>
<a href="tel:{BIZ['tel_href']}" class="callbtn">{tt['call']} {BIZ['tel_display']}</a></div></header>
<main><section style="padding:70px 0 30px;text-align:center"><div class="wrap narrow">
<h1 style="max-width:none;margin-inline:auto">{h}</h1>{body}</div></section></main>
<footer><div class="wrap"><div class="fbot">{tt['hoursline']}{tt['hours']} · {tt['closed']}<br>
© 2026 {BIZ['en']} · {BIZ['street']}, {BIZ['city']}, {BIZ['region']} {BIZ['zip']}</div></div></footer>
</body></html>"""

    def bilingual(en_body, zh_body):
        """英文在上、中文在下，中間一條分隔線。"""
        return (en_body
                + '<hr style="margin:56px auto 46px;max-width:120px;border:0;border-top:2px solid var(--line)">'
                + '<div lang="zh-Hant">' + zh_body + '</div>')

    nf_en = f'''<p class="answer" style="margin-inline:auto">{T["en"]["nf_p"]}</p>
<div class="cta-row" style="justify-content:center">
<a href="tel:{BIZ["tel_href"]}" class="btn btn-p">{T["en"]["callcta"]} {BIZ["tel_display"]}</a>
<a href="/" class="btn btn-s">Back to home</a></div>
<div class="related" style="margin-top:34px;text-align:left">
<a class="rel" href="/services/">Services<span>Conditions and treatments</span></a>
<a class="rel" href="/dot-physical/">DOT physical $95<span>Commercial driver examination</span></a>
<a class="rel" href="/insurance/">Fees and insurance<span>Four ways treatment is paid for</span></a>
<a class="rel" href="/contact/">Visit us<span>Directions and hours</span></a></div>'''

    nf_zh = f'''<h2 style="text-align:center;margin-bottom:14px">找不到這個頁面</h2>
<p class="answer" style="margin-inline:auto">您要找的頁面可能已移除或網址有誤。需要預約或有任何問題，歡迎直接來電。</p>
<div class="cta-row" style="justify-content:center">
<a href="tel:{BIZ["tel_href"]}" class="btn btn-p">致電預約 {BIZ["tel_display"]}</a>
<a href="/zh/" class="btn btn-s">回到中文首頁</a></div>
<div class="related" style="margin-top:34px;text-align:left">
<a class="rel" href="/zh/services/">治療項目<span>16 個症狀與療法頁面</span></a>
<a class="rel" href="/zh/dot-physical/">DOT 體檢 $95<span>商業司機體檢</span></a>
<a class="rel" href="/zh/insurance/">費用與保險<span>五種付費方式</span></a>
<a class="rel" href="/zh/contact/">交通與停車<span>地址與門診時間</span></a></div>'''

    with open(os.path.join(OUT,"404.html"),"w",encoding="utf-8") as f:
        f.write(apply_base(shell("en", T["en"]["nf_t"]+" — "+BIZ["en"], T["en"]["nf_h"],
                                 bilingual(nf_en, nf_zh))))

    ty_en = f'''<p class="answer" style="margin-inline:auto">{T["en"]["ty_p"]}</p>
<div class="cta-row" style="justify-content:center">
<a href="tel:{BIZ["tel_href"]}" class="btn btn-p">{T["en"]["call"]} {BIZ["tel_display"]}</a>
<a href="/" class="btn btn-s">Back to home</a></div>'''
    ty_zh = f'''<h2 style="text-align:center;margin-bottom:14px">已收到，我們會主動致電</h2>
<p class="answer" style="margin-inline:auto">感謝您的來信。我們會在門診時間內（{BIZ["hours_zh"]}）依您選擇的時段主動致電。若急需就診，也歡迎直接來電。</p>
<div class="cta-row" style="justify-content:center">
<a href="tel:{BIZ["tel_href"]}" class="btn btn-p">直接致電 {BIZ["tel_display"]}</a>
<a href="/zh/" class="btn btn-s">回到中文首頁</a></div>'''
    with open(os.path.join(OUT,"thanks.html"),"w",encoding="utf-8") as f:
        f.write(apply_base(shell("en", T["en"]["ty_t"]+" — "+BIZ["en"], T["en"]["ty_h"],
                                 bilingual(ty_en, ty_zh))))
    # 審稿用的全站目錄（noindex，不進 sitemap）
    groups = [("品牌層",""),("服務層","services/"),("DOT 筒倉","dot-physical"),
              ("付費層","insurance/"),("信任層",None)]
    def grp(sl):
        if sl.startswith("services"): return "服務層"
        if sl.startswith("dot-physical"): return "DOT 筒倉"
        if sl.startswith("insurance"): return "付費層"
        if sl in ("","about","about/dr-stewart-chen","about/team","contact"): return "品牌層"
        return "信任層"
    buckets = {}
    for pg in PAGES:
        buckets.setdefault(grp(pg["slug"]), []).append(pg)
    rows = ""
    for gname in ["品牌層","服務層","DOT 筒倉","付費層","信任層"]:
        ps = buckets.get(gname, [])
        rows += f'<h2>{gname}<span style="color:var(--ink-3);font-weight:400;font-size:16px"> · {len(ps)} 頁</span></h2><div class="related" style="margin-bottom:34px">'
        for pg in ps:
            u = "/" + (pg["slug"] + "/" if pg["slug"] else "")
            nf = len(pg.get("faqs") or [])
            rows += (f'<a class="rel" href="{u}">{html.escape(pg["h1"])}'
                     f'<span>{u} · FAQ {nf} 題</span></a>')
        rows += "</div>"
    idx = f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex,nofollow">
<title>全站目錄（審稿用）— {BIZ['zh']}</title>
<link rel="stylesheet" href="/assets/site.css?v={CSSV}"></head>
<body><header class="top"><div class="wrap topbar">
<a href="/" class="brand"><span class="mark" aria-hidden="true">莊</span>
<span><span class="bname">全站目錄</span><br><span class="bsub">內部審稿用 · 不會被搜尋引擎收錄</span></span></a>
<a href="/" class="callbtn">看首頁</a></div></header>
<main><section style="padding:48px 0"><div class="wrap">
<div class="note" style="margin-bottom:34px"><div class="h">這一頁給誰看</div>
<p>這是<strong>內部審稿用</strong>的目錄，方便逐頁檢查內容。已加 <code>noindex</code>，也不在 sitemap 裡，
不會被搜尋引擎收錄。要改內容請編輯 <code>site/content/*.py</code>，改完跑 <code>python3 build.py</code>。</p></div>
{rows}
<div class="note ok"><div class="h">其他產出</div>
<p><a href="/sitemap.xml">sitemap.xml</a> · <a href="/robots.txt">robots.txt</a> ·
<a href="/404.html">404 頁</a> · <a href="/thanks.html">表單送出後的感謝頁</a></p></div>
</div></section></main>
<footer><div class="wrap"><div class="fbot">共 {len(PAGES)} 頁 · 產生於 {TODAY}</div></div></footer>
</body></html>"""
    os.makedirs(os.path.join(OUT, "_pages"), exist_ok=True)
    with open(os.path.join(OUT, "_pages", "index.html"), "w", encoding="utf-8") as f:
        f.write(apply_base(idx))
    print(f"✓ 產出 {n} 頁 + 404 + thanks + 審稿目錄 /_pages/ → {OUT}/")
    return n

if __name__ == "__main__":
    main()
