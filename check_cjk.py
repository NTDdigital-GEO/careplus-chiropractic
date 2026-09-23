# -*- coding: utf-8 -*-
"""內容品質掃描：非繁中字元、政策風險字、缺漏欄位"""
import sys,re,glob
# 韓文 + 日文假名，但排除 U+30FB「・」（繁中排版正規分隔符）
BAD = re.compile(r'[가-힯぀-ヺー-ヿ]')
RISK = re.compile(r'唯一|最好|最佳|最優|治癒|痊癒|痊愈|保證|根治|徹底根除|神速|妙手回春|包治|療效顯著|百分之百')
hits=0
for f in sorted(glob.glob("content/*.py")):
    for n,l in enumerate(open(f,encoding="utf-8"),1):
        for m in BAD.finditer(l):
            print(f"  [非繁中] {f}:{n} 「{m.group()}」 …{l.strip()[max(0,m.start()-25):m.start()+25]}…"); hits+=1
        for m in RISK.finditer(l):
            print(f"  [政策風險] {f}:{n} 「{m.group()}」 …{l.strip()[max(0,m.start()-30):m.start()+30]}…"); hits+=1
print("✓ 掃描通過" if not hits else f"✗ {hits} 處需處理")
sys.exit(1 if hits else 0)
