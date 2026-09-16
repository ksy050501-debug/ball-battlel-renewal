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

replace_once('<title>볼배틀 리뉴얼 v50</title>', '<title>볼배틀 리뉴얼 v51</title>', 'document title')
replace_once('<h1 id="mainTitle">볼배틀 리뉴얼 v50</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v51</h1>', 'visible title')

replace_once(
    'wallSegments: 6, wallHeal: 4, tourGain: 8, wallDamage: 5, domeGain: 7, gaugeMax: 100,',
    'wallSegments: 6, wallHeal: 6, tourGain: 8, fanDamage: 5, antiDamage: 5, domeGain: 7, gaugeMax: 100,',
    'Oshi wall values'
)

replace_once(
    'skillName: "팬이 되어줘! · 투어 · 도쿄돔", condition: "벽 24구간에 관객 후보 생성 · 먼저 닿는 쪽에 따라 팬/안티팬 확정", desc: "일반 벽을 보라색 관객 후보로 만든다. 최애가 먼저 다시 닿으면 분홍색 팬, 적이 먼저 닿으면 빨간색 안티팬이 된다. 팬은 회복과 투어를, 안티팬은 최애에게 피해와 도쿄돔을 준다." },',
    'skillName: "팬이 되어줘! · 투어 · 도쿄돔", condition: "벽 24구간에 관객 후보 생성 · 먼저 닿는 쪽에 따라 팬/안티팬 확정", desc: "보라색 관객 후보를 최애가 먼저 만나면 팬, 적이 먼저 만나면 안티팬이 된다. 팬 확정 즉시 회복과 투어를 얻고, 팬 벽은 적에게 피해를 준다. 안티팬 벽은 최애에게 피해와 도쿄돔을 준 뒤 다시 관객 후보로 돌아간다." },',
    'Oshi character description'
)

pattern = re.compile(r'''    function oshiWallEffectReady\(o, key\) \{.*?\n    \}\n    function oshiWallCollision\(f, wall, coordinate\) \{.*?\n    \}\n    function addOshiAftershock''', re.S)
new_block = r'''    function oshiWallEffectReady(o, key, actorId) {
      const effectKey = `${key}|${actorId}`;
      const last = o.wallLast.get(effectKey);
      return last == null || battleTime - last >= OSHI.wallEffectCooldown;
    }
    function markOshiWallEffect(o, key, actorId) {
      o.wallLast.set(`${key}|${actorId}`, battleTime);
    }
    function applyOshiFanBenefit(f, o) {
      const before = f.hp;
      f.hp = Math.min(f.maxHp, f.hp + OSHI.wallHeal);
      const healed = Math.max(0, f.hp - before);
      if (healed > 0) {
        f.healingDone = (f.healingDone || 0) + healed;
        spawnFloatingText(f.x, f.y - f.r - 20, "+" + healed, "#f9a8d4");
      }
      o.tour = Math.min(OSHI.gaugeMax, o.tour + OSHI.tourGain);
      spawnFloatingText(f.x, f.y - f.r - 36, `투어 +${OSHI.tourGain}`, "#f472b6");
      if (o.tour >= OSHI.gaugeMax && o.concert <= 0) startOshiTour(f);
    }
    function oshiWallCollision(f, wall, coordinate) {
      if (!f?.alive) return;
      const owners = fighters.filter(owner => owner.alive && owner.oshi);
      for (const owner of owners) {
        const o = owner.oshi;
        const key = oshiWallKey(wall, coordinate);
        const state = o.wallStates.get(key);
        if (owner === f) {
          if (!state) {
            o.wallStates.set(key, "candidate");
            if (!fastSimMode) {
              spawnParticles(f.x, f.y, "#a855f7", 7);
              spawnFloatingText(f.x, f.y - f.r - 18, "팬이 되어줘!", "#c084fc");
            }
            continue;
          }
          if (state === "candidate") {
            o.wallStates.set(key, "fan");
            o.wallClaimers.delete(key);
            markOshiWallEffect(o, key, owner.id);
            applyOshiFanBenefit(owner, o);
            if (!fastSimMode) {
              spawnParticles(f.x, f.y, "#f472b6", 8);
              spawnFloatingText(f.x, f.y - f.r - 18, "팬!", "#f9a8d4");
            }
            continue;
          }
          if (state === "fan") {
            if (!oshiWallEffectReady(o, key, owner.id)) continue;
            markOshiWallEffect(o, key, owner.id);
            applyOshiFanBenefit(owner, o);
          } else if (state === "anti") {
            if (!oshiWallEffectReady(o, key, owner.id)) continue;
            markOshiWallEffect(o, key, owner.id);
            const claimantId = o.wallClaimers.get(key);
            const source = fighters.find(e => e.id === claimantId) || owner;
            damage(owner, OSHI.antiDamage, source, "안티팬");
            o.dome = Math.min(OSHI.gaugeMax, o.dome + OSHI.domeGain);
            spawnFloatingText(owner.x, owner.y - owner.r - 34, `도쿄돔 +${OSHI.domeGain}`, "#ef4444");
            o.wallStates.set(key, "candidate");
            o.wallClaimers.delete(key);
            if (!fastSimMode) {
              spawnParticles(owner.x, owner.y, "#a855f7", 7);
              spawnFloatingText(owner.x, owner.y - owner.r - 18, "다시 관객 후보", "#c084fc");
            }
            if (o.dome >= OSHI.gaugeMax && owner.alive) triggerOshiDome(owner);
          }
        } else if (!f.isSummon && areEnemies(owner, f)) {
          if (state === "candidate") {
            o.wallStates.set(key, "anti");
            o.wallClaimers.set(key, f.id);
            if (!fastSimMode) {
              spawnParticles(f.x, f.y, "#ef4444", 8);
              spawnFloatingText(f.x, f.y - f.r - 18, "안티팬", "#f87171");
            }
          } else if (state === "fan") {
            if (!oshiWallEffectReady(o, key, f.id)) continue;
            markOshiWallEffect(o, key, f.id);
            damage(f, OSHI.fanDamage, owner, "팬덤");
            if (!fastSimMode) spawnFloatingText(f.x, f.y - f.r - 18, "팬덤!", "#f472b6");
          }
        }
      }
    }
    function addOshiAftershock'''
s, count = pattern.subn(new_block, s, count=1)
if count != 1:
    raise SystemExit(f'Oshi wall function block: expected 1 replacement, found {count}')

info_pattern = re.compile(r'''      if \(c\.id === "oshi"\) return \{ damage: .*? \};\n''')
new_info = '      if (c.id === "oshi") return { damage: "팬 벽 적 접촉 5 / 안티팬 벽 최애 접촉 5 / 투어 초당2 · 5초 연속 체류30 / 후유증: 체류 2초당 총3을 5초 DOT / 도쿄돔 자해35 + 출혈3×8", tick: "벽 한 면 6구간 · 팬 확정 즉시 HP+6·투어+8 / 팬 재접촉 HP+6·투어+8 / 안티팬 피격 후 관객 후보로 복귀", tip: "후보 생성 자체로는 투어 게이지를 얻지 않는다. 보라색 후보를 최애가 먼저 다시 만나면 팬, 적이 먼저 만나면 안티팬이 된다. 팬 벽은 적에게 피해를 주며, 안티팬 벽은 최애에게 피해와 도쿄돔 게이지를 준 뒤 보라색 후보로 돌아간다." };\n'
s, count = info_pattern.subn(new_info, s, count=1)
if count != 1:
    raise SystemExit(f'Oshi damage info: expected 1 replacement, found {count}')

marker = '    const patchNotes = [\n'
if s.count(marker) != 1:
    raise SystemExit('patchNotes marker missing or duplicated')
s = s.replace(marker, marker + '      "v51: 최애 팬덤 상호작용 조정. 관객 후보 생성 자체에는 투어 보상이 없으며, 팬 확정 순간 회복 6·투어 8을 즉시 1회 획득한다. 팬 벽에 적이 닿으면 피해 5, 안티팬 벽에서 최애가 피해 5와 도쿄돔 게이지를 받은 뒤 해당 벽은 보라색 관객 후보로 돌아간다.",\n', 1)

checks = [
    '<title>볼배틀 리뉴얼 v51</title>',
    '<h1 id="mainTitle">볼배틀 리뉴얼 v51</h1>',
    'wallHeal: 6', 'fanDamage: 5', 'antiDamage: 5',
    'applyOshiFanBenefit(owner, o);',
    'o.wallStates.set(key, "candidate");',
    'damage(f, OSHI.fanDamage, owner, "팬덤");',
    'v51: 최애 팬덤 상호작용 조정.'
]
for item in checks:
    if item not in s:
        raise SystemExit(f'missing postcondition: {item}')

path.write_text(s, encoding='utf-8')
