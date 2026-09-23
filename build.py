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
SITE = os.environ.get("SITE_URL", "https://stewartchenchiro.com").rstrip("/")
BASE = "/" + os.environ.get("BASE_PATH", "").strip("/") if os.environ.get("BASE_PATH", "").strip("/") else ""
NOINDEX = os.environ.get("NOINDEX", "") == "1"   # 預覽站設 1，避免被搜尋引擎收錄
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
 "chiro_ca":   ("ext","https://www.chiro.ca.gov/consumers/verify_lic.shtml","加州脊骨神經醫學委員會・執照查詢"),
 "dwc_qme":    ("ext","https://www.dir.ca.gov/dwc/MedicalUnit/imchp.html","加州 DWC・QME 制度說明"),
 "dwc_main":   ("ext","https://www.dir.ca.gov/dwc/","加州勞工賠償局（DWC）"),
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

NAV_FOOT = [
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

def e(s): return html.escape(str(s), quote=True)

def src_line(keys, label="參考來源："):
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
    elif t == "form":
        body = FORM_HTML
    elif t == "raw":
        body = b["html"]

    if b.get("sources") and t != "price":
        body += src_line(b["sources"])
    return f'<section class="{b.get("bg","")}"><div class="wrap">{head}{body}</div></section>'

FORM_HTML = f'''<form class="formwrap" id="cbForm" method="POST" action="REPLACE_WITH_ENDPOINT" novalidate>
<div style="position:absolute;left:-9999px" aria-hidden="true"><label>請勿填寫<input type="text" name="_gotcha" tabindex="-1" autocomplete="off"></label></div>
<label for="n">稱呼 <span style="color:var(--accent)">*</span></label>
<input id="n" name="name" type="text" required autocomplete="name" placeholder="例：陳先生">
<label for="t">回電號碼 <span style="color:var(--accent)">*</span></label>
<input id="t" name="phone" type="tel" required autocomplete="tel" inputmode="tel" placeholder="510-000-0000">
<label for="r">想處理的問題</label>
<select id="r" name="reason"><option value="">請選擇（可略過）</option>
<option>車禍受傷</option><option>工傷／需要 QME 評估</option><option>腰背・頸肩疼痛</option>
<option>坐骨神經痛・手腳麻木</option><option>DOT／CDL 商業司機體檢</option><option>針灸或推拿</option>
<option>其他／不確定</option></select>
<label for="w">方便接電話的時段</label>
<select id="w" name="best_time"><option>上午 9:00–12:00</option><option>下午 12:00–15:00</option>
<option>下午 15:00–18:00</option><option>都可以</option></select>
<label for="l">希望用哪種語言溝通</label>
<select id="l" name="language"><option>粵語</option><option>國語／普通話</option><option>台語／閩南話</option><option>English</option></select>
<button type="submit">送出，請診所回電</button>
<p class="formnote">我們只會用這個號碼與您聯繫預約事宜。<br>急需就診請直接致電 <a href="tel:{BIZ["tel_href"]}">{BIZ["tel_display"]}</a>。</p>
</form>'''

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

def physician_node():
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
        {"@type":"EducationalOccupationalCredential","credentialCategory":"Qualified Medical Evaluator (QME)",
         "recognizedBy":{"@type":"GovernmentOrganization",
           "name":"State of California, Division of Workers' Compensation","url":"https://www.dir.ca.gov/dwc/"}},
        {"@type":"EducationalOccupationalCredential","credentialCategory":"Certified Medical Examiner",
         "recognizedBy":{"@type":"GovernmentOrganization",
           "name":"U.S. Department of Transportation, FMCSA National Registry",
           "url":"https://nationalregistry.fmcsa.dot.gov/"}}],
    }

def build_schema(p):
    url = SITE + "/" + (p["slug"] + "/" if p["slug"] else "")
    url = url.replace("//", "/").replace("https:/", "https://")
    g = []
    if p["slug"] == "":
        g.append(clinic_node()); g.append(physician_node())
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
    if p.get("person_schema"): g.append(physician_node())
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
    g.append({"@type":"WebPage","@id":url+"#webpage","url":url,"name":p["title"],
              "description":p["desc"],"inLanguage":"zh-Hant",
              "isPartOf":{"@id":f"{SITE}/#website"},"about":{"@id":f"{SITE}/#clinic"},
              "breadcrumb":{"@type":"BreadcrumbList","itemListElement":[
                {"@type":"ListItem","position":i+1,"name":n,"item":SITE+u}
                for i,(n,u) in enumerate(cl)]}})
    return json.dumps({"@context":"https://schema.org","@graph":g}, ensure_ascii=False, indent=1)

# ─────────────────── 頁面組裝 ───────────────────
def render(p):
    slug = p["slug"]
    url = SITE + "/" + (slug + "/" if slug else "")
    depth_prefix = "/"
    crumb_items = [("首頁","/")] + list(p.get("crumbs",[]))
    crumb_html = "".join(f'<a href="{e(u)}">{e(n)}</a><span>›</span>' for n,u in crumb_items)
    crumb_html += f'<strong style="color:var(--ink-2);font-weight:600">{e(p.get("crumb_self") or p["h1"])}</strong>'

    faq_html = ""
    if p.get("faqs"):
        items = ""
        for i,(q,a,s) in enumerate(p["faqs"]):
            op = " open" if i == 0 else ""
            items += (f'<details{op}><summary>{e(q)}</summary><div class="fa">{a}'
                      f'{src_line(s) if s else ""}</div></details>')
        faq_html = (f'<section class="{p.get("faq_bg","")}"><div class="wrap">'
                    f'<div class="sechead"><p class="eyebrow">常見問題</p>'
                    f'<h2>{e(p.get("faq_h2","常見問題"))}</h2></div>'
                    f'<div class="faq">{items}</div></div></section>')

    blocks_html = "".join(blk(b) for b in p.get("blocks", []))

    rel_html = ""
    if p.get("related"):
        rel_html = blk({"t":"related","bg":"alt","eyebrow":"相關頁面",
                        "h2":p.get("related_h2","你可能也需要看這些"),"items":p["related"]})

    cta_html = ""
    if p.get("cta", True):
        cta_html = (f'<section class="{p.get("cta_bg","")}" id="callback"><div class="wrap">'
                    f'<div class="sechead"><p class="eyebrow">回電預約</p>'
                    f'<h2>不方便現在打電話？留下時段，我們回電給您</h2>'
                    f'<p>本中心採電話預約。若您現在不方便通話，填寫下方表單，我們會在門診時間內主動致電。</p>'
                    f'</div>{FORM_HTML}</div></section>')

    nap = ""
    if p.get("nap"):
        nap = f'''<div class="napbar">
      <div class="napitem"><div class="k">地址</div><div class="v">{BIZ["street"]}<br>{BIZ["city"]}, {BIZ["region"]} {BIZ["zip"]}</div></div>
      <div class="napitem"><div class="k">交通</div><div class="v">Lake Merritt BART<br>步行約 5 分鐘</div></div>
      <div class="napitem"><div class="k">看診語言</div><div class="v">粵語・國語・台語<br>閩南話・English</div></div>
      <div class="napitem"><div class="k">電話</div><div class="v"><a href="tel:{BIZ["tel_href"]}">{BIZ["tel_display"]}</a><br><span style="color:var(--ink-3);font-size:13.5px">週日休診</span></div></div>
    </div>'''

    foot_cols = "".join(
        f'<div><h4>{e(t)}</h4><ul>' + "".join(f'<li><a href="{e(u)}">{e(n)}</a></li>' for u,n in ls) + "</ul></div>"
        for t,ls in NAV_FOOT)

    return f'''<!doctype html>
<html lang="zh-Hant">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(p["title"])}</title>
<meta name="description" content="{e(p["desc"])}">
<link rel="canonical" href="{e(url)}">
<link rel="alternate" hreflang="zh-Hant" href="{e(url)}">
<link rel="alternate" hreflang="en" href="{EN_SITE}/">
<link rel="alternate" hreflang="x-default" href="{EN_SITE}/">
<meta property="og:type" content="website">
<meta property="og:locale" content="zh_TW">
<meta property="og:site_name" content="{BIZ["zh"]} {BIZ["en"]}">
<meta property="og:title" content="{e(p["title"])}">
<meta property="og:description" content="{e(p["desc"])}">
<meta property="og:url" content="{e(url)}">
<meta name="twitter:card" content="summary_large_image">
<link rel="stylesheet" href="/assets/site.css">
</head>
<body>
<a href="#main" class="skip">跳到主要內容</a>
<header class="top"><div class="wrap topbar">
  <a href="/" class="brand"><span class="mark" aria-hidden="true">莊</span>
  <span><span class="bname">{BIZ["zh"]}</span><br><span class="bsub">CAREPLUS CHIROPRACTIC · SINCE {BIZ["founded"]}</span></span></a>
  <a href="tel:{BIZ["tel_href"]}" class="callbtn">致電 {BIZ["tel_display"]}</a>
</div></header>
<nav class="crumb" aria-label="麵包屑"><div class="wrap">{crumb_html}</div></nav>
<main id="main">
<div class="phead"><div class="wrap">
  <span class="openpill"><span class="dot" aria-hidden="true"></span>{BIZ["hours_zh"]}</span>
  <h1>{e(p["h1"])}</h1>
  <p class="answer">{p["answer"]}</p>
  <div class="cta-row">
    <a href="tel:{BIZ["tel_href"]}" class="btn btn-p">致電預約 {BIZ["tel_display"]}</a>
    <a href="#callback" class="btn btn-s">請診所回電</a>
  </div>
  {nap}
</div></div>
{blocks_html}
{faq_html}
{rel_html}
{cta_html}
</main>
<footer><div class="wrap">
  <div class="fgrid">
    <div><h4>{BIZ["zh"]}</h4><p style="color:var(--ink-2);margin:0;line-height:1.75;font-size:14.8px">
      {BIZ["en"]}<br>{BIZ["street"]}<br>{BIZ["city"]}, {BIZ["region"]} {BIZ["zip"]}<br>
      <a href="tel:{BIZ["tel_href"]}" style="font-weight:650">{BIZ["tel_display"]}</a></p></div>
    {foot_cols}
  </div>
  <div class="fbot">
    營業時間：{BIZ["hours_zh"]} · 週日休診<br>
    本網站內容僅供一般健康資訊參考，不能取代專業醫療診斷或治療建議。個別狀況請親自到診評估。<br>
    © 2026 {BIZ["en"]} · 奧克蘭中國城執業 {BIZ["years"]} 年 · <a href="{EN_SITE}/" hreflang="en">English Site</a>
  </div>
</div></footer>
<script type="application/ld+json">
{build_schema(p)}
</script>
<script>
(function(){{window.dataLayer=window.dataLayer||[];
var f=document.getElementById('cbForm');
if(f)f.addEventListener('submit',function(e){{var r=document.getElementById('r');
window.dataLayer.push({{event:'callback_submit',form_name:'callback_request',reason:r?r.value:'',page_path:location.pathname}});
// 收件端點還沒設定時，不要真的送出（會變成 404），改成提示
if((f.getAttribute('action')||'').indexOf('REPLACE_WITH_ENDPOINT')>-1){{
  e.preventDefault();
  alert('這是預覽版，表單還沒接上收件信箱，所以不會真的送出。\\n\\n正式上線後，送出的內容會寄到診所的信箱。\\n現在要預約請直接致電 510-465-7982。');
}}}});
document.querySelectorAll('a[href^="tel:"]').forEach(function(a){{a.addEventListener('click',function(){{
window.dataLayer.push({{event:'phone_click',phone_number:a.getAttribute('href').replace('tel:',''),page_path:location.pathname}});}});}});
}})();
</script>
</body></html>'''

def apply_base(html_text):
    """把站內絕對路徑 /xxx 加上子路徑前綴，並視需要插入 noindex。
    只動 href="/ 與 src="/ ，不碰 http(s):// 與 //。"""
    if BASE:
        html_text = re.sub(r'(href|src)="/(?!/)', r'\1="' + BASE + "/", html_text)
    if NOINDEX and "<head>" in html_text:
        html_text = html_text.replace(
            "<head>", '<head>\n<meta name="robots" content="noindex,nofollow">', 1)
    return html_text

def write(p):
    d = os.path.join(OUT, p["slug"]) if p["slug"] else OUT
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f:
        f.write(apply_base(render(p)))
    return os.path.join(d, "index.html")

def main():
    from content import PAGES
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
        f'  <url><loc>{SITE}/{p["slug"]+"/" if p["slug"] else ""}</loc>'
        f'<lastmod>{TODAY}</lastmod>'
        f'<priority>{prio.get(p["slug"], "0.9" if p["slug"].count("/")==1 else "0.6")}</priority></url>\n'
        for p in PAGES)
    with open(os.path.join(OUT, "sitemap.xml"), "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n'
                '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + urls + "</urlset>\n")
    # 404 與感謝頁（不進 sitemap、加 noindex）
    shell = lambda title, h, body: f"""<!doctype html>
<html lang="zh-Hant"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="robots" content="noindex">
<title>{title}</title><link rel="stylesheet" href="/assets/site.css"></head>
<body><header class="top"><div class="wrap topbar">
<a href="/" class="brand"><span class="mark" aria-hidden="true">莊</span>
<span><span class="bname">{BIZ['zh']}</span><br><span class="bsub">CAREPLUS CHIROPRACTIC · SINCE {BIZ['founded']}</span></span></a>
<a href="tel:{BIZ['tel_href']}" class="callbtn">致電 {BIZ['tel_display']}</a></div></header>
<main><section style="padding:90px 0;text-align:center"><div class="wrap narrow">
<h1 style="max-width:none;margin-inline:auto">{h}</h1>{body}</div></section></main>
<footer><div class="wrap"><div class="fbot">營業時間：{BIZ['hours_zh']} · 週日休診<br>
© 2026 {BIZ['en']} · {BIZ['street']}, {BIZ['city']}, {BIZ['region']} {BIZ['zip']}</div></div></footer>
</body></html>"""
    with open(os.path.join(OUT,"404.html"),"w",encoding="utf-8") as f:
        f.write(apply_base(shell("找不到頁面 — "+BIZ["zh"], "找不到這個頁面",
          f'''<p class="answer" style="margin-inline:auto">您要找的頁面可能已移除或網址有誤。需要預約或有任何問題，歡迎直接來電。</p>
<div class="cta-row" style="justify-content:center">
<a href="tel:{BIZ["tel_href"]}" class="btn btn-p">致電預約 {BIZ["tel_display"]}</a>
<a href="/" class="btn btn-s">回到首頁</a></div>
<div class="related" style="margin-top:40px;text-align:left">
<a class="rel" href="/services/">治療項目<span>16 個症狀與療法頁面</span></a>
<a class="rel" href="/dot-physical/">DOT 體檢 $95<span>商業司機體檢</span></a>
<a class="rel" href="/insurance/">費用與保險<span>五種付費方式</span></a>
<a class="rel" href="/contact/">交通與停車<span>地址與門診時間</span></a></div>''')))
    with open(os.path.join(OUT,"thanks.html"),"w",encoding="utf-8") as f:
        f.write(apply_base(shell("已收到您的回電申請 — "+BIZ["zh"], "已收到，我們會盡快回電",
          f'''<p class="answer" style="margin-inline:auto">感謝您的來信。我們會在門診時間內（{BIZ["hours_zh"]}）依您選擇的時段主動致電。若急需就診，也歡迎直接來電。</p>
<div class="cta-row" style="justify-content:center">
<a href="tel:{BIZ["tel_href"]}" class="btn btn-p">直接致電 {BIZ["tel_display"]}</a>
<a href="/" class="btn btn-s">回到首頁</a></div>
<script>window.dataLayer=window.dataLayer||[];window.dataLayer.push({{event:"callback_thankyou"}});</script>''')))
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
<link rel="stylesheet" href="/assets/site.css"></head>
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
