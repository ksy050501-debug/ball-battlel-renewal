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

replace_once('<title>볼배틀 리뉴얼 v49</title>', '<title>볼배틀 리뉴얼 v50</title>', 'document title')
replace_once('<h1 id="mainTitle">볼배틀 리뉴얼 v49</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v50</h1>', 'visible title')

old_char = '''      { id: "oshi", name: "최애", mark: "★", role: "애니", color: "#ec4899", hp: 170, attack: 0, speed: 2.7, range: 180,
        skillName: "분홍빛 투어 · 도쿄돔", condition: "벽 24구간 염색 · 분홍벽 접촉으로 서로 다른 두 게이지 축적", desc: "벽을 분홍색으로 물들인다. 분홍벽은 최애에게 회복과 투어를, 적에게 피해와 도쿄돔 게이지를 준다. 투어는 공연장 지속 피해, 도쿄돔은 최애 자신에게 큰 후유증을 남긴다." },'''
new_char = '''      { id: "oshi", name: "최애", mark: "★", role: "애니", color: "#ec4899", hp: 170, attack: 0, speed: 2.7, range: 180,
        skillName: "팬이 되어줘! · 투어 · 도쿄돔", condition: "벽 24구간에 관객 후보 생성 · 먼저 닿는 쪽에 따라 팬/안티팬 확정", desc: "일반 벽을 보라색 관객 후보로 만든다. 최애가 먼저 다시 닿으면 분홍색 팬, 적이 먼저 닿으면 빨간색 안티팬이 된다. 팬은 회복과 투어를, 안티팬은 최애에게 피해와 도쿄돔을 준다." },'''
replace_once(old_char, new_char, 'Oshi character card')

oshi_block = r'''    const OSHI = {
      wallSegments: 6, wallHeal: 4, tourGain: 8, wallDamage: 5, domeGain: 7, gaugeMax: 100,
      wallEffectCooldown: 2,
      concertDuration: 10, concertRadius: 135, concertDps: 2, concertStayTime: 5, concertStayDamage: 30,
      aftershockUnitSeconds: 2, aftershockUnitDamage: 3, aftershockDuration: 5,
      domeSelfDamage: 35, domeFreeze: 0.75, bleedDuration: 8, bleedDamage: 3
    };
    function initOshi(f) {
      f.oshi = {
        tour: 0, dome: 0,
        wallStates: new Map(), wallLast: new Map(), wallClaimers: new Map(),
        concert: 0, concertX: 0, concertY: 0, audience: new Map(),
        bleed: 0, bleedTick: 1, domeSceneUntil: 0
      };
    }
    function oshiWallKey(wall, coordinate) {
      const start = (wall === "left" || wall === "right") ? arena.y : arena.x;
      const segSize = arena.size / OSHI.wallSegments;
      const idx = clamp(Math.floor((coordinate - start) / segSize), 0, OSHI.wallSegments - 1);
      return `${wall}:${idx}`;
    }
    function startOshiTour(f) {
      const o = f.oshi;
      if (!o || o.concert > 0) return;
      o.tour = 0; o.dome = 0;
      o.concert = OSHI.concertDuration;
      o.concertX = f.x; o.concertY = f.y;
      o.audience = new Map();
      spawnBlast(f.x, f.y, OSHI.concertRadius, "#f472b6");
      spawnParticles(f.x, f.y, "#f9a8d4", 30);
      spawnFloatingText(f.x, f.y - f.r - 42, "투어 콘서트!", "#f9a8d4");
      playSound("magic", 1.0);
      log(`<strong>${escapeHtml(f.name)}</strong> 투어 콘서트 개막 · 반경 ${OSHI.concertRadius}`, "스킬");
    }
    function triggerOshiDome(f) {
      const o = f.oshi;
      if (!o) return;
      o.tour = 0; o.dome = 0;
      o.domeSceneUntil = performance.now() + 1400;
      triggerHitStop(OSHI.domeFreeze);
      screenShake = Math.max(screenShake, 0.55);
      spawnBlast(f.x, f.y, 105, "#7f1d1d");
      spawnFloatingText(f.x, f.y - f.r - 48, "돔 공연 축하해.", "#ef4444");
      playSound("explosion", 0.9);
      bodyDirectDamage(f, OSHI.domeSelfDamage, f, "도쿄돔 후유증", "#ef4444");
      if (f.alive) { o.bleed = OSHI.bleedDuration; o.bleedTick = 1; }
      log(`<strong>${escapeHtml(f.name)}</strong> 도쿄돔 · 자해 ${OSHI.domeSelfDamage} + ${OSHI.bleedDuration}초 출혈`, "스킬");
    }
    function oshiWallEffectReady(o, key) {
      const last = o.wallLast.get(key);
      return last == null || battleTime - last >= OSHI.wallEffectCooldown;
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
            if (!fastSimMode) {
              spawnParticles(f.x, f.y, "#f472b6", 8);
              spawnFloatingText(f.x, f.y - f.r - 18, "팬!", "#f9a8d4");
            }
            continue;
          }
          if (!oshiWallEffectReady(o, key)) continue;
          o.wallLast.set(key, battleTime);
          if (state === "fan") {
            const before = f.hp;
            f.hp = Math.min(f.maxHp, f.hp + OSHI.wallHeal);
            const healed = Math.max(0, f.hp - before);
            if (healed > 0) {
              f.healingDone = (f.healingDone || 0) + healed;
              spawnFloatingText(f.x, f.y - f.r - 20, "+" + healed, "#f9a8d4");
            }
            o.tour = Math.min(OSHI.gaugeMax, o.tour + OSHI.tourGain);
            spawnFloatingText(f.x, f.y - f.r - 36, `투어 +${OSHI.tourGain}`, "#f472b6");
            if (o.tour >= OSHI.gaugeMax && o.concert <= 0) startOshiTour(owner);
          } else if (state === "anti") {
            const claimantId = o.wallClaimers.get(key);
            const source = fighters.find(e => e.id === claimantId) || owner;
            damage(owner, OSHI.wallDamage, source, "안티팬");
            o.dome = Math.min(OSHI.gaugeMax, o.dome + OSHI.domeGain);
            spawnFloatingText(owner.x, owner.y - owner.r - 34, `도쿄돔 +${OSHI.domeGain}`, "#ef4444");
            if (o.dome >= OSHI.gaugeMax && owner.alive) triggerOshiDome(owner);
          }
        } else if (!f.isSummon && areEnemies(owner, f) && state === "candidate") {
          o.wallStates.set(key, "anti");
          o.wallClaimers.set(key, f.id);
          if (!fastSimMode) {
            spawnParticles(f.x, f.y, "#ef4444", 8);
            spawnFloatingText(f.x, f.y - f.r - 18, "안티팬", "#f87171");
          }
        }
      }
    }
    function addOshiAftershock(enemy, source, totalDamage) {
      totalDamage = Math.max(0, Math.round(totalDamage));
      if (!enemy?.alive || totalDamage <= 0) return;
      if (!enemy.oshiAftershocks) enemy.oshiAftershocks = [];
      enemy.oshiAftershocks.push({ source, remaining: totalDamage, ticksLeft: OSHI.aftershockDuration, timer: 1 });
      spawnFloatingText(enemy.x, enemy.y - enemy.r - 24, `후유증 ${totalDamage}`, "#f9a8d4");
    }
    function updateOshiAftershock(f, dt) {
      const effects = f.oshiAftershocks;
      if (!effects?.length || !f.alive) return;
      for (let i = effects.length - 1; i >= 0; i--) {
        const effect = effects[i];
        effect.timer -= dt;
        while (effect.timer <= 0 && effect.remaining > 0 && effect.ticksLeft > 0 && f.alive) {
          effect.timer += 1;
          const hit = Math.max(1, Math.ceil(effect.remaining / effect.ticksLeft));
          effect.remaining -= hit;
          effect.ticksLeft -= 1;
          damage(f, hit, effect.source || f, "후유증");
        }
        if (effect.remaining <= 0 || effect.ticksLeft <= 0 || !f.alive) effects.splice(i, 1);
      }
    }
    function finishOshiTour(f) {
      const o = f.oshi;
      if (!o) return;
      for (const [id, entry] of o.audience) {
        const enemy = fighters.find(e => e.id === id && e.alive);
        if (!enemy || entry.total <= 0) continue;
        const units = Math.round(entry.total / OSHI.aftershockUnitSeconds);
        const totalDamage = units * OSHI.aftershockUnitDamage;
        addOshiAftershock(enemy, f, totalDamage);
      }
      o.audience.clear();
      spawnFloatingText(f.x, f.y - f.r - 28, "투어 종료", "#fbcfe8");
    }
    function updateOshi(f, dt) {
      const o = f.oshi;
      if (!o || !f.alive) return;
      if (o.bleed > 0) {
        o.bleed = Math.max(0, o.bleed - dt);
        o.bleedTick -= dt;
        while (o.bleedTick <= 0 && f.alive) {
          o.bleedTick += 1;
          bodyDirectDamage(f, OSHI.bleedDamage, f, "도쿄돔 출혈", "#ef4444");
        }
      }
      if (o.concert <= 0) return;
      const before = o.concert;
      o.concert = Math.max(0, o.concert - dt);
      o.concertX = f.x; o.concertY = f.y;
      enemiesOf(f).forEach(enemy => {
        if (!enemy.alive) return;
        let entry = o.audience.get(enemy.id);
        if (!entry) { entry = { total: 0, streak: 0, tick: 0 }; o.audience.set(enemy.id, entry); }
        const inside = Math.hypot(enemy.x - f.x, enemy.y - f.y) <= OSHI.concertRadius + enemy.r;
        if (!inside) { entry.streak = 0; entry.tick = 0; return; }
        entry.total += dt; entry.streak += dt; entry.tick += dt;
        while (entry.tick >= 1 && enemy.alive) {
          entry.tick -= 1;
          damage(enemy, OSHI.concertDps, f, "투어 공연");
        }
        while (entry.streak >= OSHI.concertStayTime && enemy.alive) {
          entry.streak -= OSHI.concertStayTime;
          damage(enemy, OSHI.concertStayDamage, f, "5초 연속 관람");
          spawnBlast(enemy.x, enemy.y, 45, "#f472b6");
        }
      });
      if (before > 0 && o.concert <= 0) finishOshiTour(f);
    }
    function drawOshiArenaEffects() {
      fighters.filter(f => f.oshi).forEach(f => {
        const o = f.oshi;
        if (o.wallStates.size) {
          const seg = arena.size / OSHI.wallSegments;
          ctx.save(); ctx.lineWidth = 8; ctx.lineCap = "round";
          o.wallStates.forEach((state, key) => {
            const [wall, raw] = key.split(":"); const i = Number(raw); const a = i * seg + 5, b = (i + 1) * seg - 5;
            const color = state === "fan" ? "#f472b6" : state === "anti" ? "#ef4444" : "#a855f7";
            ctx.strokeStyle = color; ctx.shadowColor = color; ctx.shadowBlur = state === "candidate" ? 10 : 15;
            ctx.beginPath();
            if (wall === "top") { ctx.moveTo(arena.x + a, arena.y + 4); ctx.lineTo(arena.x + b, arena.y + 4); }
            else if (wall === "bottom") { ctx.moveTo(arena.x + a, arena.y2 - 4); ctx.lineTo(arena.x + b, arena.y2 - 4); }
            else if (wall === "left") { ctx.moveTo(arena.x + 4, arena.y + a); ctx.lineTo(arena.x + 4, arena.y + b); }
            else { ctx.moveTo(arena.x2 - 4, arena.y + a); ctx.lineTo(arena.x2 - 4, arena.y + b); }
            ctx.stroke();
          });
          ctx.restore();
        }
        if (o.concert > 0 && f.alive) {
          const pulse = 0.5 + 0.5 * Math.sin(battleTime * 8);
          ctx.save();
          ctx.beginPath(); ctx.rect(arena.x, arena.y, arena.size, arena.size); ctx.clip();
          ctx.fillStyle = `rgba(244,114,182,${0.08 + pulse * 0.04})`; ctx.strokeStyle = `rgba(249,168,212,${0.62 + pulse * 0.28})`; ctx.lineWidth = 5;
          ctx.beginPath(); ctx.arc(f.x, f.y, OSHI.concertRadius, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
          ctx.restore();
        }
      });
    }
    function drawOshiDomeOverlay() {'''

pattern = r'    const OSHI = \{.*?    function drawOshiDomeOverlay\(\) \{'
s2, n = re.subn(pattern, oshi_block, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'Oshi block replacement failed: {n}')
s = s2

old_info = '''      if (c.id === "oshi") return { damage: "분홍벽 적 접촉 5 / 투어 초당2 · 5초 연속 체류30 / 종료 후 누적 체류 1초당 1.5 / 도쿄돔 자해35 + 출혈3×8", tick: "벽 한 면 6구간 · 최애 분홍벽 접촉 HP+4·투어+8 / 적 접촉 도쿄돔+7", tip: "투어와 도쿄돔은 별도 게이지다. 하나가 발동하면 둘 다 0으로 초기화된다. 투어는 10초간 고정 공연장을 만들며, 도쿄돔은 0.75초 시간정지 연출 뒤 최애에게 자해와 출혈을 준다." };'''
new_info = '''      if (c.id === "oshi") return { damage: "안티팬 접촉 5 / 투어 초당2 · 5초 연속 체류30 / 후유증: 누적 체류 2초당 총3을 투어 종료 후 최대5초간 분할 / 도쿄돔 자해35 + 출혈3×8", tick: "벽 한 면 6구간 · 보라 관객 후보 → 최애 선접촉 팬 / 적 선접촉 안티팬 · 팬 접촉 HP+4·투어+8 · 안티팬 접촉 도쿄돔+7", tip: "팬/안티팬 벽은 확정 후 유지되며 효과는 같은 구간에서 2초마다 재발동한다. 투어는 10초 동안 최애를 따라다니는 반경135 공연장이다. 투어와 도쿄돔 중 하나가 발동하면 두 게이지는 모두 0이 된다." };'''
replace_once(old_info, new_info, 'Oshi damage info')

status_pattern = r'''      if \(f\.oshi\) \{.*?      \}\n      if \(f\.tano\) return'''
status_repl = '''      if (f.oshi) {
        const o = f.oshi;
        const counts = { candidate: 0, fan: 0, anti: 0 };
        o.wallStates.forEach(state => { if (counts[state] != null) counts[state]++; });
        return { ratio: clamp(o.tour / OSHI.gaugeMax, 0, 1), className: "skill-fill", text: o.concert > 0 ? `투어 공연 · ${o.concert.toFixed(1)}초` : `투어 ${Math.floor(o.tour)}/${OSHI.gaugeMax}`,
          extraBarsHtml: `<div class="bar" title="도쿄돔 게이지"><div class="bar-fill rage-fill" style="width:${clamp(o.dome / OSHI.gaugeMax, 0, 1) * 100}%"></div></div>`,
          extraTextHtml: `<div class="status-skill-label">도쿄돔 ${Math.floor(o.dome)}/${OSHI.gaugeMax}${o.bleed > 0 ? ` · 출혈 ${o.bleed.toFixed(1)}초` : ""} · 관객후보 ${counts.candidate} · 팬 ${counts.fan} · 안티팬 ${counts.anti}</div>` };
      }
      if (f.tano) return'''
s2, n = re.subn(status_pattern, status_repl, s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'Oshi status block replacement failed: {n}')
s = s2

old_update_head = '''    function updateFighter(f, dt) {
      if (!f.alive) return;
      if (f.duelMonster) updateDuelMonster(f, dt);'''
new_update_head = '''    function updateFighter(f, dt) {
      if (!f.alive) return;
      updateOshiAftershock(f, dt);
      if (!f.alive) return;
      if (f.duelMonster) updateDuelMonster(f, dt);'''
replace_once(old_update_head, new_update_head, 'updateFighter aftershock hook')

patch_anchor = '''    const patchNotes = [
      "v49:'''
patch_repl = '''    const patchNotes = [
      "v50: 최애 팬덤 벽을 재설계. 최애가 일반 벽을 보라색 관객 후보로 만들고, 다음 선접촉이 최애면 분홍 팬·적이면 빨간 안티팬으로 영구 확정된다. 팬은 2초마다 회복·투어, 안티팬은 2초마다 최애에게 피해·도쿄돔을 준다. 투어 반경을 180→135로 줄이고 공연장이 최애를 따라다니도록 변경. 투어 종료 후 후유증은 누적 체류 2초당 총3 피해를 최대 5초 동안 정수 도트 피해로 나눠 적용.",
      "v49:'''
replace_once(patch_anchor, patch_repl, 'v50 patch note')

# Sanity checks
checks = [
    '<title>볼배틀 리뉴얼 v50</title>',
    '<h1 id="mainTitle">볼배틀 리뉴얼 v50</h1>',
    'concertRadius: 135',
    'wallStates: new Map()',
    '"팬이 되어줘!"',
    'damage(f, hit, effect.source || f, "후유증")',
    'updateOshiAftershock(f, dt);',
    'v50: 최애 팬덤 벽을 재설계.'
]
for token in checks:
    if token not in s:
        raise SystemExit(f'missing postcondition: {token}')
if 'aftershockPerSecond: 1.5' in s:
    raise SystemExit('old decimal aftershock remains')

path.write_text(s, encoding='utf-8')
print('v50 Oshi update applied')
