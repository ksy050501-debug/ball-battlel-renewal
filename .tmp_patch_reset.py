from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if '볼배틀 리뉴얼 v137' not in s:
    raise SystemExit('v137 marker missing')
s = s.replace('볼배틀 리뉴얼 v137', '볼배틀 리뉴얼 v138', 1)

old = '''      <div class="button-row" style="width:min(700px,100%);grid-template-columns:1fr;">
        <button class="ghost" id="copyMatchupBtn">전적 복사</button>
      </div>'''
new = '''      <div class="button-row" style="width:min(700px,100%);">
        <button class="ghost" id="copyMatchupBtn">전적 복사</button>
        <button class="danger" id="resetMatchupBtn">전적 리셋</button>
      </div>'''
if s.count(old) != 1:
    raise SystemExit(f'button row marker expected 1, found {s.count(old)}')
s = s.replace(old, new, 1)

old = '    $("copyMatchupBtn").addEventListener("click", copyMatchupHistory);'
new = old + '\n    $("resetMatchupBtn").addEventListener("click", resetMatchupHistory);'
if s.count(old) != 1:
    raise SystemExit(f'copy listener marker expected 1, found {s.count(old)}')
s = s.replace(old, new, 1)

p.write_text(s, encoding='utf-8')
