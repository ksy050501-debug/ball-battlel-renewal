from pathlib import Path

path = Path('index.html')
text = path.read_text(encoding='utf-8')


def rep(old, new, expected=1):
    global text
    count = text.count(old)
    if count != expected:
        raise SystemExit(f'anchor mismatch: expected {expected}, got {count}: {old[:100]!r}')
    text = text.replace(old, new)


rep('<title>볼배틀 리뉴얼 v65</title>', '<title>볼배틀 리뉴얼 v66</title>')

rep(
'''    const characters = [\n      { id: "hinta",''',
'''    const characters = [\n      { id: "riddle_lord", name: "리들 경", mark: "蛇", role: "영화", color: "#64748b", hp: 180, attack: 0, speed: 2.8, range: 260,\n        skillName: "피엔드피레 · 아바다 케다브라 · 호크룩스", condition: "피엔드피레13초 · 아바다8초 · 딱총나무 지팡이16초 · 사망 시 호크룩스 1회", desc: "뱀 형태의 불꽃을 두르고 초록색 다단 광선을 발사한다. 딱총나무 지팡이를 획득하면 불꽃 범위와 화상이 강화되고 아바다 케다브라가 거리 무관 확정타가 된다. 첫 사망 시 7칸 호크룩스로 7초를 버티면 약화 상태로 부활한다." },\n      { id: "hinta",'''
)

RIDDLE_CODE = r'''
    const RIDDLE = {
      fiendCooldown: 13, fiendDuration: 4, fiendRadius: 95, fiendDamage: 4, fiendTick: .4,
      fiendBurn: 2, fiendBurnDuration: 3, elderFiendRadius: 130, elderFiendDamage: 5, elderFiendBurn: 3,
      avadaCooldown: 8, avadaCast: .35, avadaDuration: .9, avadaRange: 260, avadaWidth: 18,
      avadaHits: 5, avadaDamage: 5, elderAvadaDamage: 6,
      wandSpawn: 16, wandLife: 8, elderDuration: 12,
      horcruxSegments: 7, horcruxDuration: 7, horcruxContactCooldown: .75,
      weakHp: 90, weakSpeed: 2.5, weakFiendRadiusPenalty: 15, weakDamageMultiplier: .8
    };

    function initRiddle(f) {
      f.riddle = {
        fiendCd: 6.5, fiendActive: 0, fiendTick: 0,
        avadaCd: 4, avadaCast: 0, avadaLife: 0, avadaTick: 0, avadaAngle: 0, avadaTargetId: null, avadaElder: false,
        wandTimer: RIDDLE.wandSpawn, wand: null, elderBuff: 0,
        horcruxUsed: false, horcruxActive: false, horcruxSegments: 0, horcruxTimer: 0, horcruxX: 0, horcruxY: 0,
        horcruxContacts: new Map(), weakened: false
      };
    }

    function riddleIsEnemy(target, source) {
      return !!(target && source && target !== source && source.alive && areEnemies(target, source));
    }

    function finalizeRiddleDeath(target, source, reason = "호크룩스 파괴") {
      if (!target?.alive) return;
      target.hp = 0;
      target.alive = false;
      if (target.riddle) {
        target.riddle.horcruxActive = false;
        target.riddle.fiendActive = 0;
        target.riddle.avadaCast = 0;
        target.riddle.avadaLife = 0;
        target.riddle.wand = null;
      }
      triggerDeathEffect(target);
      if (source && source.alive && !target.isSummon) {
        source.kills = (source.kills || 0) + 1;
        log(`<strong>${escapeHtml(source.name)}</strong>의 ${reason}! <strong>${escapeHtml(target.name)}</strong> 탈락`);
      } else {
        log(`<strong>${escapeHtml(target.name)}</strong> 호크룩스 소멸`, "탈락");
      }
    }

    function tryActivateRiddleHorcrux(target) {
      const r = target?.riddle;
      if (!r || r.horcruxUsed || r.horcruxActive) return false;
      r.horcruxUsed = true;
      r.horcruxActive = true;
      r.horcruxSegments = RIDDLE.horcruxSegments;
      r.horcruxTimer = RIDDLE.horcruxDuration;
      r.horcruxX = target.x;
      r.horcruxY = target.y;
      r.horcruxContacts = new Map();
      r.fiendActive = 0;
      r.avadaCast = 0;
      r.avadaLife = 0;
      r.wand = null;
      r.elderBuff = 0;
      target.hp = 1;
      target.vx = 0;
      target.vy = 0;
      target.freeze = 0;
      target.jolt = 0;
      target.joltStop = 0;
      fighters.forEach(e => {
        if (e.burningTicks?.length) e.burningTicks = e.burningTicks.filter(b => b.source !== target);
      });
      spawnBlast(target.x, target.y, 72, "#9ca3af");
      spawnParticles(target.x, target.y, "#d1d5db", 26);
      spawnFloatingText(target.x, target.y - target.r - 42, "호크룩스 · 7칸", "#d1d5db");
      playSound("rift", .8);
      log(`<strong>${escapeHtml(target.name)}</strong> 사망 회피 · 호크룩스 7칸 / ${RIDDLE.horcruxDuration}초`, "부활");
      return true;
    }

    function damageRiddleHorcrux(target, amount, source, reason = "공격") {
      const r = target?.riddle;
      if (!r?.horcruxActive || !riddleIsEnemy(target, source)) return 0;
      const raw = Math.max(0, Math.round(amount || 0));
      const loss = 1 + Math.floor(raw / 10);
      r.horcruxSegments = Math.max(0, r.horcruxSegments - loss);
      spawnFloatingText(target.x, target.y - target.r - 30, `호크룩스 -${loss}`, "#cbd5e1");
      spawnHitFlash(target.x, target.y, "#9ca3af", 30);
      if (r.horcruxSegments <= 0) finalizeRiddleDeath(target, source, reason || "호크룩스 파괴");
      return raw;
    }

    function riddleHorcruxContact(target, source) {
      const r = target?.riddle;
      if (!r?.horcruxActive || !riddleIsEnemy(target, source)) return;
      const last = r.horcruxContacts.get(source.id);
      if (last != null && battleTime - last < RIDDLE.horcruxContactCooldown) return;
      r.horcruxContacts.set(source.id, battleTime);
      r.horcruxSegments = Math.max(0, r.horcruxSegments - 1);
      spawnFloatingText(target.x, target.y - target.r - 30, "접촉 · 호크룩스 -1", "#cbd5e1");
      if (r.horcruxSegments <= 0) finalizeRiddleDeath(target, source, "호크룩스 접촉 파괴");
    }

    function reviveRiddleWeakened(f) {
      const r = f?.riddle;
      if (!r || !r.horcruxActive || !f.alive) return;
      r.horcruxActive = false;
      r.weakened = true;
      r.horcruxSegments = 0;
      r.horcruxTimer = 0;
      f.maxHp = RIDDLE.weakHp;
      f.hp = RIDDLE.weakHp;
      f.baseSpeed = RIDDLE.weakSpeed;
      f.speed = RIDDLE.weakSpeed;
      const v = randomVelocity(f.baseSpeed);
      f.vx = v.vx;
      f.vy = v.vy;
      r.fiendCd = 4;
      r.avadaCd = 2.5;
      spawnBlast(f.x, f.y, 86, "#6b7280");
      spawnParticles(f.x, f.y, "#d1d5db", 30);
      spawnFloatingText(f.x, f.y - f.r - 46, "약화된 리들 경 부활", "#e5e7eb");
      playSound("magic", 1.1);
      log(`<strong>${escapeHtml(f.name)}</strong> 호크룩스 생존 · 체력 ${RIDDLE.weakHp}의 약화 상태로 부활`, "부활");
    }

    function riddleFiendRadius(f) {
      const r = f.riddle;
      let radius = r.elderBuff > 0 ? RIDDLE.elderFiendRadius : RIDDLE.fiendRadius;
      if (r.weakened) radius -= RIDDLE.weakFiendRadiusPenalty;
      return radius;
    }

    function startRiddleFiendfyre(f) {
      const r = f.riddle;
      r.fiendActive = RIDDLE.fiendDuration;
      r.fiendTick = 0;
      r.fiendCd = RIDDLE.fiendCooldown;
      spawnBlast(f.x, f.y, riddleFiendRadius(f), r.elderBuff > 0 ? "#fb923c" : "#ef4444");
      spawnFloatingText(f.x, f.y - f.r - 38, "피엔드피레!", "#fb923c");
      playSound("fire", 1.05);
      log(`<strong>${escapeHtml(f.name)}</strong> 피엔드피레`, "스킬");
    }

    function tickRiddleFiendfyre(f, dt) {
      const r = f.riddle;
      if (r.fiendActive <= 0) return;
      r.fiendActive = Math.max(0, r.fiendActive - dt);
      r.fiendTick -= dt;
      const elder = r.elderBuff > 0;
      const radius = riddleFiendRadius(f);
      while (r.fiendTick <= 0 && r.fiendActive > 0 && f.alive) {
        r.fiendTick += RIDDLE.fiendTick;
        enemiesOf(f).forEach(e => {
          if (!e.alive || Math.hypot(e.x - f.x, e.y - f.y) > radius + e.r) return;
          const dealt = damage(e, elder ? RIDDLE.elderFiendDamage : RIDDLE.fiendDamage, f, "피엔드피레");
          if (dealt > 0) {
            applyBurn(e, f, elder ? RIDDLE.elderFiendBurn : RIDDLE.fiendBurn, RIDDLE.fiendBurnDuration, 1, 3, "riddle_fiendfyre");
            if (!fastSimMode) spawnHitFlash(e.x, e.y, elder ? "#f97316" : "#ef4444", 25);
          }
        });
      }
    }

    function startRiddleAvada(f) {
      const r = f.riddle;
      const target = nearestEnemy(f).enemy;
      if (!target) return;
      r.avadaCd = RIDDLE.avadaCooldown;
      r.avadaCast = RIDDLE.avadaCast;
      r.avadaLife = 0;
      r.avadaTick = 0;
      r.avadaTargetId = target.id;
      r.avadaElder = r.elderBuff > 0;
      r.avadaAngle = Math.atan2(target.y - f.y, target.x - f.x);
      f.vx = 0;
      f.vy = 0;
      spawnFloatingText(f.x, f.y - f.r - 42, "아바다 케다브라!", "#4ade80");
      playSound("charge", 1.05);
    }

    function beginRiddleAvadaBeam(f) {
      const r = f.riddle;
      r.avadaLife = RIDDLE.avadaDuration;
      r.avadaTick = 0;
      spawnBlast(f.x, f.y, 54, "#22c55e");
      playSound("beam", 1.15);
      log(`<strong>${escapeHtml(f.name)}</strong> 아바다 케다브라${r.avadaElder ? " · 딱총나무 확정타" : ""}`, "스킬");
    }

    function riddleAvadaDamage(f) {
      const r = f.riddle;
      const base = r.avadaElder ? RIDDLE.elderAvadaDamage : RIDDLE.avadaDamage;
      return r.weakened ? Math.max(1, Math.round(base * RIDDLE.weakDamageMultiplier)) : base;
    }

    function tickRiddleAvadaBeam(f, dt) {
      const r = f.riddle;
      if (r.avadaLife <= 0) return;
      r.avadaLife = Math.max(0, r.avadaLife - dt);
      r.avadaTick -= dt;
      const interval = RIDDLE.avadaDuration / RIDDLE.avadaHits;
      while (r.avadaTick <= 0 && r.avadaLife > 0 && f.alive) {
        r.avadaTick += interval;
        const power = riddleAvadaDamage(f);
        if (r.avadaElder) {
          const target = fighterById(r.avadaTargetId);
          if (target?.alive && areEnemies(f, target)) {
            damage(target, power, f, "딱총나무 아바다 케다브라");
            if (!fastSimMode) spawnHitFlash(target.x, target.y, "#4ade80", 30);
          }
        } else {
          const x2 = f.x + Math.cos(r.avadaAngle) * RIDDLE.avadaRange;
          const y2 = f.y + Math.sin(r.avadaAngle) * RIDDLE.avadaRange;
          enemiesOf(f).forEach(e => {
            if (!e.alive) return;
            const d = distancePointToSegment(e.x, e.y, f.x, f.y, x2, y2);
            if (d <= e.r + RIDDLE.avadaWidth / 2) {
              damage(e, power, f, "아바다 케다브라");
              if (!fastSimMode) spawnHitFlash(e.x, e.y, "#4ade80", 30);
            }
          });
        }
      }
    }

    function spawnRiddleWand(f) {
      const r = f.riddle;
      const pad = 24;
      r.wand = {
        x: rand(arena.x + pad, arena.x2 - pad),
        y: rand(arena.y + pad, arena.y2 - pad),
        life: RIDDLE.wandLife,
        angle: rand(-Math.PI, Math.PI)
      };
      r.wandTimer = RIDDLE.wandSpawn;
      spawnBlast(r.wand.x, r.wand.y, 44, "#a3a3a3");
      spawnFloatingText(r.wand.x, r.wand.y - 24, "딱총나무 지팡이", "#d6d3d1");
    }

    function collectRiddleWand(f) {
      const r = f.riddle;
      if (!r.wand) return;
      r.wand = null;
      r.wandTimer = RIDDLE.wandSpawn;
      r.elderBuff = RIDDLE.elderDuration;
      spawnBlast(f.x, f.y, 76, "#86efac");
      spawnParticles(f.x, f.y, "#bbf7d0", 24);
      spawnFloatingText(f.x, f.y - f.r - 48, "딱총나무 지팡이 획득!", "#bbf7d0");
      playSound("magic", 1.25);
      log(`<strong>${escapeHtml(f.name)}</strong> 딱총나무 지팡이 · ${RIDDLE.elderDuration}초 강화`, "강화");
    }

    function updateRiddle(f, dt) {
      const r = f?.riddle;
      if (!r) return false;
      if (r.horcruxActive) {
        f.x = r.horcruxX;
        f.y = r.horcruxY;
        f.vx = 0;
        f.vy = 0;
        r.horcruxTimer = Math.max(0, r.horcruxTimer - dt);
        if (r.horcruxTimer <= 0 && f.alive) reviveRiddleWeakened(f);
        return r.horcruxActive;
      }

      r.elderBuff = Math.max(0, r.elderBuff - dt);
      r.fiendCd = Math.max(0, r.fiendCd - dt);
      r.avadaCd = Math.max(0, r.avadaCd - dt);

      if (r.wand) {
        r.wand.life = Math.max(0, r.wand.life - dt);
        if (r.wand.life <= 0) { r.wand = null; r.wandTimer = RIDDLE.wandSpawn; }
        else if (Math.hypot(f.x - r.wand.x, f.y - r.wand.y) <= f.r + 14) collectRiddleWand(f);
      } else {
        r.wandTimer = Math.max(0, r.wandTimer - dt);
        if (r.wandTimer <= 0) spawnRiddleWand(f);
      }

      tickRiddleFiendfyre(f, dt);

      if (r.avadaCast > 0) {
        r.avadaCast = Math.max(0, r.avadaCast - dt);
        f.vx = 0;
        f.vy = 0;
        if (r.avadaCast <= 0) beginRiddleAvadaBeam(f);
      } else {
        tickRiddleAvadaBeam(f, dt);
      }

      if (r.fiendCd <= 0) startRiddleFiendfyre(f);
      if (r.avadaCd <= 0 && r.avadaCast <= 0 && r.avadaLife <= 0) startRiddleAvada(f);

      return r.avadaCast > 0 || r.avadaLife > 0;
    }

    function drawElderWand(x, y, scale = 1, angle = -.65) {
      ctx.save();
      ctx.translate(x, y);
      ctx.rotate(angle);
      ctx.scale(scale, scale);
      ctx.lineCap = "round";
      ctx.strokeStyle = "#29221e";
      ctx.lineWidth = 3.2;
      ctx.beginPath();
      ctx.moveTo(-24, 0);
      ctx.lineTo(25, 0);
      ctx.stroke();
      ctx.fillStyle = "#3f332c";
      [-17, -6, 7, 18].forEach((px, i) => {
        ctx.beginPath();
        ctx.ellipse(px, 0, i === 0 ? 5 : 4, i === 0 ? 5.5 : 4.5, 0, 0, Math.PI * 2);
        ctx.fill();
        ctx.fillStyle = "#211a17";
        for (let n = 0; n < 4; n++) {
          const a = n * Math.PI / 2 + i * .4;
          ctx.beginPath();
          ctx.arc(px + Math.cos(a) * 2.2, Math.sin(a) * 2.2, .75, 0, Math.PI * 2);
          ctx.fill();
        }
        ctx.fillStyle = "#3f332c";
      });
      ctx.fillStyle = "#211a17";
      ctx.beginPath();
      ctx.moveTo(-29, -4); ctx.lineTo(-23, 0); ctx.lineTo(-29, 4); ctx.closePath(); ctx.fill();
      ctx.restore();
    }

    function drawRiddleFiendfyre(f) {
      const r = f.riddle;
      if (!f.alive || r.horcruxActive || r.fiendActive <= 0) return;
      const radius = riddleFiendRadius(f);
      const elder = r.elderBuff > 0;
      const pulse = .5 + .5 * Math.sin(battleTime * 9);
      ctx.save();
      ctx.beginPath(); ctx.rect(arena.x, arena.y, arena.size, arena.size); ctx.clip();
      ctx.strokeStyle = elder ? `rgba(251,146,60,${.65 + pulse*.25})` : `rgba(239,68,68,${.60 + pulse*.25})`;
      ctx.lineWidth = 4;
      ctx.shadowColor = elder ? "#fb923c" : "#ef4444";
      ctx.shadowBlur = 18;
      ctx.beginPath(); ctx.arc(f.x, f.y, radius, 0, Math.PI * 2); ctx.stroke();
      for (let i = 0; i < 6; i++) {
        const a = battleTime * 1.9 + i * Math.PI * 2 / 6;
        const hx = f.x + Math.cos(a) * radius;
        const hy = f.y + Math.sin(a) * radius;
        const tx = f.x + Math.cos(a - .28) * (radius - 22);
        const ty = f.y + Math.sin(a - .28) * (radius - 22);
        ctx.strokeStyle = i % 2 ? "#fb923c" : "#ef4444";
        ctx.lineWidth = 7;
        ctx.beginPath(); ctx.moveTo(tx, ty); ctx.quadraticCurveTo(f.x + Math.cos(a-.15)*(radius+10), f.y + Math.sin(a-.15)*(radius+10), hx, hy); ctx.stroke();
        ctx.fillStyle = elder ? "#fdba74" : "#f87171";
        ctx.save(); ctx.translate(hx, hy); ctx.rotate(a + Math.PI/2);
        ctx.beginPath(); ctx.moveTo(0, -9); ctx.lineTo(-6, 5); ctx.lineTo(0, 2); ctx.lineTo(6, 5); ctx.closePath(); ctx.fill();
        ctx.fillStyle = "#fef3c7";
        ctx.beginPath(); ctx.arc(-2.4, -2, 1.2, 0, Math.PI*2); ctx.arc(2.4, -2, 1.2, 0, Math.PI*2); ctx.fill();
        ctx.restore();
      }
      ctx.restore();
    }

    function drawRiddleAvada(f) {
      const r = f.riddle;
      if (!f.alive || r.horcruxActive || r.avadaLife <= 0) return;
      let x2, y2;
      if (r.avadaElder) {
        const target = fighterById(r.avadaTargetId);
        if (target?.alive) { x2 = target.x; y2 = target.y; }
      }
      if (x2 == null) {
        x2 = f.x + Math.cos(r.avadaAngle) * RIDDLE.avadaRange;
        y2 = f.y + Math.sin(r.avadaAngle) * RIDDLE.avadaRange;
      }
      const flicker = .65 + .35 * Math.sin(battleTime * 45);
      ctx.save();
      ctx.strokeStyle = `rgba(34,197,94,${.5 + .35*flicker})`;
      ctx.shadowColor = "#22c55e";
      ctx.shadowBlur = 26;
      ctx.lineWidth = r.avadaElder ? 14 : 10;
      ctx.beginPath(); ctx.moveTo(f.x, f.y); ctx.lineTo(x2, y2); ctx.stroke();
      ctx.strokeStyle = "#bbf7d0";
      ctx.lineWidth = 3;
      ctx.beginPath(); ctx.moveTo(f.x, f.y); ctx.lineTo(x2, y2); ctx.stroke();
      ctx.restore();
    }

    function drawRiddleEffects() {
      fighters.filter(f => f.riddle).forEach(f => {
        const r = f.riddle;
        if (f.alive && !r.horcruxActive && r.wand) {
          const bob = Math.sin(battleTime * 3 + f.id) * 3;
          ctx.save();
          ctx.shadowColor = "#a7f3d0";
          ctx.shadowBlur = 14;
          drawElderWand(r.wand.x, r.wand.y + bob, .85, r.wand.angle);
          ctx.restore();
          drawRing(r.wand.x, r.wand.y + bob, 18, "rgba(167,243,208,.55)", 1.5);
        }
        drawRiddleFiendfyre(f);
        drawRiddleAvada(f);
      });
    }

    function drawRiddleCharacter(f) {
      const r = f.riddle;
      if (r?.horcruxActive) {
        ctx.save();
        ctx.translate(f.x, f.y);
        ctx.globalAlpha = .82;
        ctx.fillStyle = "#4b5563";
        ctx.beginPath(); ctx.moveTo(-15, 20); ctx.lineTo(-20, -2); ctx.quadraticCurveTo(0, -18, 20, -2); ctx.lineTo(15, 20); ctx.closePath(); ctx.fill();
        ctx.fillStyle = "#9ca3af";
        ctx.beginPath(); ctx.ellipse(0, -9, 13, 16, 0, 0, Math.PI*2); ctx.fill();
        ctx.strokeStyle = "#6b7280"; ctx.lineWidth = 1.5;
        ctx.beginPath(); ctx.moveTo(-8,-15); ctx.lineTo(-2,-8); ctx.lineTo(-7,0); ctx.moveTo(7,-16); ctx.lineTo(3,-7); ctx.lineTo(8,-1); ctx.stroke();
        ctx.fillStyle = "#374151";
        ctx.beginPath(); ctx.ellipse(-5,-10,2.4,1.4,0,0,Math.PI*2); ctx.ellipse(5,-10,2.4,1.4,0,0,Math.PI*2); ctx.fill();
        ctx.restore();
        const seg = Math.max(0, r.horcruxSegments);
        const w = 6, gap = 2, total = RIDDLE.horcruxSegments * w + (RIDDLE.horcruxSegments - 1) * gap;
        ctx.save();
        for (let i=0;i<RIDDLE.horcruxSegments;i++) {
          ctx.fillStyle = i < seg ? "#d1d5db" : "#374151";
          ctx.fillRect(f.x-total/2+i*(w+gap), f.y-f.r-30, w, 5);
        }
        ctx.fillStyle="#e5e7eb";ctx.font="800 9px system-ui";ctx.textAlign="center";
        ctx.fillText(`${r.horcruxTimer.toFixed(1)}초`,f.x,f.y-f.r-34);
        ctx.restore();
        drawHealthBar(f); drawName(f); return;
      }

      ctx.save();
      ctx.translate(f.x, f.y);
      const s = f.r / 20;
      ctx.scale(s, s);
      if (r?.weakened) ctx.globalAlpha = .9;
      ctx.fillStyle = r?.weakened ? "#111827" : "#05070a";
      ctx.beginPath(); ctx.moveTo(-18, 20); ctx.lineTo(-15, 1); ctx.quadraticCurveTo(-11,-5,0,-4); ctx.quadraticCurveTo(11,-5,15,1); ctx.lineTo(18,20); ctx.closePath(); ctx.fill();
      ctx.fillStyle = r?.weakened ? "#b7bcc3" : "#d4d8dc";
      ctx.strokeStyle = "#7b8188"; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.ellipse(0, -7, 13.5, 16.5, 0, 0, Math.PI*2); ctx.fill(); ctx.stroke();
      ctx.fillStyle = "#6b7280";
      ctx.beginPath(); ctx.moveTo(-11,-17); ctx.quadraticCurveTo(0,-24,11,-17); ctx.quadraticCurveTo(4,-21,-4,-20); ctx.closePath(); ctx.fill();
      ctx.fillStyle = "#fee2e2";
      ctx.beginPath(); ctx.ellipse(-5.2,-9,3.2,1.9,-.08,0,Math.PI*2); ctx.ellipse(5.2,-9,3.2,1.9,.08,0,Math.PI*2); ctx.fill();
      ctx.fillStyle = "#7f1d1d";
      ctx.beginPath(); ctx.ellipse(-5.1,-9,1.25,1.45,0,0,Math.PI*2); ctx.ellipse(5.1,-9,1.25,1.45,0,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle = "#737982"; ctx.lineWidth = 1.2;
      ctx.beginPath(); ctx.moveTo(-2.1,-4); ctx.quadraticCurveTo(-3,-1,-3.3,1); ctx.moveTo(2.1,-4); ctx.quadraticCurveTo(3,-1,3.3,1); ctx.stroke();
      ctx.fillStyle = "#5b6168";
      ctx.beginPath(); ctx.ellipse(-2.5,0,1.2,1.8,-.18,0,Math.PI*2); ctx.ellipse(2.5,0,1.2,1.8,.18,0,Math.PI*2); ctx.fill();
      ctx.strokeStyle = "#7f7474"; ctx.lineWidth = 1.1;
      ctx.beginPath(); ctx.moveTo(-5.5,6); ctx.quadraticCurveTo(0,7,5.5,6); ctx.stroke();
      ctx.save(); ctx.translate(11,7); ctx.rotate(-.8); drawElderWand(0,0,.55,0); ctx.restore();
      if (r?.elderBuff > 0) {
        ctx.strokeStyle="#86efac";ctx.lineWidth=1.8;ctx.globalAlpha=.8;
        ctx.beginPath();ctx.arc(0,0,23+Math.sin(battleTime*7)*2,0,Math.PI*2);ctx.stroke();
      }
      ctx.restore();
      drawHealthBar(f); drawName(f);
    }
'''

rep('    const HINTA = {', RIDDLE_CODE + '\n    const HINTA = {')

rep(
'''      if (c.id === "oshi") initOshi(fighter);\n      if (c.id === "hinta") initHinta(fighter);''',
'''      if (c.id === "oshi") initOshi(fighter);\n      if (c.id === "riddle_lord") initRiddle(fighter);\n      if (c.id === "hinta") initHinta(fighter);'''
)

rep(
'''    function isCasting(f) {\n      return !!(f && f.castPause && f.castPause > 0);\n    }''',
'''    function isCasting(f) {\n      return !!(f && ((f.castPause && f.castPause > 0) || f.riddle?.horcruxActive || (f.riddle?.avadaCast || 0) > 0 || (f.riddle?.avadaLife || 0) > 0));\n    }'''
)

rep(
'''      updateOshiAftershock(f, dt);\n      if (!f.alive) return;''',
'''      updateOshiAftershock(f, dt);\n      if (!f.alive) return;\n      if (f.riddle && updateRiddle(f, dt)) return;'''
)

rep(
'''      if (f.oshi) { drawOshiCharacter(f); return; }\n      if (f.hinta) { drawHintaCharacter(f); return; }''',
'''      if (f.oshi) { drawOshiCharacter(f); return; }\n      if (f.riddle) { drawRiddleCharacter(f); return; }\n      if (f.hinta) { drawHintaCharacter(f); return; }'''
)

rep('      drawHintaBalls();\n      drawLisaWaves();', '      drawHintaBalls();\n      drawRiddleEffects();\n      drawLisaWaves();')

rep(
'''              recordOshiContact(a, b);\n              recordOshiContact(b, a);\n              passJabamiBomb(a, b);''',
'''              recordOshiContact(a, b);\n              recordOshiContact(b, a);\n              riddleHorcruxContact(a, b);\n              riddleHorcruxContact(b, a);\n              passJabamiBomb(a, b);'''
)

rep(
'''      if (!target || !target.alive || (target.dodoVoid || 0) > 0 || target.tano?.hidden > 0) return 0;\n      if ((target.duelMonster?.invuln || 0) > 0 || target.duelMonster?.fusing)''',
'''      if (!target || !target.alive || (target.dodoVoid || 0) > 0 || target.tano?.hidden > 0) return 0;\n      if (target.riddle?.horcruxActive) return damageRiddleHorcrux(target, amount, source, reason);\n      if ((target.duelMonster?.invuln || 0) > 0 || target.duelMonster?.fusing)'''
)

rep(
'''      if (!target || !target.alive || (target.tano?.hidden > 0 && reason !== "스톤 소실")) return 0;\n      if (tryHeroLeonGuardBlock(target, reason)) return 0;''',
'''      if (!target || !target.alive || (target.tano?.hidden > 0 && reason !== "스톤 소실")) return 0;\n      if (target.riddle?.horcruxActive) return damageRiddleHorcrux(target, amount, source, reason);\n      if (tryHeroLeonGuardBlock(target, reason)) return 0;'''
)

old_death = '''        target.hp = 0;\n        target.alive = false;'''
if text.count(old_death) != 2:
    raise SystemExit(f'death anchor mismatch: {text.count(old_death)}')
text = text.replace(old_death, '''        if (tryActivateRiddleHorcrux(target)) return final;\n        target.hp = 0;\n        target.alive = false;''')

rep(
'''    function characterDamageInfo(c) {\n      if (c.id === "hinta")''',
'''    function characterDamageInfo(c) {\n      if (c.id === "riddle_lord") return {damage:"피엔드피레 0.4초마다4 + 화상2×3초 / 딱총나무 강화 0.4초마다5 + 화상3×3초 · 아바다 케다브라 5×5 / 강화 6×5",tick:"피엔드피레13초·4초 지속 · 아바다8초·0.9초 다단 · 딱총나무16초마다 등장·8초 유지·획득 시12초 강화",tip:"딱총나무 강화 중 피엔드피레 반경95→130, 아바다 케다브라는 거리와 조준을 무시하고 지정 대상에게 확정 적중한다. 첫 사망 때 호크룩스 7칸/7초 상태가 되며 이동·공격 불가. 적 접촉마다 1칸, 공격 피격마다 기본1칸＋피해10당 1칸 추가 감소. 생존하면 HP90·이속2.5로 부활하며 피엔드피레 반경-15, 아바다 피해20% 감소. 두 번째 부활은 없다."};\n      if (c.id === "hinta")'''
)

rep(
'''    function skillProgressInfo(f) {\n      if(f.hinta){''',
'''    function skillProgressInfo(f) {\n      if(f.riddle){const r=f.riddle;if(r.horcruxActive)return {ratio:clamp(r.horcruxSegments/RIDDLE.horcruxSegments,0,1),className:"rage-fill",text:`호크룩스 ${r.horcruxSegments}/${RIDDLE.horcruxSegments} · 부활 ${r.horcruxTimer.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">접촉 -1 · 공격 피격 -1＋피해10당 추가 -1</div>'};return {ratio:r.elderBuff>0?clamp(r.elderBuff/RIDDLE.elderDuration,0,1):clamp(1-r.wandTimer/RIDDLE.wandSpawn,0,1),className:"skill-fill",text:r.elderBuff>0?`딱총나무 강화 ${r.elderBuff.toFixed(1)}초`:r.wand?`딱총나무 지팡이 · 남은 ${r.wand.life.toFixed(1)}초`:`딱총나무 등장 ${r.wandTimer.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">${r.weakened?"약화 부활 · ":""}피엔드피레 ${r.fiendCd.toFixed(1)}초 · 아바다 ${r.avadaCd.toFixed(1)}초</div>`};}\n      if(f.hinta){'''
)

rep(
'''    const patchNotes = [\n      "v65:''',
'''    const patchNotes = [\n      "v66: 신규 캐릭터 리들 경 추가. 피엔드피레 원형 뱀 불꽃·화상, 아바다 케다브라 초록 다단 광선, 16초 주기 딱총나무 지팡이 강화와 거리 무관 확정타를 구현. 첫 사망은 7칸 호크룩스 상태로 전환되어 접촉/피격/피해량에 따라 칸이 감소하고 7초 생존 시 HP90 약화형으로 1회 부활. 참고 이미지 기반 창백한 민머리·뱀 코·검은 로브와 딱총나무 지팡이를 캔버스 드로잉으로 추가.",\n      "v65:'''
)

path.write_text(text, encoding='utf-8')
print('v66 Riddle Lord patch applied')
