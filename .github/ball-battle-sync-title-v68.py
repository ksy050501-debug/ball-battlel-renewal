from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")
old='<h1 id="mainTitle">볼배틀 리뉴얼 v64</h1>'
new='<h1 id="mainTitle">볼배틀 리뉴얼 v68</h1>'
if t.count(old)!=1:
    raise SystemExit(f"expected exactly one visible title, found {t.count(old)}")
p.write_text(t.replace(old,new,1),encoding="utf-8")

# trigger
