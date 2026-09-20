from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:180]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v85</title>','<title>볼배틀 리뉴얼 v86</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v85</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v86</h1>')

rep(
'''      { id: "riddle_lord", name: "리들 경", mark: "蛇", role: "영화", color: "#64748b", hp: 180, attack: 0, speed: 2.8, range: 260,
        skillName: "피엔드피레 · 아바다 케다브라 · 호크룩스", condition: "공유 쿨9초 · 피엔드피레↔아바다 번갈아 시전 · 딱총나무 지팡이16초 · 사망 시 호크룩스 1회", desc: "피엔드피레와 아바다 케다브라를 하나의 쿨타임으로 번갈아 사용한다. 딱총나무 지팡이를 획득하면 불꽃 범위와 화상이 강화되고 아바다 케다브라가 거리 무관 확정타가 된다. 첫 사망 시 7칸 호크룩스로 7초를 버티면 본래 능력으로 부활하며, 대기 중 피격·충돌마다 부활 HP가 10씩 감소한다. 부활 최대 체력은 70이며 지팡이도 계속 획득할 수 있다. 지팡이는 사라지지 않고 등장 25초 뒤 자동 습득한다." },''',
'''      { id: "riddle_lord", name: "리들 경", mark: "蛇", role: "영화", color: "#64748b", hp: 180, attack: 0, speed: 2.8, range: 260,
        skillName: "피엔드피레 · 아바다 케다브라 · 호크룩스", condition: "공유 쿨9초 · 피엔드피레↔아바다 번갈아 시전 · 딱총나무 지팡이16초 · 사망 시 호크룩스 1회", desc: "피엔드피레와 아바다 케다브라를 하나의 쿨타임으로 번갈아 사용한다. 딱총나무 지팡이를 획득하면 불꽃 범위와 화상이 강화되고 아바다 케다브라가 거리 무관 확정타가 된다. 첫 사망 시 7칸 호크룩스로 7초를 버티면 본래 능력으로 부활하며, 대기 중 피격·충돌마다 부활 HP가 10씩 감소한다. 부활 최대 체력은 70이며 지팡이도 계속 획득할 수 있다. 지팡이는 사라지지 않고 등장 25초 뒤 자동 습득한다." },
      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 100,
        skillName: "템포 · Caravan", condition: "연주 8초 유지마다 템포 상승 · 피격 시 1단계 하락 · 20초마다 Caravan", desc: "주변 적에게 드럼 음파를 반복해서 퍼뜨린다. 연주를 끊기지 않고 이어갈수록 기본→업템포→광란으로 빨라지고 강해지며, 피해를 받으면 템포가 한 단계 떨어진다. 20초마다 4초간 Caravan 솔로에 돌입해 빠른 광역 비트를 연속으로 울리고 마지막 심벌 크래시로 마무리한다." },'''
)

insert_anchor='''    function initRiddle(f) {
'''
andrum_code='''    const ANDRUM = {
      tempoRise: 8,
      intervals: [1.20, .90, .68],
      damages: [5, 6, 7],
      radii: [58, 66, 74],
      caravanPeriod: 20,
      caravanDuration: 4,
      caravanInterval: .45,
      caravanDamage: 3,
      caravanRadius: 82,
      crashDamage: 16,
      crashRadius: 100
    };

    function initAndrum(f) {
      f.andrum = {
        stage: 0,
        tempo: 0,
        beat: .7,
        pulse: 0,
        pulseRadius: 0,
        caravanCd: ANDRUM.caravanPeriod,
        caravan: 0,
        caravanBeat: 0,
        lastDamageTaken: f.damageTaken || 0
      };
    }

    function andrumStageName(stage) {
      return ["기본 템포", "업템포", "광란 템포"][clamp(stage || 0, 0, 2)] || "기본 템포";
    }

    function andrumWave(f, power, radius, label, color = "#fbbf24") {
      const victims = enemiesOf(f).filter(e => Math.hypot(e.x-f.x,e.y-f.y) <= radius + e.r);
      victims.forEach(e => {
        damage(e, power, f, label);
        spawnHitFlash(e.x, e.y, color, 20);
      });
      spawnBlast(f.x, f.y, radius, color);
      spawnParticles(f.x, f.y, color, 8);
      if (!fastSimMode) playSound("magic", .45);
      if (f.andrum) {
        f.andrum.pulse = .20;
        f.andrum.pulseRadius = radius;
      }
      return victims.length;
    }

    function updateAndrum(f, dt) {
      const a = f?.andrum;
      if (!a || !f.alive) return;
      a.pulse = Math.max(0, a.pulse - dt);

      const taken = f.damageTaken || 0;
      if (taken > a.lastDamageTaken + .001) {
        if (a.stage > 0) {
          a.stage -= 1;
          spawnFloatingText(f.x, f.y-f.r-36, "템포 흔들림", "#fca5a5");
        }
        a.tempo = 0;
      }
      a.lastDamageTaken = taken;

      if (a.caravan > 0) {
        const before = a.caravan;
        a.caravan = Math.max(0, a.caravan - dt);
        a.caravanBeat -= dt;
        while (a.caravanBeat <= 0 && a.caravan > 0) {
          andrumWave(f, ANDRUM.caravanDamage, ANDRUM.caravanRadius, "Caravan 연타", "#fde68a");
          a.caravanBeat += ANDRUM.caravanInterval;
        }
        if (before > 0 && a.caravan <= 0) {
          andrumWave(f, ANDRUM.crashDamage, ANDRUM.crashRadius, "Caravan 심벌 크래시", "#f59e0b");
          spawnFloatingText(f.x, f.y-f.r-46, "CRASH!", "#fef3c7");
          a.caravanCd = ANDRUM.caravanPeriod;
          a.beat = ANDRUM.intervals[a.stage];
        }
        return;
      }

      a.caravanCd = Math.max(0, a.caravanCd - dt);
      if (a.caravanCd <= 0) {
        a.caravan = ANDRUM.caravanDuration;
        a.caravanBeat = 0;
        spawnFloatingText(f.x, f.y-f.r-46, "Caravan!", "#fde68a");
        return;
      }

      a.tempo += dt;
      if (a.stage < 2 && a.tempo >= ANDRUM.tempoRise) {
        a.stage += 1;
        a.tempo = 0;
        spawnFloatingText(f.x, f.y-f.r-36, andrumStageName(a.stage), "#fde68a");
      }

      a.beat -= dt;
      if (a.beat <= 0) {
        andrumWave(f, ANDRUM.damages[a.stage], ANDRUM.radii[a.stage], "드럼 비트", a.stage === 2 ? "#fb923c" : "#fbbf24");
        a.beat += ANDRUM.intervals[a.stage];
      }
    }

    function drawAndrumCharacter(f) {
      const a = f.andrum || {stage:0,pulse:0,caravan:0};
      if (!f.portraitOnly && a.pulse > 0) {
        const alpha = clamp(a.pulse / .20, 0, 1);
        ctx.save();
        ctx.globalAlpha = alpha * .75;
        ctx.strokeStyle = a.caravan > 0 ? "#fde68a" : (a.stage >= 2 ? "#fb923c" : "#fbbf24");
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(f.x, f.y, Math.max(f.r+8, (a.pulseRadius||60) * (1.08-alpha*.08)), 0, Math.PI*2);
        ctx.stroke();
        ctx.restore();
      }

      ctx.save();
      ctx.translate(f.x, f.y);
      ctx.scale(f.r/20, f.r/20);

      // 단순 도형형 사람.
      ctx.fillStyle = "#1f2937";
      ctx.fillRect(-8, -2, 16, 19);
      ctx.fillStyle = "#e7c3a4";
      ctx.beginPath(); ctx.arc(0, -12, 8, 0, Math.PI*2); ctx.fill();
      ctx.fillStyle = "#5b4636";
      ctx.beginPath(); ctx.arc(0, -15, 8, Math.PI, Math.PI*2); ctx.fill();
      ctx.strokeStyle = "#111827"; ctx.lineWidth = 1.5;
      ctx.beginPath(); ctx.moveTo(-4,-11); ctx.lineTo(-1,-11); ctx.moveTo(2,-11); ctx.lineTo(5,-11); ctx.stroke();

      // 스틱 두 개.
      const swing = Math.sin(battleTime * (a.caravan>0 ? 24 : 10 + a.stage*4)) * .35;
      ctx.strokeStyle = "#d6b37a"; ctx.lineWidth = 2;
      ctx.beginPath(); ctx.moveTo(-5,2); ctx.lineTo(-14,-7+swing*10); ctx.moveTo(5,2); ctx.lineTo(14,-7-swing*10); ctx.stroke();

      // 드럼 3개.
      ctx.fillStyle = "#7c2d12"; ctx.strokeStyle = "#f3f4f6"; ctx.lineWidth = 1.2;
      for (const [x,y,r] of [[-10,13,6],[10,13,6],[0,18,7]]) {
        ctx.beginPath(); ctx.arc(x,y,r,0,Math.PI*2); ctx.fill(); ctx.stroke();
      }
      // 심벌 2개.
      ctx.strokeStyle = "#9ca3af"; ctx.lineWidth = 1;
      ctx.beginPath(); ctx.moveTo(-16,8); ctx.lineTo(-16,-1); ctx.moveTo(16,8); ctx.lineTo(16,-1); ctx.stroke();
      ctx.fillStyle = "#fbbf24";
      ctx.beginPath(); ctx.ellipse(-16,-2,7,2.1,0,0,Math.PI*2); ctx.fill();
      ctx.beginPath(); ctx.ellipse(16,-2,7,2.1,0,0,Math.PI*2); ctx.fill();

      ctx.restore();
      drawHealthBar(f);
      drawName(f);
      if (!f.portraitOnly && a.caravan > 0) drawRing(f.x,f.y,f.r+9,"rgba(253,230,138,.8)",3);
    }

    function initRiddle(f) {
'''
rep(insert_anchor,andrum_code)

rep(
'''      if (c.id === "newhello_sergeant") initNewhello(fighter);
      if (c.id === "riddle_lord") initRiddle(fighter);''',
'''      if (c.id === "newhello_sergeant") initNewhello(fighter);
      if (c.id === "andrum") initAndrum(fighter);
      if (c.id === "riddle_lord") initRiddle(fighter);'''
)

rep(
'''      updateLisa(f, dt);
      updateOshi(f, dt);
      if (updatePowerPunch(f, dt)) return;''',
'''      updateLisa(f, dt);
      updateOshi(f, dt);
      if (f.andrum) updateAndrum(f, dt);
      if (!f.alive) return;
      if (updatePowerPunch(f, dt)) return;'''
)

rep(
'''      if (f.newhello) { drawNewhelloCharacter(f); return; }
      if (f.riddle) { drawRiddleCharacter(f); return; }''',
'''      if (f.newhello) { drawNewhelloCharacter(f); return; }
      if (f.andrum) { drawAndrumCharacter(f); return; }
      if (f.riddle) { drawRiddleCharacter(f); return; }'''
)

rep(
'''        if (c.id === "newhello_sergeant") initNewhello(preview);
        if (c.id === "hinta") preview.hinta = { pose: 0 };''',
'''        if (c.id === "newhello_sergeant") initNewhello(preview);
        if (c.id === "andrum") initAndrum(preview);
        if (c.id === "hinta") preview.hinta = { pose: 0 };'''
)

rep(
'''    function skillProgressInfo(f) {
      if(f.newhello){const n=f.newhello;return {ratio:clamp(1-n.cd/NEWHELLO.period,0,1),className:"skill-fill",''',
'''    function skillProgressInfo(f) {
      if(f.andrum){const a=f.andrum;return {ratio:a.caravan>0?clamp(a.caravan/ANDRUM.caravanDuration,0,1):clamp(a.tempo/ANDRUM.tempoRise,0,1),className:a.caravan>0?"rage-fill":"skill-fill",
        text:a.caravan>0?"Caravan 솔로 "+a.caravan.toFixed(1)+"초":andrumStageName(a.stage)+" · 다음 템포 "+Math.max(0,ANDRUM.tempoRise-a.tempo).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">비트 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · Caravan까지 ${a.caravanCd.toFixed(1)}초</div>`};}
      if(f.newhello){const n=f.newhello;return {ratio:clamp(1-n.cd/NEWHELLO.period,0,1),className:"skill-fill",'''
)

rep(
'''    function characterDamageInfo(c) {
      if(c.id==="newhello_sergeant")return {damage:"일반 광역 회전베기8 / 와이어 광역 강습16 + 출혈1×5회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",''',
'''    function characterDamageInfo(c) {
      if(c.id==="andrum")return {damage:"드럼 비트 5/6/7 · 반경58/66/74 · Caravan 연타3(0.45초마다) · 마지막 심벌 크래시16/반경100",
        tick:"연주 유지8초마다 기본→업템포→광란 · 비트 간격1.20/0.90/0.68초 · 피격 시 템포 1단계 하락 · Caravan 20초마다 4초",
        tip:"직접 접촉 공격 없이 자기 주변에 원형 음파를 반복한다. 피해를 받으면 현재 템포가 한 단계 떨어지고 상승 진행도도 초기화된다. Caravan 동안 일반 비트 대신 0.45초마다 광역3 피해를 주며 종료 순간 반경100 심벌 크래시16으로 마무리한다."};
      if(c.id==="newhello_sergeant")return {damage:"일반 광역 회전베기8 / 와이어 광역 강습16 + 출혈1×5회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",'''
)

rep(
'''      const patchNotes = [
      "v85: 뉴헬로 병장 연속 와이어 상한 추가.''',
'''      const patchNotes = [
      "v86: 영화 캐릭터 앤드럼 추가. HP150·이속2.7. 직접 접촉 공격 대신 드럼 비트로 반경58/66/74에 5/6/7 광역 피해를 주며 8초간 피격 없이 연주를 이어가면 기본→업템포→광란으로 상승, 피격 시 1단계 하락. 20초마다 4초 Caravan 솔로로 0.45초마다 반경82 피해3을 연타하고 마지막 반경100 심벌 크래시16. 외형은 사람·드럼3개·심벌2개만 사용한 단순 도형형으로 구현.",
      "v85: 뉴헬로 병장 연속 와이어 상한 추가.'''
)

p.write_text(t,encoding="utf-8")
