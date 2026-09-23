# -*- coding: utf-8 -*-
"""服務頁工廠：統一骨架，每頁只需提供差異內容。
骨架依 GEO 藍圖 7.2：H1 → 直答 → 這是什麼情況 → 我們怎麼處理 → 費用與保險 → 為什麼選這裡 → FAQ → 相關"""

PAY_ROUTES = [
 ("/insurance/auto-accident/","車禍理賠","對方責任險、自身 MedPay，或律師代理下以 lien 處理。","需要準備什麼 →"),
 ("/insurance/workers-comp/","工傷理賠","加州勞工賠償體系，含 QME 醫療評估。","流程說明 →"),
 ("/insurance/ppo/","私人保險","PPO 方案的給付與自付額說明。","如何確認 →"),
 ("/insurance/self-pay/","自費","初診檢查含數位 X 光的自費價目。","查看價目 →"),
]

WHY_DEFAULT = [
 ("執業年資","1988 年至今・38 年","在奧克蘭中國城同一個社區服務 38 年，處理過大量脊椎相關的個案。",False),
 ("看診語言","粵語・國語・台語・英語","從問診到治療計畫說明，全程可用您最習慣的語言，不需要自己帶翻譯。",False),
 ("院內檢查","數位 X 光・當次評估","必要時可在院內拍攝數位 X 光，不需另外跑一趟影像中心。",False),
 ("交通","Lake Merritt BART 步行 5 分鐘","診所位於奧克蘭中國城 Madison 專業大樓，大樓與路邊皆有停車位。",False),
]

STEPS_DEFAULT = [
 ("問診：先聽你怎麼說","了解疼痛的位置、什麼時候開始、什麼動作會加重、過去有沒有受過傷、工作與睡姿的習慣。若是車禍或工傷，也會問事故經過。"),
 ("理學檢查","觸診、活動度測試、神經學檢查（反射、肌力、感覺），判斷問題來自結構、神經還是軟組織。"),
 ("必要時拍數位 X 光","院內可直接拍攝。是否需要由醫師依臨床判斷決定，不是每個人都要拍。"),
 ("說明評估結果與治療計畫","當次就把檢查發現、可能的原因、建議的處理方式與大概需要的次數講清楚，再決定要不要開始。"),
]

def svc(slug, h1, title, desc, answer, sname, sdesc, what_h2, what_html, what_src,
        methods, faqs, related, procedure=None, steps=None, why=None,
        extra_blocks=None, crumb_self=None):
    blocks = [
      {"t":"prose","eyebrow":"先了解狀況","h2":what_h2,"html":what_html,"sources":what_src},
      {"t":"steps","bg":"alt","eyebrow":"第一次來會發生什麼","h2":"我們怎麼處理",
       "lede":"我們不會第一次見面就開始做治療。先把狀況查清楚，再決定怎麼做。",
       "items":steps or STEPS_DEFAULT},
      {"t":"checklist","eyebrow":"可能用到的方式","h2":"依個別狀況搭配使用",
       "lede":"不是每個人都會用到全部項目，實際組合由評估結果決定。",
       "items":methods,
       "sources":["aca","nccih_back"]},
      {"t":"routes","bg":"alt","eyebrow":"費用與保險","h2":"這類治療通常由誰支付",
       "lede":"費用來源會影響你需要準備的文件。選擇最接近你的情況：",
       "items":PAY_ROUTES},
      {"t":"facts","eyebrow":"為什麼選這裡","h2":"幾項客觀條件","items":why or WHY_DEFAULT},
    ]
    if extra_blocks:
        blocks = blocks[:1] + extra_blocks + blocks[1:]
    p = {
      "slug":"services/"+slug, "crumbs":[("治療項目","/services/")],
      "crumb_self":crumb_self or h1.split("｜")[0],
      "title":title, "desc":desc, "h1":h1, "answer":answer, "cta_bg":"alt",
      "service":{"type":"MedicalProcedure" if procedure else "Service",
                 "name":sname,"desc":sdesc},
      "blocks":blocks, "faqs":faqs, "related":related,
      "faq_bg":"alt" if not extra_blocks else "",
    }
    if procedure: p["service"]["procedureType"] = procedure
    return p
