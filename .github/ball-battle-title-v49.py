from pathlib import Path

path = Path('index.html')
s = path.read_text(encoding='utf-8')
old = '<h1 id="mainTitle">볼배틀 리뉴얼 v45</h1>'
new = '<h1 id="mainTitle">볼배틀 리뉴얼 v49</h1>'
if old not in s:
    raise SystemExit('main title anchor not found')
s = s.replace(old, new, 1)
path.write_text(s, encoding='utf-8')
