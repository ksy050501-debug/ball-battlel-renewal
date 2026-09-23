from pathlib import Path
import re

p=Path('index.html')
t=p.read_text(encoding='utf-8')

pairs=[
('condition: "웹스윙 8초 · 빗나가면 벽을 타고 연속 스윙 · 비스윙 중 5초마다 거미줄 6연사"',
 'condition: "웹스윙 8초 · 빗나가면 먼 벽으로 최대5연속 스윙 · 비스윙 중 5초마다 거미줄 6연사"'),
('웹스윙 8초 · 적을 못 맞히면 벽을 축으로 부채꼴 이동 후 다시 발사, 적중할 때까지 반복',
 '웹스윙 8초 · 먼 벽으로 최대5연속 · 스윙 중 몸 충돌도 근접18+강넉백'),
]
for old,new in pairs:
    if old not in t:
        raise SystemExit('missing text: '+old[:40])
    t=t.replace(old,new,1)

p.write_text(t,encoding='utf-8')
scripts=re.findall(r'<script[^>]*>([\s\S]*?)</script>',t)
Path('/tmp/index_js_check.js').write_text('\n'.join(scripts),encoding='utf-8')
