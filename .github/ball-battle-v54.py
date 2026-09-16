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

def replace_count(old, new, expected, label):
    global s
    count = s.count(old)
    if count != expected:
        raise SystemExit(f'{label}: expected {expected} occurrences, found {count}')
    s = s.replace(old, new)

replace_once('<title>볼배틀 리뉴얼 v53</title>', '<title>볼배틀 리뉴얼 v54</title>', 'document title')
replace_once('<h1 id="mainTitle">볼배틀 리뉴얼 v53</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v54</h1>', 'visible title')

# 최애 카드 설명을 벽/회복형에서 노래-인지도-투어-돔 공연형으로 교체한다.
old_card = '''      { id: "oshi", name: "최애", mark: "★", role: "애니", color: "#ec4899", hp: 170, attack: 0, speed: 2.7, range: 180,
        skillName: "팬이 되어줘! · 투어 · 도쿄돔", condition: "벽 24구간에 관객 후보 생성 · 먼저 닿는 쪽에 따라 팬/안티팬 확정", desc: "보라색 관객 후보를 최애가 먼저 만나면 팬, 적이 먼저 만나면 안티팬이 된다. 팬 확정 즉시 회복과 투어를 얻고, 팬 벽은 적에게 피해를 준다. 안티팬 벽은 최애에게 피해와 도쿄돔을 준 뒤 다시 관객 후보로 돌아간다." },'''
new_card = '''      { id: "oshi", name: "최애", mark: "★", role: "애니", color: "#ec4899", hp: 170, attack: 0, speed: 2.7, range: 180,
        skillName: "노래 · 인지도 · 투어 · 돔 공연", condition: "노래 적중·적 접촉으로 인지도 100 → 투어 · 3회 투어 뒤 다음 100은 돔 공연", desc: "2초마다 주변에 원형 노래를 부르며 노래는 점점 넓고 강해진다. 노래에 맞은 적은 3초간 느려지고 최애에게 주는 모든 피해가 감소한다. 투어를 거칠수록 다음 노래의 최소 단계가 상승하며, 네 번째 공연은 도쿄돔으로 바뀐다." },'''
replace_once(old_card, new_card, 'Oshi character card')

# 최애 전투 로직 전체를 단순한 노래/인지도/투어/도쿄돔 흐름으로 교체한다.
pattern = re.compile(r'''    const OSHI = \{.*?\n    function drawOshiCharacter\(f\) \{''', re.S)
new_block = r'''    const OSHI = {
      gaugeMax: 100,
      songPeriod: 2,
      songFameGain: 10,
      contactFameGain: 4,
      contactFameCooldown: 1,
      songLevels: [
        { radius: 90, damage: 3 },
        { radius: 110, damage: 4 },
        { radius: 130, damage: 5 },
        { radius: 150, damage: 6 }
      ],
      debuffDuration: 3,
      damageMultiplier: 0.8,
      slowMultiplier: 0.8,
      concertDuration: 10,
      concertRadius: 135,
      concertDps: 2,
      concertStayTime: 5,
      concertStayDamage: 30,
      aftershockUnitSeconds: 2,
      aftershockUnitDamage: 3,
      aftershockDuration: 5,
      domeSelfDamage: 35,
      domeFreeze: 0.75,
      bleedDuration: 8,
      bleedDamage: 3,
      encoreDuration: 8,
      encoreRadius: 175,
      encoreDps: 4,
      encoreStayDamage: 40
    };

    function initOshi(f) {
      f.oshi = {
        fame: 0,
        songTimer: OSHI.songPeriod,
        songLevel: 0,
        minSongLevel: 0,
        toursCompleted: 0,
        domeDone: false,
        concert: 0,
        concertX: 0,
        concertY: 0,
        audience: new Map(),
        contactLast: new Map(),
        isDome: false,
        encore: false,
        bleed: 0,
        bleedTick: 1,
        domeSceneUntil: 0
      };
    }

    // v54부터 최애는 벽을 사용하지 않는다. 기존 벽 충돌 호출부와의 호환을 위한 no-op.
    function oshiWallCollision() {}

    function updateOshiSongDebuffs(f, dt) {
      const debuffs = f?.oshiSongDebuffs;
      if (!(debuffs instanceof Map) || debuffs.size === 0) return;
      for (const [sourceId, time] of [...debuffs.entries()]) {
        const next = time - dt;
        if (next <= 0) debuffs.delete(sourceId);
        else debuffs.set(sourceId, next);
      }
    }

    function oshiSongSlowMultiplier(f) {
      const debuffs = f?.oshiSongDebuffs;
      if (!(debuffs instanceof Map) || debuffs.size === 0) return 1;
      for (const time of debuffs.values()) if (time > 0) return OSHI.slowMultiplier;
      return 1;
    }

    function applyOshiSongDebuff(target, source) {
      if (!target?.alive || !source?.alive) return;
      if (!(target.oshiSongDebuffs instanceof Map)) target.oshiSongDebuffs = new Map();
      target.oshiSongDebuffs.set(source.id, OSHI.debuffDuration);
      if (!fastSimMode) spawnFloatingText(target.x, target.y - target.r - 28, "노래 디버프", "#f9a8d4");
    }

    // 노래 디버프에 걸린 공격자가 해당 최애에게 주는 모든 피해를 20% 줄인다.
    // 소수 피해가 생기지 않도록 정수 반올림하며, 감소 뒤에도 최소 피해는 1이다.
    function oshiReducedIncomingDamage(target, amount, source) {
      if (!(amount > 0) || !target?.oshi || !source || source === target) return amount;
      const debuffs = source.oshiSongDebuffs;
      const remaining = debuffs instanceof Map ? (debuffs.get(target.id) || 0) : 0;
      if (remaining <= 0) return amount;
      return Math.max(1, Math.round(amount * OSHI.damageMultiplier));
    }

    function gainOshiFame(f, amount, text = "") {
      const o = f?.oshi;
      if (!o || !f.alive || o.concert > 0 || amount <= 0) return;
      const before = o.fame;
      o.fame = Math.min(OSHI.gaugeMax, o.fame + amount);
      const gained = Math.max(0, o.fame - before);
      if (gained > 0 && !fastSimMode && text) spawnFloatingText(f.x, f.y - f.r - 38, text, "#f472b6");
      if (o.fame >= OSHI.gaugeMax && o.concert <= 0) {
        const dome = o.toursCompleted >= 3 && !o.domeDone;
        startOshiTour(f, dome);
      }
    }

    function recordOshiContact(f, enemy) {
      const o = f?.oshi;
      if (!o || !f.alive || !enemy?.alive || o.concert > 0 || !areEnemies(f, enemy)) return;
      const last = o.contactLast.get(enemy.id);
      if (last != null && battleTime - last < OSHI.contactFameCooldown) return;
      o.contactLast.set(enemy.id, battleTime);
      gainOshiFame(f, OSHI.contactFameGain, `인지도 +${OSHI.contactFameGain}`);
    }

    function performOshiSong(f) {
      const o = f?.oshi;
      if (!o || !f.alive || o.concert > 0) return;
      const level = clamp(Math.max(o.minSongLevel, o.songLevel), 0, OSHI.songLevels.length - 1);
      const spec = OSHI.songLevels[level];
      let hits = 0;
      enemiesOf(f).forEach(enemy => {
        if (!enemy.alive) return;
        if (Math.hypot(enemy.x - f.x, enemy.y - f.y) > spec.radius + enemy.r) return;
        const dealt = damage(enemy, spec.damage, f, `노래 ${level + 1}단계`);
        if (dealt <= 0) return;
        hits += 1;
        applyOshiSongDebuff(enemy, f);
        if (!fastSimMode) spawnHitFlash(enemy.x, enemy.y, "#f9a8d4", 24 + level * 5);
      });
      if (!fastSimMode) {
        spawnBlast(f.x, f.y, spec.radius, level >= 3 ? "#ec4899" : "#f9a8d4");
        spawnParticles(f.x, f.y, level >= 3 ? "#f472b6" : "#fbcfe8", 10 + level * 4);
        spawnFloatingText(f.x, f.y - f.r - 24, `노래 ${level + 1}단계`, "#f9a8d4");
      }
      o.songLevel = Math.min(OSHI.songLevels.length - 1, level + 1);
      if (hits > 0) gainOshiFame(f, hits * OSHI.songFameGain, `인지도 +${hits * OSHI.songFameGain}`);
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

    function startOshiTour(f, dome = false) {
      const o = f?.oshi;
      if (!o || !f.alive || o.concert > 0) return;
      o.fame = 0;
      o.audience = new Map();
      o.isDome = !!dome;
      o.encore = false;

      if (dome) {
        o.domeDone = true;
        o.domeSceneUntil = performance.now() + 1400;
        triggerHitStop(OSHI.domeFreeze);
        screenShake = Math.max(screenShake, 0.55);
        spawnBlast(f.x, f.y, 105, "#7f1d1d");
        spawnFloatingText(f.x, f.y - f.r - 48, "돔 공연 축하해.", "#ef4444");
        playSound("explosion", 0.9);
        bodyDirectDamage(f, OSHI.domeSelfDamage, f, "도쿄돔 칼 피해", "#ef4444");
        if (!f.alive) return;
        o.bleed = OSHI.bleedDuration;
        o.bleedTick = 1;
        log(`<strong>${escapeHtml(f.name)}</strong> 도쿄돔 개막 · 칼 피해 ${OSHI.domeSelfDamage} + ${OSHI.bleedDuration}초 출혈`, "스킬");
      }

      o.concert = OSHI.concertDuration;
      o.concertX = f.x;
      o.concertY = f.y;
      spawnBlast(f.x, f.y, OSHI.concertRadius, dome ? "#ef4444" : "#f472b6");
      spawnParticles(f.x, f.y, dome ? "#fecaca" : "#f9a8d4", 30);
      spawnFloatingText(f.x, f.y - f.r - 42, dome ? "도쿄돔 투어!" : "투어 콘서트!", dome ? "#f87171" : "#f9a8d4");
      playSound("magic", 1.0);
      if (!dome) log(`<strong>${escapeHtml(f.name)}</strong> 투어 콘서트 개막 · 반경 ${OSHI.concertRadius}`, "스킬");
    }

    function startOshiEncore(f) {
      const o = f?.oshi;
      if (!o || !f.alive || !o.isDome || o.encore || o.concert <= 0) return;
      o.encore = true;
      o.concert += OSHI.encoreDuration;
      spawnBlast(f.x, f.y, OSHI.encoreRadius, "#fb7185");
      spawnParticles(f.x, f.y, "#fecdd3", 36);
      spawnFloatingText(f.x, f.y - f.r - 52, "공연 연장!", "#fecaca");
      playSound("magic", 1.35);
      log(`<strong>${escapeHtml(f.name)}</strong> 출혈 생존 · 도쿄돔 공연 연장`, "스킬");
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
      const wasDome = o.isDome;
      o.audience.clear();
      o.toursCompleted += 1;
      o.minSongLevel = Math.min(OSHI.songLevels.length - 1, o.toursCompleted);
      o.songLevel = o.minSongLevel;
      o.songTimer = OSHI.songPeriod;
      o.isDome = false;
      o.encore = false;
      spawnFloatingText(f.x, f.y - f.r - 28, `${wasDome ? "도쿄돔" : "투어"} 종료 · 노래 ${o.minSongLevel + 1}단계부터`, "#fbcfe8");
    }

    function updateOshi(f, dt) {
      const o = f.oshi;
      if (!o || !f.alive) return;

      if (o.bleed > 0) {
        const wasBleeding = o.bleed > 0;
        o.bleed = Math.max(0, o.bleed - dt);
        o.bleedTick -= dt;
        while (o.bleedTick <= 0 && f.alive) {
          o.bleedTick += 1;
          bodyDirectDamage(f, OSHI.bleedDamage, f, "도쿄돔 출혈", "#ef4444");
        }
        if (wasBleeding && o.bleed <= 0 && f.alive && o.isDome && o.concert > 0) startOshiEncore(f);
      }
      if (!f.alive) return;

      if (o.concert > 0) {
        const before = o.concert;
        o.concert = Math.max(0, o.concert - dt);
        o.concertX = f.x;
        o.concertY = f.y;
        const radius = o.encore ? OSHI.encoreRadius : OSHI.concertRadius;
        const dps = o.encore ? OSHI.encoreDps : OSHI.concertDps;
        const stayDamage = o.encore ? OSHI.encoreStayDamage : OSHI.concertStayDamage;
        enemiesOf(f).forEach(enemy => {
          if (!enemy.alive) return;
          let entry = o.audience.get(enemy.id);
          if (!entry) { entry = { total: 0, streak: 0, tick: 0 }; o.audience.set(enemy.id, entry); }
          const inside = Math.hypot(enemy.x - f.x, enemy.y - f.y) <= radius + enemy.r;
          if (!inside) { entry.streak = 0; entry.tick = 0; return; }
          entry.total += dt;
          entry.streak += dt;
          entry.tick += dt;
          while (entry.tick >= 1 && enemy.alive) {
            entry.tick -= 1;
            damage(enemy, dps, f, o.encore ? "도쿄돔 연장 공연" : "투어 공연");
          }
          while (entry.streak >= OSHI.concertStayTime && enemy.alive) {
            entry.streak -= OSHI.concertStayTime;
            damage(enemy, stayDamage, f, o.encore ? "도쿄돔 5초 연속 관람" : "5초 연속 관람");
            spawnBlast(enemy.x, enemy.y, 45, o.encore ? "#ef4444" : "#f472b6");
          }
        });
        if (before > 0 && o.concert <= 0) finishOshiTour(f);
        return;
      }

      o.songTimer -= dt;
      while (o.songTimer <= 0 && f.alive && o.concert <= 0) {
        o.songTimer += OSHI.songPeriod;
        performOshiSong(f);
      }
    }

    function drawOshiArenaEffects() {
      fighters.filter(f => f.oshi && f.alive).forEach(f => {
        const o = f.oshi;
        if (o.concert <= 0) return;
        const pulse = 0.5 + 0.5 * Math.sin(battleTime * 8);
        const radius = o.encore ? OSHI.encoreRadius : OSHI.concertRadius;
        ctx.save();
        ctx.beginPath(); ctx.rect(arena.x, arena.y, arena.size, arena.size); ctx.clip();
        ctx.fillStyle = o.encore ? `rgba(239,68,68,${0.10 + pulse * 0.05})` : `rgba(244,114,182,${0.08 + pulse * 0.04})`;
        ctx.strokeStyle = o.encore ? `rgba(248,113,113,${0.72 + pulse * 0.24})` : `rgba(249,168,212,${0.62 + pulse * 0.28})`;
        ctx.lineWidth = o.encore ? 7 : 5;
        ctx.beginPath(); ctx.arc(f.x, f.y, radius, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
        ctx.restore();
      });
    }

    function drawOshiDomeOverlay() {
      const now = performance.now();
      const host = fighters.find(f => f.oshi && f.oshi.domeSceneUntil > now);
      if (!host) return;
      const remain = clamp((host.oshi.domeSceneUntil - now) / 1400, 0, 1);
      ctx.save();
      ctx.fillStyle = `rgba(0,0,0,${0.48 + remain * 0.28})`; ctx.fillRect(arena.x, arena.y, arena.size, arena.size);
      ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.font = "900 46px Georgia, serif";
      ctx.shadowColor = "#7f1d1d"; ctx.shadowBlur = 24; ctx.fillStyle = "#dc2626";
      ctx.fillText("돔 공연 축하해.", arena.x + arena.size / 2, arena.y + arena.size / 2);
      ctx.restore();
    }

    function drawOshiCharacter(f) {'''
s, count = pattern.subn(new_block, s, count=1)
if count != 1:
    raise SystemExit(f'Oshi logic block: expected 1 replacement, found {count}')

# 전역 피해 처리: 노래 디버프가 걸린 공격자가 그 최애에게 가하는 일반/직접 피해를 모두 감소시킨다.
damage_pattern = re.compile(r'''(    function damage\(target, amount, source, reason = "공격"\) \{\n      if \(!target.*?\n      if \(tryHeroLeonGuardBlock\(target, reason\)\) return 0;\n)(      if \(target\.iron\) \{)''', re.S)
s, count = damage_pattern.subn(r'''\1      amount = oshiReducedIncomingDamage(target, amount, source);\n\2''', s, count=1)
if count != 1:
    raise SystemExit(f'damage reduction hook: expected 1 replacement, found {count}')

body_pattern = re.compile(r'''(    function bodyDirectDamage\(target, amount, source, reason = "직접피해", color = "#fb923c"\) \{.*?\n      if \(tryHeroLeonGuardBlock\(target, reason\)\) return 0;\n)(      if \(target\.iron\) \{)''', re.S)
s, count = body_pattern.subn(r'''\1      amount = oshiReducedIncomingDamage(target, amount, source);\n\2''', s, count=1)
if count != 1:
    raise SystemExit(f'bodyDirectDamage reduction hook: expected 1 replacement, found {count}')

# 푸른 눈/융합룡 및 오벨리스크의 실제 소환수를 피해 source로 넘겨, 해당 소환수가 노래에 맞았을 때 피해 감소가 적용되게 한다.
replace_once('damage(e,b.tickPower,owner||dragon,"버스트 스트림 다단")', 'damage(e,b.tickPower,dragon,"버스트 스트림 다단")', 'Blue-Eyes stream source')
replace_once('const dealt=damage(e,4,owner||dragon,"얼티메이트 버스트 다단")', 'const dealt=damage(e,4,dragon,"얼티메이트 버스트 다단")', 'Ultimate dragon source')
replace_once('damage(e,30,owner,"갓 핸드 크러셔")', 'damage(e,30,f,"갓 핸드 크러셔")', 'Obelisk crusher source')

# 모든 캐릭터의 노래 디버프 타이머를 갱신한다.
replace_once(
'''    function updateFighter(f, dt) {
      if (!f.alive) return;
      updateOshiAftershock(f, dt);''',
'''    function updateFighter(f, dt) {
      if (!f.alive) return;
      updateOshiSongDebuffs(f, dt);
      updateOshiAftershock(f, dt);''',
'updateFighter Oshi debuff tick'
)

# 실제 이동속도와 이동속도 판정 모두에 20% 슬로우를 반영한다.
replace_count(
'''      const irisGlassSlow = irisLitGlassSlowMultiplier(f);
      const boost = f.baseId === "wind_rio" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);''',
'''      const irisGlassSlow = irisLitGlassSlowMultiplier(f);
      const oshiSlow = oshiSongSlowMultiplier(f);
      const boost = f.baseId === "wind_rio" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);''',
2,
'Oshi slow declarations'
)
replace_once(
'      return Math.hypot(f.vx, f.vy) * slow * boost * gardenSlow * irisGlassSlow;',
'      return Math.hypot(f.vx, f.vy) * slow * boost * gardenSlow * irisGlassSlow * oshiSlow;',
'Oshi slow speed query'
)
replace_once(
'      f.x += f.vx * slow * boost * gardenSlow * irisGlassSlow * dt;\n      f.y += f.vy * slow * boost * gardenSlow * irisGlassSlow * dt;',
'      f.x += f.vx * slow * boost * gardenSlow * irisGlassSlow * oshiSlow * dt;\n      f.y += f.vy * slow * boost * gardenSlow * irisGlassSlow * oshiSlow * dt;',
'Oshi slow movement'
)

# 몸 접촉도 인지도 획득 조건으로 연결한다.
replace_once(
'''              recordJabamiContact(a, b);
              recordJabamiContact(b, a);
              passJabamiBomb(a, b);''',
'''              recordJabamiContact(a, b);
              recordJabamiContact(b, a);
              recordOshiContact(a, b);
              recordOshiContact(b, a);
              passJabamiBomb(a, b);''',
'Oshi contact fame hook'
)

# 상태창을 인지도/노래 단계/투어 진행으로 교체한다.
status_pattern = re.compile(r'''      if \(f\.oshi\) \{\n        const o = f\.oshi;\n        const counts = \{ candidate: 0, fan: 0, anti: 0 \};\n        o\.wallStates\.forEach\(state => \{ if \(counts\[state\] != null\) counts\[state\]\+\+; \}\);\n        return \{ ratio: clamp\(o\.tour / OSHI\.gaugeMax, 0, 1\), className: "skill-fill", text: .*?\n      \}''', re.S)
new_status = r'''      if (f.oshi) {
        const o = f.oshi;
        const songStage = Math.min(OSHI.songLevels.length, (o.songLevel || 0) + 1);
        const showTours = Math.min(3, o.toursCompleted || 0);
        const concertName = o.isDome ? (o.encore ? "도쿄돔 연장" : "도쿄돔 공연") : "투어 공연";
        return { ratio: clamp(o.fame / OSHI.gaugeMax, 0, 1), className: "skill-fill", text: o.concert > 0 ? `${concertName} · ${o.concert.toFixed(1)}초` : `인지도 ${Math.floor(o.fame)}/${OSHI.gaugeMax}`,
          extraTextHtml: `<div class="status-skill-label">노래 ${songStage}단계 · 투어 ${showTours}/3${o.domeDone ? " · 돔 공연 완료" : ""}${o.bleed > 0 ? ` · 출혈 ${o.bleed.toFixed(1)}초` : ""}${o.encore ? " · 공연 연장" : ""}</div>` };
      }'''
s, count = status_pattern.subn(new_status, s, count=1)
if count != 1:
    raise SystemExit(f'Oshi status block: expected 1 replacement, found {count}')

# 캐릭터 상세 수치 설명 갱신.
info_pattern = re.compile(r'''      if \(c\.id === "oshi"\) return \{ damage: .*? \};\n''')
new_info = '      if (c.id === "oshi") return { damage: "노래 1~4단계 피해 3/4/5/6 · 반경 90/110/130/150 / 투어 초당2 · 5초 연속 체류30 / 후유증: 체류 2초당 총3을 5초 DOT / 도쿄돔 칼35 + 출혈3×8 / 공연 연장 반경175·초당4·5초40", tick: "노래 2초 · 노래 적중 1명당 인지도+10 · 적 접촉 대상별 1초마다+4 · 인지도100에 투어", tip: "노래 적중자는 3초간 이동속도 20% 감소 및 최애에게 주는 모든 피해 20% 감소(감소 후 최소 피해 1). 최대 체력 비례 피해와 푸른 눈의 백룡 등 소환수 피해에도 적용된다. 투어 3회를 마친 뒤 다시 인지도100을 채우면 도쿄돔이 시작되며, 출혈 종료까지 생존하면 공연이 연장된다." };\n'
s, count = info_pattern.subn(new_info, s, count=1)
if count != 1:
    raise SystemExit(f'Oshi damage info: expected 1 replacement, found {count}')

# 패치노트 추가.
marker = '    const patchNotes = [\n'
if s.count(marker) != 1:
    raise SystemExit('patchNotes marker missing or duplicated')
v54_note = '      "v54: 최애 전면 리워크. 벽·팬·회복 시스템을 삭제하고 2초 주기의 성장형 원형 노래와 인지도 게이지를 도입했다. 노래 적중 1명당 인지도10, 적 접촉은 대상별 1초마다4를 얻고 100에서 투어가 열린다. 노래 적중자는 3초간 이속과 최애에게 주는 모든 피해가 20% 감소하며 피해는 정수·최소1로 처리된다. 투어 종료마다 다음 노래의 최소 단계가 상승하고, 3회 투어 후 다음 인지도100은 도쿄돔으로 전환된다. 돔은 칼 피해35와 8초 출혈 뒤 생존 시 공연이 연장되어 반경·피해가 강화된다.",\n'
s = s.replace(marker, marker + v54_note, 1)

checks = [
    '<title>볼배틀 리뉴얼 v54</title>',
    '<h1 id="mainTitle">볼배틀 리뉴얼 v54</h1>',
    'songPeriod: 2',
    'songFameGain: 10',
    'contactFameGain: 4',
    'damageMultiplier: 0.8',
    'slowMultiplier: 0.8',
    'function performOshiSong(f)',
    'function oshiReducedIncomingDamage(target, amount, source)',
    'amount = oshiReducedIncomingDamage(target, amount, source);',
    'recordOshiContact(a, b);',
    'damage(e,b.tickPower,dragon,"버스트 스트림 다단")',
    'bodyDirectDamage(e, e.maxHp * 0.5, f, "핑거플립", "#facc15")',
    'v54: 최애 전면 리워크.'
]
for item in checks:
    if item not in s:
        raise SystemExit(f'missing postcondition: {item}')

# 제거되어야 할 구형 벽/회복 필드가 최애 상태/UI에 남지 않았는지 확인한다.
for obsolete in ['wallStates: new Map()', 'wallHeal: 6', '관객후보 ${counts.candidate}']:
    if obsolete in s:
        raise SystemExit(f'obsolete Oshi wall token remains: {obsolete}')

path.write_text(s, encoding='utf-8')
