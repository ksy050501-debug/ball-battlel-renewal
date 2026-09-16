from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def rep(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s = s.replace(old, new, 1)


rep('<title>볼배틀 리뉴얼 v48</title>', '<title>볼배틀 리뉴얼 v49</title>', 'title')

old_buttons = '''      <div class="button-row" id="simBoostRow" style="width:min(700px,100%);">
        <button class="primary" id="quickSimAdaptiveBtn">빠른 전체 테스트</button>
        <button class="ghost" id="quickSimAll30Btn">선택 전체 30전</button>
        <button class="ghost" id="quickSim100Btn">1대1 100전</button>
        <button class="warn" id="fullMatrix30Btn">전체 상성표 30전</button>
        <button class="ghost" id="copyMatchupBtn">전적 복사</button>
        <button class="ghost" id="resetMatchupBtn">전적 초기화</button>
      </div>
      <p class="status" id="tipText">자동 테스트: 1명 선택은 전체 테스트, 2명 선택은 1대1 100전, 전체 상성표는 모든 조합을 한 번씩 30전으로 계산합니다.</p>'''
new_buttons = '''      <div class="button-row three" id="simBoostRow" style="width:min(700px,100%);">
        <button class="primary" id="quickSimAll30Btn">1인 전체 테스트</button>
        <button class="warn" id="fullMatrix30Btn">전체 테스트</button>
        <button class="ghost" id="quickSim100Btn">1대1 100전</button>
      </div>
      <div class="button-row" style="width:min(700px,100%);grid-template-columns:1fr;">
        <button class="ghost" id="copyMatchupBtn">전적 복사</button>
      </div>
      <p class="status" id="tipText">1인 전체 테스트는 선택한 1명을 나머지 전원과 각각 30전, 전체 테스트는 모든 조합을 각각 30전, 1대1 100전은 선택한 2명을 100전 시뮬레이션합니다.</p>'''
rep(old_buttons, new_buttons, 'simulation buttons')
rep('    $("quickSimAdaptiveBtn").addEventListener("click", runQuickSimAdaptive);\n', '', 'adaptive listener')
rep('    $("resetMatchupBtn").addEventListener("click", resetMatchupHistory);\n', '', 'reset listener')

oshi_character = '''      { id: "oshi", name: "최애", mark: "★", role: "애니", color: "#ec4899", hp: 170, attack: 0, speed: 2.7, range: 180,
        skillName: "분홍빛 투어 · 도쿄돔", condition: "벽 24구간 염색 · 분홍벽 접촉으로 서로 다른 두 게이지 축적", desc: "벽을 분홍색으로 물들인다. 분홍벽은 최애에게 회복과 투어를, 적에게 피해와 도쿄돔 게이지를 준다. 투어는 공연장 지속 피해, 도쿄돔은 최애 자신에게 큰 후유증을 남긴다." },
'''
rep('      { id: "iron_mask", name: "철가면"', oshi_character + '      { id: "iron_mask", name: "철가면"', 'oshi character')

rep('      if (c.id === "logo_doctor") initLogo(fighter);', '      if (c.id === "oshi") initOshi(fighter);\n      if (c.id === "logo_doctor") initLogo(fighter);', 'oshi init')
rep('      updateLisa(f, dt);\n      if (updatePowerPunch(f, dt)) return;', '      updateLisa(f, dt);\n      updateOshi(f, dt);\n      if (updatePowerPunch(f, dt)) return;', 'oshi update')

rep('      if (f.x - f.r < arena.x) {\n        f.x = arena.x + f.r;', '      if (f.x - f.r < arena.x) {\n        oshiWallCollision(f, "left", f.y);\n        f.x = arena.x + f.r;', 'left wall hook')
rep('      if (f.x + f.r > arena.x2) {\n        f.x = arena.x2 - f.r;', '      if (f.x + f.r > arena.x2) {\n        oshiWallCollision(f, "right", f.y);\n        f.x = arena.x2 - f.r;', 'right wall hook')
rep('      if (f.y - f.r < arena.y) {\n        f.y = arena.y + f.r;', '      if (f.y - f.r < arena.y) {\n        oshiWallCollision(f, "top", f.x);\n        f.y = arena.y + f.r;', 'top wall hook')
rep('      if (f.y + f.r > arena.y2) {\n        f.y = arena.y2 - f.r;', '      if (f.y + f.r > arena.y2) {\n        oshiWallCollision(f, "bottom", f.x);\n        f.y = arena.y2 - f.r;', 'bottom wall hook')

rep('      ctx.strokeRect(arena.x + 3, arena.y + 3, arena.size - 6, arena.size - 6);', '      ctx.strokeRect(arena.x + 3, arena.y + 3, arena.size - 6, arena.size - 6);\n      drawOshiArenaEffects();', 'draw arena effects')
rep('      drawDeathEffects();\n\n      if (!running && fighters.length === 0) {', '      drawDeathEffects();\n      drawOshiDomeOverlay();\n\n      if (!running && fighters.length === 0) {', 'draw dome overlay')
rep('      if (f.lisa) { drawLisaCharacter(f); return; }', '      if (f.lisa) { drawLisaCharacter(f); return; }\n      if (f.oshi) { drawOshiCharacter(f); return; }', 'draw oshi character')

oshi_info = '''      if (c.id === "oshi") return { damage: "분홍벽 적 접촉 5 / 투어 초당2 · 5초 연속 체류30 / 종료 후 누적 체류 1초당 1.5 / 도쿄돔 자해35 + 출혈3×8", tick: "벽 한 면 6구간 · 최애 분홍벽 접촉 HP+4·투어+8 / 적 접촉 도쿄돔+7", tip: "투어와 도쿄돔은 별도 게이지다. 하나가 발동하면 둘 다 0으로 초기화된다. 투어는 10초간 고정 공연장을 만들며, 도쿄돔은 0.75초 시간정지 연출 뒤 최애에게 자해와 출혈을 준다." };
'''
rep('      if (c.id === "justice_ally") return {', oshi_info + '      if (c.id === "justice_ally") return {', 'oshi damage info')

oshi_status = '''      if (f.oshi) {
        const o = f.oshi;
        return { ratio: clamp(o.tour / OSHI.gaugeMax, 0, 1), className: "skill-fill", text: o.concert > 0 ? `투어 공연 · ${o.concert.toFixed(1)}초` : `투어 ${Math.floor(o.tour)}/${OSHI.gaugeMax}`,
          extraBarsHtml: `<div class="bar" title="도쿄돔 게이지"><div class="bar-fill rage-fill" style="width:${clamp(o.dome / OSHI.gaugeMax, 0, 1) * 100}%"></div></div>`,
          extraTextHtml: `<div class="status-skill-label">도쿄돔 ${Math.floor(o.dome)}/${OSHI.gaugeMax}${o.bleed > 0 ? ` · 출혈 ${o.bleed.toFixed(1)}초` : ""} · 분홍벽 ${o.pinkWalls.size}/${OSHI.wallSegments * 4}</div>` };
      }
'''
rep('      if (f.tano) return {', oshi_status + '      if (f.tano) return {', 'oshi status')

oshi_code = r'''

    const OSHI = {
      wallSegments: 6, wallHeal: 4, tourGain: 8, wallDamage: 5, domeGain: 7, gaugeMax: 100,
      concertDuration: 10, concertRadius: 180, concertDps: 2, concertStayTime: 5, concertStayDamage: 30, aftershockPerSecond: 1.5,
      domeSelfDamage: 35, domeFreeze: 0.75, bleedDuration: 8, bleedDamage: 3
    };
    function initOshi(f) {
      f.oshi = { tour: 0, dome: 0, pinkWalls: new Set(), concert: 0, concertX: 0, concertY: 0, audience: new Map(), bleed: 0, bleedTick: 1, domeSceneUntil: 0 };
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
      spawnBlast(o.concertX, o.concertY, OSHI.concertRadius, "#f472b6");
      spawnParticles(o.concertX, o.concertY, "#f9a8d4", 30);
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
    function oshiWallCollision(f, wall, coordinate) {
      if (!f?.alive) return;
      const owners = fighters.filter(owner => owner.alive && owner.oshi);
      for (const owner of owners) {
        const o = owner.oshi;
        const key = oshiWallKey(wall, coordinate);
        if (owner === f) {
          if (!o.pinkWalls.has(key)) {
            o.pinkWalls.add(key);
            if (!fastSimMode) {
              spawnParticles(f.x, f.y, "#f472b6", 7);
              spawnFloatingText(f.x, f.y - f.r - 18, "분홍벽", "#f9a8d4");
            }
            continue;
          }
          const healed = Math.min(OSHI.wallHeal, Math.max(0, f.maxHp - f.hp));
          if (healed > 0) {
            f.hp += healed;
            f.healingDone = (f.healingDone || 0) + healed;
            spawnFloatingText(f.x, f.y - f.r - 20, "+" + healed, "#f9a8d4");
          }
          o.tour = Math.min(OSHI.gaugeMax, o.tour + OSHI.tourGain);
          spawnFloatingText(f.x, f.y - f.r - 36, `투어 +${OSHI.tourGain}`, "#f472b6");
          if (o.tour >= OSHI.gaugeMax && o.concert <= 0) startOshiTour(owner);
        } else if (!f.isSummon && areEnemies(owner, f) && o.pinkWalls.has(key)) {
          damage(f, OSHI.wallDamage, owner, "분홍벽");
          o.dome = Math.min(OSHI.gaugeMax, o.dome + OSHI.domeGain);
          spawnFloatingText(f.x, f.y - f.r - 34, `도쿄돔 +${OSHI.domeGain}`, "#fb7185");
          if (o.dome >= OSHI.gaugeMax) triggerOshiDome(owner);
        }
      }
    }
    function finishOshiTour(f) {
      const o = f.oshi;
      if (!o) return;
      for (const [id, entry] of o.audience) {
        const enemy = fighters.find(e => e.id === id && e.alive);
        if (!enemy || entry.total <= 0) continue;
        const after = Math.round(entry.total * OSHI.aftershockPerSecond * 10) / 10;
        if (after > 0) damage(enemy, after, f, "투어 후유증");
      }
      o.audience.clear();
      spawnFloatingText(o.concertX, o.concertY - 28, "투어 종료", "#fbcfe8");
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
      enemiesOf(f).forEach(enemy => {
        if (!enemy.alive) return;
        let entry = o.audience.get(enemy.id);
        if (!entry) { entry = { total: 0, streak: 0, tick: 0 }; o.audience.set(enemy.id, entry); }
        const inside = Math.hypot(enemy.x - o.concertX, enemy.y - o.concertY) <= OSHI.concertRadius + enemy.r;
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
        if (o.pinkWalls.size) {
          const seg = arena.size / OSHI.wallSegments;
          ctx.save();
          ctx.strokeStyle = "#f472b6"; ctx.shadowColor = "#ec4899"; ctx.shadowBlur = 14; ctx.lineWidth = 8; ctx.lineCap = "round";
          o.pinkWalls.forEach(key => {
            const [wall, raw] = key.split(":"); const i = Number(raw); const a = i * seg + 5, b = (i + 1) * seg - 5;
            ctx.beginPath();
            if (wall === "top") { ctx.moveTo(arena.x + a, arena.y + 4); ctx.lineTo(arena.x + b, arena.y + 4); }
            else if (wall === "bottom") { ctx.moveTo(arena.x + a, arena.y2 - 4); ctx.lineTo(arena.x + b, arena.y2 - 4); }
            else if (wall === "left") { ctx.moveTo(arena.x + 4, arena.y + a); ctx.lineTo(arena.x + 4, arena.y + b); }
            else { ctx.moveTo(arena.x2 - 4, arena.y + a); ctx.lineTo(arena.x2 - 4, arena.y + b); }
            ctx.stroke();
          });
          ctx.restore();
        }
        if (o.concert > 0) {
          const pulse = 0.5 + 0.5 * Math.sin(battleTime * 8);
          ctx.save();
          ctx.beginPath(); ctx.rect(arena.x, arena.y, arena.size, arena.size); ctx.clip();
          ctx.fillStyle = `rgba(244,114,182,${0.08 + pulse * 0.04})`; ctx.strokeStyle = `rgba(249,168,212,${0.62 + pulse * 0.28})`; ctx.lineWidth = 5;
          ctx.beginPath(); ctx.arc(o.concertX, o.concertY, OSHI.concertRadius, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
          ctx.restore();
        }
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
    function drawOshiCharacter(f) {
      ctx.save(); ctx.translate(f.x, f.y); ctx.scale(f.r / 20, f.r / 20);
      ctx.fillStyle = "#f5d0fe"; ctx.strokeStyle = "#ec4899"; ctx.lineWidth = 2.5;
      ctx.beginPath(); ctx.arc(0, 0, 18, 0, Math.PI * 2); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#7e22ce";
      ctx.beginPath(); ctx.arc(0, -5, 18, Math.PI, Math.PI * 2); ctx.fill();
      ctx.beginPath(); ctx.moveTo(-18, -4); ctx.quadraticCurveTo(-23, 10, -13, 17); ctx.lineTo(-8, 7); ctx.closePath(); ctx.fill();
      ctx.beginPath(); ctx.moveTo(18, -4); ctx.quadraticCurveTo(23, 10, 13, 17); ctx.lineTo(8, 7); ctx.closePath(); ctx.fill();
      ctx.fillStyle = "#fff";
      ctx.beginPath(); ctx.ellipse(-6, 1, 4, 5, 0, 0, Math.PI * 2); ctx.ellipse(6, 1, 4, 5, 0, 0, Math.PI * 2); ctx.fill();
      ctx.fillStyle = "#ec4899"; ctx.font = "900 8px system-ui"; ctx.textAlign = "center"; ctx.textBaseline = "middle"; ctx.fillText("★", -6, 1); ctx.fillText("★", 6, 1);
      ctx.strokeStyle = "#be185d"; ctx.lineWidth = 1.4; ctx.beginPath(); ctx.arc(0, 6, 5, 0.15 * Math.PI, 0.85 * Math.PI); ctx.stroke();
      ctx.restore();
      drawHealthBar(f); drawName(f);
    }
'''
rep('    const TANO = {', oshi_code + '\n\n    const TANO = {', 'oshi mechanics block')

rep('    const patchNotes = [\n', '    const patchNotes = [\n      "v49: 애니 캐릭터 최애 추가. 벽을 24구간으로 나눠 분홍색으로 염색하며, 분홍벽은 최애에게 회복·투어 게이지를, 적에게 피해·도쿄돔 게이지를 준다. 투어는 원형 공연장의 지속·체류·후유증 피해, 도쿄돔은 시간정지·암전 문구 뒤 자해와 출혈을 적용한다. 자동 테스트 UI는 1인 전체 테스트·전체 테스트·1대1 100전과 전적 복사만 남기도록 정리.",\n', 'patch note')

# Static postconditions
checks = [
    '<title>볼배틀 리뉴얼 v49</title>',
    'id="oshi"', 'ragePower: 9', 'hp: 160',
    'id="quickSimAll30Btn">1인 전체 테스트', 'id="fullMatrix30Btn">전체 테스트', 'id="quickSim100Btn">1대1 100전',
    'id="copyMatchupBtn">전적 복사',
    'function oshiWallCollision', 'function startOshiTour', 'function triggerOshiDome', 'drawOshiDomeOverlay();'
]
for needle in checks:
    if needle not in s:
        raise SystemExit(f'missing postcondition: {needle}')
for forbidden in ['id="quickSimAdaptiveBtn"', 'id="resetMatchupBtn"']:
    if forbidden in s:
        raise SystemExit(f'forbidden UI remains: {forbidden}')

p.write_text(s, encoding='utf-8')
print('v49 patch applied')
