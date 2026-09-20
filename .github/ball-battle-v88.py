from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:220]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v87</title>','<title>볼배틀 리뉴얼 v88</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v87</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v88</h1>')

rep(
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 210,
        skillName: "템포 · Caravan", condition: "연주 8초 유지마다 템포 상승 · 피격 시 상승 진행도 절반 · 16초마다 Caravan", desc: "주변 적에게 드럼 음파를 반복해서 퍼뜨린다. 연주를 이어갈수록 기본→업템포→광란으로 빨라지고 범위가 넓어진다. 피해를 받아도 단계는 내려가지 않고 다음 템포까지의 진행도만 절반으로 줄어든다. 16초마다 4초간 Caravan 솔로에 돌입해 넓은 광역 비트를 연속으로 울리고 마지막 대형 심벌 크래시로 마무리한다. 실제 드럼 패턴은 하이햇 8비트, 2·4박 스네어, 1·3박 킥으로 연주한다." },''',
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 210,
        skillName: "그루브 · WHIPLASH", condition: "140BPM 고정 · 4마디마다 탐 필인 · 킥 타격에 음파 공격 · 16초마다 WHIPLASH", desc: "140BPM을 끝까지 유지하며 하이햇 8비트, 2·4박 스네어, 1·3박 킥의 기본 그루브를 연주한다. 공격 판정은 킥과 정확히 동시에 발생한다. 4마디마다 하이·미드·플로어 탐을 섞은 1마디 필인을 넣고 다음 1박을 크래시로 연다. 연주를 유지하면 그루브 단계가 올라 피해와 범위가 강해지며, 피격 시 단계는 유지하고 다음 단계 진행도만 절반으로 줄어든다. 16초마다 4초간 WHIPLASH 드럼 솔로에 들어가 16비트 탐·스네어·킥을 몰아치고 마지막 대형 크래시로 마무리한다." },'''
)

rep(
'''    function playAndrumCrash() {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      noise(.75,.13,0,5200,"highpass");
      noise(.55,.07,.01,8500,"bandpass");
      tone(310,.32,"triangle",.035,0,210);
    }''',
'''    function playAndrumTom(kind = 1, strength = 1) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const s=Math.max(.5,Math.min(1.5,strength));
      const tones=[
        [235,145,.18,.105,1350],
        [180,105,.22,.115,1050],
        [128,68,.28,.13,760]
      ];
      const [start,end,dur,vol,click]=tones[clamp(kind|0,0,2)];
      tone(start,dur,"sine",vol*s,0,end);
      tone(start*1.52,dur*.65,"triangle",vol*.025*s,0,end*1.35);
      noise(.035,.032*s,0,click,"bandpass");
    }
    function playAndrumCrash(strength = 1) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const s=Math.max(.55,Math.min(1.5,strength));
      // 긴 금속성 꼬리: 서로 다른 대역의 노이즈를 겹쳐 얇은 '쉬익' 대신 실제 크래시처럼 퍼지게 한다.
      noise(1.15,.085*s,0,3300,"bandpass");
      noise(.95,.070*s,.004,5200,"bandpass");
      noise(.82,.052*s,.009,7600,"bandpass");
      noise(.68,.038*s,.014,9800,"highpass");
      tone(420,.22,"triangle",.018*s,0,310);
      tone(690,.16,"triangle",.012*s,.008,510);
    }'''
)

rep(
'''    const ANDRUM = {
      tempoRise: 8,
      intervals: [1.20, .90, .68],
      damages: [5, 6, 7],
      radii: [110, 135, 160],
      bpms: [110, 145, 180],
      caravanBpm: 220,
      caravanPeriod: 16,
      caravanDuration: 4,
      caravanInterval: .45,
      caravanDamage: 3,
      caravanRadius: 170,
      crashDamage: 16,
      crashRadius: 210
    };''',
'''    const ANDRUM = {
      grooveRise: 8,
      bpm: 140,
      damages: [5, 6, 7],
      radii: [110, 135, 160],
      fillBars: 4,
      whiplashPeriod: 16,
      whiplashDuration: 4,
      whiplashDamage: 3,
      whiplashRadius: 170,
      crashDamage: 16,
      crashRadius: 210
    };'''
)

rep(
'''      f.andrum = {
        stage: 0,
        tempo: 0,
        beat: .7,
        pulse: 0,
        pulseRadius: 0,
        caravanCd: ANDRUM.caravanPeriod,
        caravan: 0,
        caravanBeat: 0,
        drumStep: 0,
        drumClock: 0,
        lastDamageTaken: f.damageTaken || 0
      };''',
'''      f.andrum = {
        stage: 0,
        groove: 0,
        pulse: 0,
        pulseRadius: 0,
        whiplashCd: ANDRUM.whiplashPeriod,
        whiplash: 0,
        drumStep: 0,
        drumClock: 0,
        fillCrashPending: false,
        lastDamageTaken: f.damageTaken || 0
      };'''
)

rep(
'''    function andrumStageName(stage) {
      return ["기본 템포", "업템포", "광란 템포"][clamp(stage || 0, 0, 2)] || "기본 템포";
    }''',
'''    function andrumStageName(stage) {
      return ["기본 그루브", "몰입 그루브", "광란 그루브"][clamp(stage || 0, 0, 2)] || "기본 그루브";
    }'''
)

rep(
'''    function updateAndrumDrums(f, dt) {
      const a=f?.andrum;
      if(!a)return;
      const bpm=a.caravan>0?ANDRUM.caravanBpm:ANDRUM.bpms[a.stage];
      const eighth=30/bpm;
      a.drumClock-=dt;
      let safety=0;
      while(a.drumClock<=0 && safety++<6){
        const step=a.drumStep%8;
        playAndrumHiHat(step===0 || step===4);
        if(step===0 || step===4)playAndrumKick(a.caravan>0?1.15:1);
        if(step===2 || step===6)playAndrumSnare(a.caravan>0?1.15:1);
        a.drumStep=(step+1)%8;
        a.drumClock+=eighth;
      }
    }''',
'''    function andrumKickAttack(f, whiplash=false) {
      const a=f.andrum;
      if(!a || !f.alive)return;
      if(whiplash){
        andrumWave(f,ANDRUM.whiplashDamage,ANDRUM.whiplashRadius,"WHIPLASH 킥","#fde68a");
      }else{
        andrumWave(f,ANDRUM.damages[a.stage],ANDRUM.radii[a.stage],"킥 음파",a.stage===2?"#fb923c":"#fbbf24");
      }
    }

    function updateAndrumDrums(f, dt) {
      const a=f?.andrum;
      if(!a)return;
      const sixteenth=15/ANDRUM.bpm;
      const eighth=sixteenth*2;
      a.drumClock-=dt;
      let safety=0;

      while(a.drumClock<=0 && safety++<10){
        if(a.whiplash>0){
          // WHIPLASH는 BPM을 올리지 않고 같은 140BPM 안에서 16비트로 세분화한 솔로다.
          const s=a.drumStep%16;
          if(s===0){playAndrumCrash(1.05);playAndrumKick(1.2);andrumKickAttack(f,true);}
          else if(s===1)playAndrumTom(0,1.05);
          else if(s===2)playAndrumTom(0,.95);
          else if(s===3)playAndrumSnare(.85);
          else if(s===4){playAndrumKick(1.15);andrumKickAttack(f,true);playAndrumTom(1,.9);}
          else if(s===5)playAndrumTom(1,1.0);
          else if(s===6)playAndrumTom(0,.9);
          else if(s===7)playAndrumSnare(.95);
          else if(s===8){playAndrumKick(1.2);andrumKickAttack(f,true);playAndrumTom(1,.9);}
          else if(s===9)playAndrumTom(2,.95);
          else if(s===10)playAndrumTom(0,.9);
          else if(s===11)playAndrumTom(1,1.0);
          else if(s===12){playAndrumKick(1.2);andrumKickAttack(f,true);playAndrumTom(2,1.05);}
          else if(s===13)playAndrumTom(2,1.0);
          else if(s===14)playAndrumSnare(1.1);
          else {playAndrumTom(2,1.15);playAndrumCrash(.82);}
          a.drumStep=(s+1)%16;
          a.drumClock+=sixteenth;
          continue;
        }

        // 평상시는 고정 140BPM. 4마디째를 탐 필인으로 쓰고, 다음 마디 1박을 크래시로 연다.
        const cycle=a.drumStep%(ANDRUM.fillBars*8);
        const bar=Math.floor(cycle/8), step=cycle%8;
        const fill=bar===ANDRUM.fillBars-1;

        if(step===0 && a.fillCrashPending){
          playAndrumCrash(.92);
          a.fillCrashPending=false;
        }

        if(!fill){
          playAndrumHiHat(step===0 || step===4);
          if(step===0 || step===4){playAndrumKick(1);andrumKickAttack(f,false);}
          if(step===2 || step===6)playAndrumSnare(1);
        }else{
          // 1마디 필인: 앞 절반은 그루브를 지키고, 뒤로 갈수록 하이→미드→플로어 탐으로 내려간다.
          if(step===0){playAndrumHiHat(true);playAndrumKick(1.05);andrumKickAttack(f,false);}
          else if(step===1)playAndrumHiHat(false);
          else if(step===2)playAndrumSnare(1.05);
          else if(step===3)playAndrumTom(0,1.0);
          else if(step===4){playAndrumKick(1.08);andrumKickAttack(f,false);playAndrumTom(0,.9);}
          else if(step===5)playAndrumTom(1,1.05);
          else if(step===6){playAndrumSnare(.9);playAndrumTom(1,.9);}
          else {playAndrumTom(2,1.15);a.fillCrashPending=true;}
        }

        a.drumStep=(cycle+1)%(ANDRUM.fillBars*8);
        a.drumClock+=eighth;
      }
    }'''
)

rep(
'''    function updateAndrum(f, dt) {
      const a = f?.andrum;
      if (!a || !f.alive) return;
      a.pulse = Math.max(0, a.pulse - dt);
      updateAndrumDrums(f,dt);

      const taken = f.damageTaken || 0;
      if (taken > a.lastDamageTaken + .001) {
        a.tempo *= .5;
        spawnFloatingText(f.x, f.y-f.r-36, "템포 진행 -50%", "#fca5a5");
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
          playAndrumCrash();
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
    }''',
'''    function updateAndrum(f, dt) {
      const a = f?.andrum;
      if (!a || !f.alive) return;
      a.pulse = Math.max(0, a.pulse - dt);

      const taken = f.damageTaken || 0;
      if (taken > a.lastDamageTaken + .001) {
        a.groove *= .5;
        spawnFloatingText(f.x, f.y-f.r-36, "그루브 진행 -50%", "#fca5a5");
      }
      a.lastDamageTaken = taken;

      if(a.whiplash>0){
        const before=a.whiplash;
        updateAndrumDrums(f,dt);
        a.whiplash=Math.max(0,a.whiplash-dt);
        if(before>0 && a.whiplash<=0){
          andrumWave(f,ANDRUM.crashDamage,ANDRUM.crashRadius,"WHIPLASH 피날레 크래시","#f59e0b");
          playAndrumCrash(1.25);
          spawnFloatingText(f.x,f.y-f.r-46,"WHIPLASH · CRASH!","#fef3c7");
          a.whiplashCd=ANDRUM.whiplashPeriod;
          a.drumStep=0;a.drumClock=0;a.fillCrashPending=false;
        }
        return;
      }

      a.whiplashCd=Math.max(0,a.whiplashCd-dt);
      if(a.whiplashCd<=0){
        a.whiplash=ANDRUM.whiplashDuration;
        a.drumStep=0;a.drumClock=0;a.fillCrashPending=false;
        spawnFloatingText(f.x,f.y-f.r-46,"WHIPLASH!","#fde68a");
        return;
      }

      a.groove+=dt;
      if(a.stage<2 && a.groove>=ANDRUM.grooveRise){
        a.stage+=1;
        a.groove=0;
        spawnFloatingText(f.x,f.y-f.r-36,andrumStageName(a.stage),"#fde68a");
      }

      updateAndrumDrums(f,dt);
    }'''
)

# 앤드럼 그림의 특수 상태명을 caravan에서 whiplash로 교체 (해당 함수 내부 3곳)
rep('''      const a = f.andrum || {stage:0,pulse:0,caravan:0};''','''      const a = f.andrum || {stage:0,pulse:0,whiplash:0};''')
rep('''        ctx.strokeStyle = a.caravan > 0 ? "#fde68a" : (a.stage >= 2 ? "#fb923c" : "#fbbf24");''','''        ctx.strokeStyle = a.whiplash > 0 ? "#fde68a" : (a.stage >= 2 ? "#fb923c" : "#fbbf24");''')
rep('''      const swing = Math.sin(battleTime * (a.caravan>0 ? 24 : 10 + a.stage*4)) * .35;''','''      const swing = Math.sin(battleTime * (a.whiplash>0 ? 24 : 12)) * .35;''')
rep('''      if (!f.portraitOnly && a.caravan > 0) drawRing(f.x,f.y,f.r+9,"rgba(253,230,138,.8)",3);''','''      if (!f.portraitOnly && a.whiplash > 0) drawRing(f.x,f.y,f.r+9,"rgba(253,230,138,.8)",3);''')

rep(
'''      if(f.andrum){const a=f.andrum;return {ratio:a.caravan>0?clamp(a.caravan/ANDRUM.caravanDuration,0,1):clamp(a.tempo/ANDRUM.tempoRise,0,1),className:a.caravan>0?"rage-fill":"skill-fill",
        text:a.caravan>0?"Caravan 솔로 "+a.caravan.toFixed(1)+"초":andrumStageName(a.stage)+" · 다음 템포 "+Math.max(0,ANDRUM.tempoRise-a.tempo).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">비트 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · ${a.caravan>0?ANDRUM.caravanBpm:ANDRUM.bpms[a.stage]}BPM · Caravan까지 ${a.caravanCd.toFixed(1)}초</div>`};}''',
'''      if(f.andrum){const a=f.andrum;return {ratio:a.whiplash>0?clamp(a.whiplash/ANDRUM.whiplashDuration,0,1):clamp(a.groove/ANDRUM.grooveRise,0,1),className:a.whiplash>0?"rage-fill":"skill-fill",
        text:a.whiplash>0?"WHIPLASH 솔로 "+a.whiplash.toFixed(1)+"초":andrumStageName(a.stage)+" · 다음 그루브 "+Math.max(0,ANDRUM.grooveRise-a.groove).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">킥 공격 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · 고정 ${ANDRUM.bpm}BPM · WHIPLASH까지 ${a.whiplashCd.toFixed(1)}초</div>`};}'''
)

rep(
'''      if(c.id==="andrum")return {damage:"드럼 비트 5/6/7 · 반경110/135/160 · Caravan 연타3(0.45초마다, 반경170) · 마지막 심벌 크래시16/반경210",
        tick:"연주 유지8초마다 기본→업템포→광란 · 비트 간격1.20/0.90/0.68초 · 피격 시 단계 유지·상승 진행도 50% 감소 · Caravan 16초마다 4초 · 드럼 110/145/180BPM(솔로220)",
        tip:"직접 접촉 공격 없이 넓은 원형 음파를 반복한다. 피해를 받아도 템포 단계는 내려가지 않고 다음 단계 진행도만 절반으로 줄어든다. 실제 드럼 사운드는 하이햇 8비트, 2·4박 스네어, 1·3박 킥 패턴이며 템포 단계가 오를수록 BPM도 빨라진다. Caravan 종료 순간 반경210 심벌 크래시16으로 마무리한다."};''',
'''      if(c.id==="andrum")return {damage:"킥 음파 5/6/7 · 반경110/135/160 · WHIPLASH 킥3/반경170 · 피날레 크래시16/반경210",
        tick:"140BPM 고정 · 하이햇8비트 / 스네어2·4 / 킥1·3 · 4마디마다 1마디 탐 필인 · 연주 유지8초마다 그루브 강화 · 피격 시 단계 유지·진행도50% 감소 · WHIPLASH 16초마다 4초",
        tip:"공격 판정은 킥 사운드가 나는 순간과 정확히 동시에 발생한다. 평상시는 140BPM을 유지하며 4번째 마디에 하이→미드→플로어 탐 필인을 넣고 다음 1박을 크래시로 연다. WHIPLASH도 BPM 자체는 140으로 고정하고 16비트 세분화 솔로를 연주하며, 솔로 중 킥마다 광역3 피해가 발생한다. 마지막에는 새 크래시 사운드와 반경210 피해16으로 마무리한다."};'''
)

rep(
'''      const patchNotes = [
      "v87: 앤드럼 대규모 상향 및 드럼 사운드 교체.''',
'''      const patchNotes = [
      "v88: 앤드럼 리듬 시스템 개편. 전투 중 BPM 상승을 제거하고 140BPM으로 고정. 기본 그루브는 하이햇 8비트·2/4박 스네어·1/3박 킥이며 공격 판정을 독립 타이머가 아닌 실제 킥 순간에 동기화. 4마디마다 하이/미드/플로어 3종 탐을 사용한 1마디 필인 후 다음 1박 크래시. Caravan 명칭을 WHIPLASH로 변경하고 4초간 같은 140BPM의 16비트 드럼 솔로로 재구성, 솔로 킥마다 기존 피해3/반경170 적용·피날레16/반경210 유지. 크래시 심벌은 다중 금속성 대역과 긴 감쇠로 재합성. 그루브 단계 피해5/6/7·반경110/135/160 및 피격 시 진행도50% 감소는 유지.",
      "v87: 앤드럼 대규모 상향 및 드럼 사운드 교체.'''
)

p.write_text(t,encoding="utf-8")
