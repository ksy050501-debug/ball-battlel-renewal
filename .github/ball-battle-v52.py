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

replace_once('<title>볼배틀 리뉴얼 v51</title>', '<title>볼배틀 리뉴얼 v52</title>', 'document title')
replace_once('<h1 id="mainTitle">볼배틀 리뉴얼 v51</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v52</h1>', 'visible title')

old = '''          } else if (state === "fan") {
            if (!oshiWallEffectReady(o, key, f.id)) continue;
            markOshiWallEffect(o, key, f.id);
            damage(f, OSHI.fanDamage, owner, "팬덤");
            if (!fastSimMode) spawnFloatingText(f.x, f.y - f.r - 18, "팬덤!", "#f472b6");
          }'''
new = '''          } else if (state === "fan") {
            if (!oshiWallEffectReady(o, key, f.id)) continue;
            markOshiWallEffect(o, key, f.id);
            damage(f, OSHI.fanDamage, owner, "팬덤");
            o.wallStates.set(key, "candidate");
            o.wallClaimers.delete(key);
            if (!fastSimMode) {
              spawnParticles(f.x, f.y, "#a855f7", 7);
              spawnFloatingText(f.x, f.y - f.r - 18, "팬덤! → 관객 후보", "#c084fc");
            }
          }'''
replace_once(old, new, 'fan wall enemy contact')

# Update Oshi tooltip text without depending on the entire long line.
s, n = re.subn(
    r'(if \(c\.id === "oshi"\) return \{ damage: ")([^"]*)(", tick: ")([^"]*)(", tip: ")([^"]*)(" \};)',
    lambda m: m.group(1) + m.group(2) + m.group(3) + m.group(4) + m.group(5) + '후보 생성 자체로는 투어 게이지를 얻지 않는다. 팬 확정 순간 회복과 투어를 즉시 얻는다. 팬 벽은 적에게 피해를 준 뒤 보라색 관객 후보로 돌아가며, 안티팬 벽도 최애에게 피해와 도쿄돔 게이지를 준 뒤 관객 후보로 돌아간다.' + m.group(7),
    s,
    count=1
)
if n != 1:
    raise SystemExit(f'Oshi tooltip: expected 1 replacement, found {n}')

marker = '    const patchNotes = [\n'
if s.count(marker) != 1:
    raise SystemExit('patchNotes marker missing or duplicated')
s = s.replace(marker, marker + '      "v52: 최애 팬 벽 일회성 공격으로 조정. 분홍색 팬 벽에 적이 닿아 팬덤 피해를 받으면 해당 벽은 즉시 보라색 관객 후보로 돌아간다. 팬 확정 회복 6·투어 8과 기존 투어·후유증·도쿄돔 수치는 유지.",\n', 1)

checks = [
    '<title>볼배틀 리뉴얼 v52</title>',
    '<h1 id="mainTitle">볼배틀 리뉴얼 v52</h1>',
    'damage(f, OSHI.fanDamage, owner, "팬덤");\n            o.wallStates.set(key, "candidate");',
    '팬덤! → 관객 후보',
    'v52: 최애 팬 벽 일회성 공격으로 조정.'
]
for item in checks:
    if item not in s:
        raise SystemExit(f'missing postcondition: {item}')

path.write_text(s, encoding='utf-8')
