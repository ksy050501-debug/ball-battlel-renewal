from pathlib import Path
import re

path = Path('index.html')
s = path.read_text(encoding='utf-8')

def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 occurrence, found {count}')
    s = s.replace(old, new, 1)

replace_once('<title>볼배틀 리뉴얼 v52</title>', '<title>볼배틀 리뉴얼 v53</title>', 'document title')
replace_once('<h1 id="mainTitle">볼배틀 리뉴얼 v52</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v53</h1>', 'visible title')
replace_once(
    'wallSegments: 6, wallHeal: 6, tourGain: 8, fanDamage: 5, antiDamage: 5, domeGain: 7, gaugeMax: 100,',
    'wallSegments: 6, wallHeal: 6, tourGain: 8, fanDamage: 5, antiDamage: 4, domeGain: 7, gaugeMax: 100,',
    'anti-fan damage value'
)

# Update the character tooltip text only; mechanics are driven by OSHI.antiDamage above.
s, count = re.subn(
    r'(if \(c\.id === "oshi"\) return \{ damage: "팬 벽 적 접촉 5 / 안티팬 벽 최애 접촉 )5( / 투어)',
    r'\g<1>4\g<2>',
    s,
    count=1
)
if count != 1:
    raise SystemExit(f'Oshi damage tooltip: expected 1 replacement, found {count}')

marker = '    const patchNotes = [\n'
if s.count(marker) != 1:
    raise SystemExit('patchNotes marker missing or duplicated')
s = s.replace(
    marker,
    marker + '      "v53: 최애 미세 버프. 안티팬 벽에 최애가 닿을 때 받는 피해를 5→4로 낮췄다. 팬 회복·팬 피해·투어·후유증·도쿄돔 수치는 유지한다.",\n',
    1
)

checks = [
    '<title>볼배틀 리뉴얼 v53</title>',
    '<h1 id="mainTitle">볼배틀 리뉴얼 v53</h1>',
    'antiDamage: 4',
    '안티팬 벽 최애 접촉 4',
    'v53: 최애 미세 버프.'
]
for item in checks:
    if item not in s:
        raise SystemExit(f'missing postcondition: {item}')

path.write_text(s, encoding='utf-8')
