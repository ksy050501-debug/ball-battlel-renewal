from pathlib import Path
import re

p = Path("index.html")
s = p.read_text(encoding="utf-8")
original = s


def replace_once(old, new, label):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f"{label}: expected 1 match, found {count}")
    s = s.replace(old, new, 1)


# Version.
replace_once("<title>볼배틀 리뉴얼 v46</title>", "<title>볼배틀 리뉴얼 v47</title>", "version")

# Lisa: sound-wave damage 9 -> 8.
replace_once(
    "const LISA = { patience: 40, idleDelay: 5, idleGain: 2, duration: 14, rageDuration: 4, rageRange: 190, period: 1.25, ragePeriod: 0.55, power: 9, range: 150, halfAngle: Math.PI / 4, speed: 2.7 };",
    "const LISA = { patience: 40, idleDelay: 5, idleGain: 2, duration: 14, rageDuration: 4, rageRange: 190, period: 1.25, ragePeriod: 0.55, power: 8, range: 150, halfAngle: Math.PI / 4, speed: 2.7 };",
    "LISA power",
)
replace_once(
    'if (c.id==="lisa") return {damage:"최근접 적 방향 90도 음파 9 · 록 사거리150 / 폭주190",tick:"인내: 받은 피해 40 또는 5초 무피격 뒤 초당2 / 록 14초",tip:"숙녀는 무공격. 피해를 받거나 5초 넘게 아무 피해도 없으면 인내가 오른다. 록 14초 중 마지막 4초는 이속 1.6배 폭주. 게이지 소진 시 숙녀 복귀."};',
    'if (c.id==="lisa") return {damage:"최근접 적 방향 90도 음파 8 · 록 사거리150 / 폭주190",tick:"인내: 받은 피해 40 또는 5초 무피격 뒤 초당2 / 록 14초",tip:"숙녀는 무공격. 피해를 받거나 5초 넘게 아무 피해도 없으면 인내가 오른다. 록 14초 중 마지막 4초는 이속 1.6배 폭주. 게이지 소진 시 숙녀 복귀."};',
    "Lisa tooltip",
)

# Iron Mask: JARVIS rebuild 8s -> 7s and Mark 42 fragments home after 2s.
replace_once(
    "const IRON = { hulkDamage: 8, hulkCooldown: 0.6, hulkKnock: 650, hulkWindup: 0.12, hulkFollow: 0.12, hp: 40, shield: 90, reShield: 30, rebuild: 8, beamPeriod: 3, beamDamage: 3, beamTick: 0.11,\n      dashPeriod: 8, dashDamage: 12, missilePeriod: 5.5, missileDamage: 8, fragmentDamage: 4, fragmentShield: 4 };",
    "const IRON = { hulkDamage: 8, hulkCooldown: 0.6, hulkKnock: 650, hulkWindup: 0.12, hulkFollow: 0.12, hp: 40, shield: 90, reShield: 30, rebuild: 7, beamPeriod: 3, beamDamage: 3, beamTick: 0.11,\n      dashPeriod: 8, dashDamage: 12, missilePeriod: 5.5, missileDamage: 8, fragmentDamage: 4, fragmentShield: 4, fragmentReturnDelay: 2, fragmentReturnSpeed: 260 };",
    "IRON constants",
)

old_fragment = '''      if (o.kind === "fragment") {
        o.age += dt;
        if (o.life <= 0) return false;
        if (o.age < 0.4) return true;
        const enemy = fighters.find(e => e.alive && areEnemies(o.owner, e) && dist(o, e) <= e.r + o.r && !(e.tano?.hidden > 0));
        if (enemy) { explodeIron(o, 30, IRON.fragmentDamage, "슈트 파편"); return false; }
        if (o.owner.iron.suit !== "naked" && dist(o, o.owner) <= o.owner.r + o.r) {
          const gain = Math.min(IRON.fragmentShield, o.owner.shieldMax - o.owner.shieldHp);
          o.owner.shieldHp += gain;
          spawnFloatingText(o.x, o.y, "슈트 +" + gain, "#7dd3fc"); return false;
        }
        return true;
      }'''
new_fragment = '''      if (o.kind === "fragment") {
        o.age += dt;
        if (o.life <= 0) return false;
        if (o.age < 0.4) return true;
        if (o.age >= IRON.fragmentReturnDelay) {
          const dx = o.owner.x - o.x, dy = o.owner.y - o.y, d = Math.hypot(dx, dy) || 1;
          const step = Math.min(d, IRON.fragmentReturnSpeed * dt);
          o.x += dx / d * step;
          o.y += dy / d * step;
        }
        const enemy = fighters.find(e => e.alive && areEnemies(o.owner, e) && dist(o, e) <= e.r + o.r && !(e.tano?.hidden > 0));
        if (enemy) { explodeIron(o, 30, IRON.fragmentDamage, "슈트 파편"); return false; }
        if (o.owner.iron.suit !== "naked" && dist(o, o.owner) <= o.owner.r + o.r) {
          const gain = Math.min(IRON.fragmentShield, o.owner.shieldMax - o.owner.shieldHp);
          o.owner.shieldHp += gain;
          spawnFloatingText(o.x, o.y, "슈트 +" + gain, "#7dd3fc"); return false;
        }
        return true;
      }'''
replace_once(old_fragment, new_fragment, "Mark42 fragment return")
replace_once(
    'if (c.id === "iron_mask") return { damage: "리펄서 10 · 부스터 12 · 미사일 8×3 · 헐크 충돌강타8 · 파편 4", tick: "리펄서 3초 / 부스터 8초 / 미사일 5.5초 / 재장착 8초", tip: "체력 30·첫 보호막 70, 재장착 50(체력 회복 없음). 몸에 연결된 굵은 빔. 조준각 고정·0.45초 예고 후 0.55초 발사, 1회당 대상별 피해 10. 헐크버스터는 적과 충돌하면 강타8·넉백. 빔 벽 반사 2회. 미사일 사거리 420·폭발 반경 55. 파편 회복 4·8초 유지. 슈트는 무작위." };',
    'if (c.id === "iron_mask") return { damage: "리펄서 10 · 부스터 12 · 미사일 8×3 · 헐크 충돌강타8 · 파편 4", tick: "리펄서 3초 / 부스터 8초 / 미사일 5.5초 / 재장착 7초", tip: "체력 40·첫 보호막 90, 재장착 보호막 30(체력 회복 없음). 몸에 연결된 굵은 빔. 조준각 고정·0.45초 예고 후 0.55초 발사. 헐크버스터는 적과 충돌하면 강타8·넉백. 빔 벽 반사 2회. 미사일 사거리 420·폭발 반경 55. 마크42 파편은 피해/보호막 회복 4이며 생성 2초 뒤 철가면에게 자동 귀환한다. 슈트는 무작위." };',
    "Iron tooltip",
)

# Tano: power stone guaranteed within first three; time stone repeats every 90s while held.
replace_once(
    "const TANO = { lossPeriod: 2, lossDamage: 10, spawn: 9, pickupBonus: 34, power: 8, spacePeriod: 8, spaceDuration: 3, mindPeriod: 10, mindDuration: 1.5, realityPeriod: 12, realityDuration: 2.5 };",
    "const TANO = { lossPeriod: 2, lossDamage: 10, spawn: 9, pickupBonus: 34, power: 8, spacePeriod: 8, spaceDuration: 3, mindPeriod: 10, mindDuration: 1.5, realityPeriod: 12, realityDuration: 2.5, timePeriod: 90 };",
    "TANO constants",
)

old_init = '''    function initTano(f) {
      f.tano = { stones: [], order: [...stoneTypes.slice(0, 5)].sort(() => Math.random() - 0.5).concat(stoneTypes[5]),
        next: TANO.spawn, drops: [], spawned: 0, history: [], space: 0, mind: 0, reality: 0, hidden: 0, reform: 0, lossClock: 0, snapped: false };
    }'''
new_init = '''    function makeTanoOrder() {
      const power = stoneTypes.find(s => s.id === "power");
      const others = stoneTypes.slice(0, 5).filter(s => s.id !== "power").sort(() => Math.random() - 0.5);
      others.splice(Math.floor(Math.random() * 3), 0, power);
      return others.concat(stoneTypes[5]);
    }
    function initTano(f) {
      f.tano = { stones: [], order: makeTanoOrder(),
        next: TANO.spawn, drops: [], spawned: 0, history: [], space: 0, mind: 0, reality: 0, timeCd: 0, hidden: 0, reform: 0, lossClock: 0, snapped: false };
    }'''
replace_once(old_init, new_init, "Tano order/init")

# Extract the old one-shot time-stone block and replace it with a reusable helper + cooldown start.
old_time_block = '''      if (stone.id === "time" && t.history.length) {
        const past = t.history.find(h => h.time >= battleTime - 10) || t.history[0];
        f.x = clamp(past.x, arena.x + f.r, arena.x2 - f.r);
        f.y = clamp(past.y, arena.y + f.r, arena.y2 - f.r);
        const healed = Math.max(0, past.hp - f.hp);
        f.hp = Math.min(f.maxHp, Math.max(f.hp, past.hp));
        f.healingDone = (f.healingDone || 0) + healed;
        spawnBlast(f.x, f.y, 90, "#22c55e");
        spawnFloatingText(f.x, f.y - 55, "10초 전으로 · +" + Math.round(healed), "#22c55e");
      }'''
replace_once(
    "\n\n    function collectTanoStone(f, stone) {",
    '''\n\n    function triggerTanoTimeStone(f) {
      const t = f.tano;
      if (!t?.history.length) return false;
      const past = t.history.find(h => h.time >= battleTime - 10) || t.history[0];
      f.x = clamp(past.x, arena.x + f.r, arena.x2 - f.r);
      f.y = clamp(past.y, arena.y + f.r, arena.y2 - f.r);
      const healed = Math.max(0, past.hp - f.hp);
      f.hp = Math.min(f.maxHp, Math.max(f.hp, past.hp));
      f.healingDone = (f.healingDone || 0) + healed;
      spawnBlast(f.x, f.y, 90, "#22c55e");
      spawnFloatingText(f.x, f.y - 55, "10초 전으로 · +" + Math.round(healed), "#22c55e");
      return true;
    }

    function collectTanoStone(f, stone) {''',
    "Time helper insertion",
)
replace_once(old_time_block, '      if (stone.id === "time") { triggerTanoTimeStone(f); t.timeCd = TANO.timePeriod; }', "Time stone collection")

replace_once(
    "      while (t.history.length > 1 && t.history[1].time < battleTime - 10) t.history.shift();\n      const wasHidden = t.hidden > 0;",
    '''      while (t.history.length > 1 && t.history[1].time < battleTime - 10) t.history.shift();
      if (t.stones.includes("time") && !t.snapped) {
        t.timeCd = Math.max(0, (t.timeCd || 0) - dt);
        if (t.timeCd <= 0) {
          triggerTanoTimeStone(f);
          t.timeCd = TANO.timePeriod;
        }
      } else if (!t.stones.includes("time")) {
        t.timeCd = 0;
      }
      const wasHidden = t.hidden > 0;''',
    "Time cooldown update",
)

replace_once(
    "          t.order = [...stoneTypes.slice(0, 5)].sort(() => Math.random() - 0.5).concat(stoneTypes[5]);",
    "          t.order = makeTanoOrder();",
    "Tano reset order",
)

replace_once(
    'if (c.id === "tano") return { damage: "충돌 강펀치 8 + 넉백 중 벽 접촉마다 8 · 핑거플립 적 최대 HP 50% 고정 피해", tick: "스톤 9초 / 핑거플립 시간정지 0.75초", tip: "파워: 충돌 시 0.12초 정지 후 피해 8·강한 넉백. 스톤 6개 완성 시 시간을 0.75초 멈추고 핑거플립. 이후 2초마다 스톤 1개 소실·자해 10." };',
    'if (c.id === "tano") return { damage: "충돌 강펀치 8 + 넉백 중 벽 접촉마다 8 · 핑거플립 적 최대 HP 50% 고정 피해", tick: "스톤 9초 / 타임 재사용 90초 / 핑거플립 시간정지 0.75초", tip: "파워스톤은 최초 3개 안에 등장한다. 타임스톤은 획득 즉시 10초 전 상태를 회복하고, 보유 중 90초마다 다시 발동한다. 스톤 6개 완성 시 시간을 0.75초 멈추고 핑거플립. 이후 2초마다 스톤 1개 소실·자해 10." };',
    "Tano tooltip",
)

old_tano_status = '''        extraTextHtml: '<div class="status-skill-label">' + stoneTypes.filter(s => f.tano.stones.includes(s.id)).map(s => s.name).join(" · ") + (f.tano.hidden > 0 ? " · 무적" : "") + '</div>' };'''
new_tano_status = '''        extraTextHtml: '<div class="status-skill-label">' + stoneTypes.filter(s => f.tano.stones.includes(s.id)).map(s => s.name).join(" · ") + (f.tano.stones.includes("time") && !f.tano.snapped ? ` · 타임 ${Math.ceil(f.tano.timeCd || 0)}초` : "") + (f.tano.hidden > 0 ? " · 무적" : "") + '</div>' };'''
replace_once(old_tano_status, new_tano_status, "Tano status cooldown")

# Patch note.
marker = "    const patchNotes = [\n"
note = '      "v47: 리사 음파 피해 9→8. 철가면 자비스 재장착 8→7초, 마크42 파편은 생성 2초 뒤 철가면을 추적해 귀환. 타노는 파워스톤이 최초 3개 안에 반드시 등장하며, 타임스톤은 획득 즉시 효과 후 보유 중 90초마다 10초 전 상태 회귀를 재사용.",\n'
if marker not in s:
    raise SystemExit("patchNotes anchor not found")
s = s.replace(marker, marker + note, 1)

if s == original:
    raise SystemExit("no changes produced")

p.write_text(s, encoding="utf-8")
print("v47 balance patch applied")
