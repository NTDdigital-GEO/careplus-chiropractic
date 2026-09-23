# 莊錦鎮脊椎治療中心 · 中文網站

CarePlus Chiropractic Health Center 的中文官網（35 頁）。
內容與版型分離：文字放在 `content/` 的 Python 檔裡，`build.py` 產出完整的 HTML 網站。

**推 main 分支 → GitHub Actions 自動建置、自動檢查、自動發布。**

---

## 目錄結構

```
content/              ← 文字都在這裡。要改內容就是改這幾個檔
  c_core.py             首頁、中心介紹、莊醫師、團隊、交通（5 頁）
  c_services_a.py       服務總覽＋車禍、腰背、頸肩、坐骨神經、椎間盤、工傷（7 頁）
  c_services_b.py       頭痛、側彎、運動傷害、NRC、針灸、推拿、復健、兒童、孕期（9 頁）
  c_dot.py              DOT／CDL 體檢（3 頁）
  c_insurance.py        付費與保險（6 頁）
  c_trust.py            價目、評價、媒體、常見問題、初診須知（5 頁）
  _svc.py               服務頁共用骨架
  __init__.py           彙整＋完整性檢查

assets/site.css       全站唯一的樣式檔
build.py              產生器（模板、schema、頁面組裝）
validate.py           檢查：失效連結／重複標題／H1／schema
check_cjk.py          檢查：非繁中字元／政策風險字
serve.py              本機預覽伺服器
make_singlefile.py    產出單一檔案版（給不會用終端機的同事審稿）
make_printable.py     產出可存成 PDF 的全文版
Caddyfile             自架主機時的設定（目前用 GitHub Pages，用不到）

.github/workflows/deploy.yml   自動建置與發布
dist/                 產出（不進版本控制，由 Actions 自動產生）
```

## 兩種改內容的方式

**方式 A — 在 GitHub 網頁上改（不用裝任何東西）**
1. 進 repo → `content/` → 點要改的檔
2. 按鉛筆圖示 → 改引號中間的中文字
3. 按 Commit changes
4. 等 2 分鐘，網站自動更新

**方式 B — 在自己電腦上改**
```bash
python3 build.py        # 產出到 dist/
python3 validate.py     # 檢查
python3 check_cjk.py    # 檢查
python3 serve.py        # 本機預覽 http://localhost:4173/
```
改完 `git add -A && git commit -m "說明" && git push`

## 建置參數（環境變數）

| 變數 | 用途 | 預設 |
|---|---|---|
| `SITE_URL` | 寫進 canonical／schema／sitemap 的完整網域 | `https://stewartchenchiro.com` |
| `BASE_PATH` | 子路徑。GitHub Pages 專案網站要填 `/repo名稱`，自訂網域留空 | 空 |
| `NOINDEX` | `1` = 加上 noindex 並擋 robots（預覽階段用）；`0` = 開放收錄 | `0` |

GitHub Actions 會自動填好前兩個。`NOINDEX` 在 `.github/workflows/deploy.yml` 裡，**正式上線時改成 0**。

## 每頁的資料格式

```python
{
 "slug": "services/sciatica",      # → /services/sciatica/
 "title": "...",                   # <title>，全站必須唯一
 "desc": "...",                    # meta description，全站必須唯一
 "h1": "...",                      # 每頁剛好一個
 "answer": "...",                  # 直答段落，40–60 字，給 AI 摘錄用
 "crumbs": [("治療項目","/services/")],
 "blocks": [...],                  # 內容區塊
 "faqs": [(問題, 答案HTML, 來源list)],
 "related": [(url, 標題, 副標)],
}
```

可用的 block 型別：`prose` `steps` `checklist` `facts` `routes` `price`
`table` `note` `equip` `people` `reviews` `related` `form` `raw`

引用來源用 `build.py` 裡 `SRC` 字典的鍵；外部引用自動上紫色、內部引用上橘色。

## 上線前還沒做的事

- [ ] 表單端點：`build.py` 裡的 `REPLACE_WITH_ENDPOINT` 要換成實際收件網址
- [ ] GTM 容器碼 `GTM-PFJXXHJN` 要加進 `render()`
- [ ] 營業時間待客戶確認（目前依英文站：週一至五 9:00–18:00、週六 9:00–12:00）
- [ ] 放照片（用 GBP 上的真實照片，轉 WebP）
- [ ] 正式上線時把 `NOINDEX` 改成 `0`，並在 Search Console 提交 sitemap
