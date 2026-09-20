from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:220]!r}")
    t=t.replace(old,new,count)

def between(start,end,new):
    global t
    a=t.find(start)
    b=t.find(end,a)
    if a<0 or b<0:
        raise SystemExit(f"markers not found: {start!r} -> {end!r}")
    t=t[:a]+new+t[b:]

rep('<title>볼배틀 리뉴얼 v88</title>','<title>볼배틀 리뉴얼 v89</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v88</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v89</h1>')

rep(
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 210,
        skillName: "그루브 · WHIPLASH", condition: "140BPM 고정 · 4마디마다 탐 필인 · 킥 타격에 음파 공격 · 16초마다 WHIPLASH", desc: "140BPM을 끝까지 유지하며 하이햇 8비트, 2·4박 스네어, 1·3박 킥의 기본 그루브를 연주한다. 공격 판정은 킥과 정확히 동시에 발생한다. 4마디마다 하이·미드·플로어 탐을 섞은 1마디 필인을 넣고 다음 1박을 크래시로 연다. 연주를 유지하면 그루브 단계가 올라 피해와 범위가 강해지며, 피격 시 단계는 유지하고 다음 단계 진행도만 절반으로 줄어든다. 16초마다 4초간 WHIPLASH 드럼 솔로에 들어가 16비트 탐·스네어·킥을 몰아치고 마지막 대형 크래시로 마무리한다." },''',
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 210,
        skillName: "그루브 · WHIPLASH", condition: "140BPM 고정 · 4마디마다 16비트 탐 필인 · 킥과 공격 완전 동기화 · WHIPLASH는 쿨 완료 후 다음 마디 시작", desc: "140BPM을 끝까지 유지한다. 기본 그루브는 하이햇 8비트·2/4박 스네어·1/3박 킥으로 시작하지만 그루브 단계가 오르면 오픈 하이햇·고스트 스네어·탐 악센트·16비트 하이햇이 더해져 구성 자체가 복잡해진다. 모든 음파 공격은 실제 킥 소리와 같은 순간에 발생하고 공격 원은 앤드럼 중심에 붙어서 표시된다. 4마디마다 마지막 두 박을 하이→미드→플로어 탐 16비트 필인으로 채운다. WHIPLASH 쿨이 차도 즉시 끼어들지 않고 다음 마디 첫 박에서 2마디짜리 정형 드럼 솔로를 시작한다." },'''
)

between(
'''    function playAndrumHiHat(accent = false) {''',
'''    function playSound(name, strength = 1) {''',
'''    function playAndrumHiHat(accent = false, open = false) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const dur=open?.22:(accent?.07:.045);
      const vol=open?.048:(accent?.038:.024);
      noise(dur,vol,0,open?6400:7600,"highpass");
      noise(open?.14:.026,open?.022:(accent?.017:.011),0,open?9200:10800,"bandpass");
    }
    function playAndrumTom(kind = 1, strength = 1) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const s=Math.max(.5,Math.min(1.5,strength));
      const tones=[
        [260,165,.17,.105,1500],
        [190,108,.22,.115,1080],
        [132,64,.30,.135,720]
      ];
      const [start,end,dur,vol,click]=tones[clamp(kind|0,0,2)];
      tone(start,dur,"sine",vol*s,0,end);
      tone(start*1.47,dur*.56,"triangle",vol*.026*s,0,end*1.28);
      noise(.032,.034*s,0,click,"bandpass");
    }
    function playAndrumCrash(strength = 1) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const s=Math.max(.55,Math.min(1.5,strength));
      // 크래시: 짧은 어택 + 여러 비정수 금속 공명 + 긴 고역 꼬리.
      noise(.075,.095*s,0,2100,"bandpass");
      noise(1.35,.070*s,.004,3600,"bandpass");
      noise(1.18,.058*s,.007,5600,"bandpass");
      noise(1.00,.045*s,.011,7800,"bandpass");
      noise(.82,.033*s,.016,10500,"highpass");
      const partials=[[487,.010,.56],[733,.008,.62],[1091,.007,.70],[1489,.006,.78],[2143,.0045,.84]];
      partials.forEach(([freq,vol,dur],i)=>tone(freq,dur,"triangle",vol*s,i*.002,freq*(.78+i*.025)));
    }

'''
)

new_block='''    const ANDRUM = {
      grooveRise: 8,
      bpm: 140,
      damages: [5, 6, 7],
      radii: [110, 135, 160],
      fillBars: 4,
      whiplashPeriod: 16,
      whiplashSteps: 32,
      whiplashDamage: 3,
      whiplashRadius: 170,
      crashDamage: 16,
      crashRadius: 210
    };

    function initAndrum(f) {
      f.andrum = {
        stage: 0,
        groove: 0,
        pulse: 0,
        pulseRadius: 0,
        pulseColor: "#fbbf24",
        whiplashCd: ANDRUM.whiplashPeriod,
        whiplashReady: false,
        whiplash: false,
        whiplashStep: 0,
        drumStep: 0,
        drumClock: 0,
        fillCrashPending: false,
        lastDamageTaken: f.damageTaken || 0
      };
    }

    function andrumStageName(stage) {
      return ["기본 그루브", "몰입 그루브", "광란 그루브"][clamp(stage || 0, 0, 2)] || "기본 그루브";
    }

    function andrumWave(f, power, radius, label, color = "#fbbf24") {
      const victims = enemiesOf(f).filter(e => Math.hypot(e.x-f.x,e.y-f.y) <= radius + e.r);
      victims.forEach(e => {
        damage(e, power, f, label);
        spawnHitFlash(e.x, e.y, color, 20);
      });
      // 공격 원은 월드 좌표에 남기는 폭발 이펙트가 아니라 앤드럼 본체에 붙은 단일 원만 사용한다.
      if (f.andrum) {
        f.andrum.pulse = .11;
        f.andrum.pulseRadius = radius;
        f.andrum.pulseColor = color;
      }
      return victims.length;
    }

    function andrumKickAttack(f, whiplash=false) {
      const a=f.andrum;
      if(!a || !f.alive)return;
      if(whiplash)andrumWave(f,ANDRUM.whiplashDamage,ANDRUM.whiplashRadius,"WHIPLASH 킥","#fde68a");
      else andrumWave(f,ANDRUM.damages[a.stage],ANDRUM.radii[a.stage],"킥 음파",a.stage===2?"#fb923c":"#fbbf24");
    }

    function andrumRhythmReady() {
      if(fastSimMode || !soundEnabled)return true;
      ensureAudio();
      return !!audioCtx && audioCtx.state==="running";
    }

    function andrumKick(f,strength=1,whiplash=false) {
      playAndrumKick(strength);
      andrumKickAttack(f,whiplash);
    }

    function playAndrumStageGroove(f,step) {
      const a=f.andrum,stage=a.stage;
      if(stage===0){
        if(step%2===0)playAndrumHiHat(step===0||step===8);
        if(step===0||step===8)andrumKick(f,1,false);
        if(step===4||step===12)playAndrumSnare(1);
        return;
      }
      if(stage===1){
        if(step%2===0)playAndrumHiHat(step===0||step===8,step===14);
        if(step===0||step===8)andrumKick(f,1.04,false);
        if(step===4||step===12)playAndrumSnare(1.03);
        if(step===11)playAndrumSnare(.38);
        if(step===15)playAndrumTom(0,.62);
        return;
      }
      // 최고 단계도 BPM은 140 그대로. 16비트 하이햇·고스트노트·탐 악센트로 밀도만 높인다.
      playAndrumHiHat(step%4===0,step===14);
      if(step===0||step===8)andrumKick(f,1.08,false);
      if(step===4||step===12)playAndrumSnare(1.08);
      if(step===3||step===7||step===11||step===15)playAndrumSnare(.34);
      if(step===6)playAndrumTom(0,.55);
      if(step===14)playAndrumTom(1,.62);
    }

    function playAndrumFillStep(f,step) {
      // 4번째 마디의 앞 두 박은 그루브, 뒤 두 박은 16비트 하강형 탐 필인.
      if(step<8){
        playAndrumStageGroove(f,step);
        return;
      }
      if(step===8)playAndrumSnare(1.08);
      else if(step===9)playAndrumTom(0,1.02);
      else if(step===10)playAndrumTom(0,1.08);
      else if(step===11)playAndrumTom(1,1.02);
      else if(step===12){playAndrumSnare(.95);andrumKick(f,1.08,false);}
      else if(step===13)playAndrumTom(1,1.10);
      else if(step===14)playAndrumTom(2,1.08);
      else if(step===15){playAndrumTom(2,1.22);f.andrum.fillCrashPending=true;}
    }

    function startAndrumWhiplash(f) {
      const a=f.andrum;
      a.whiplash=true;
      a.whiplashReady=false;
      a.whiplashStep=0;
      a.drumClock=0;
      a.fillCrashPending=false;
      spawnFloatingText(f.x,f.y-f.r-46,"WHIPLASH!","#fde68a");
    }

    function finishAndrumWhiplash(f) {
      const a=f.andrum;
      a.whiplash=false;
      a.whiplashStep=0;
      a.whiplashCd=ANDRUM.whiplashPeriod;
      a.whiplashReady=false;
      a.drumStep=0;
      a.fillCrashPending=false;
      andrumWave(f,ANDRUM.crashDamage,ANDRUM.crashRadius,"WHIPLASH 피날레 크래시","#f59e0b");
      playAndrumCrash(1.28);
      spawnFloatingText(f.x,f.y-f.r-46,"WHIPLASH · CRASH!","#fef3c7");
    }

    function playAndrumWhiplashStep(f,s) {
      // 2마디 고정 프레이즈. 랜덤 없이 '제시→하강→응답→피날레' 구조로 들리게 한다.
      const bar=Math.floor(s/16),step=s%16;
      if(bar===0){
        if(step===0){playAndrumCrash(.82);andrumKick(f,1.16,true);}
        else if(step===1)playAndrumTom(0,1.02);
        else if(step===2)playAndrumTom(0,1.00);
        else if(step===3)playAndrumSnare(.92);
        else if(step===4){playAndrumSnare(1.12);andrumKick(f,1.08,true);}
        else if(step===5)playAndrumTom(0,.98);
        else if(step===6)playAndrumTom(1,1.05);
        else if(step===7)playAndrumTom(1,1.08);
        else if(step===8){andrumKick(f,1.14,true);playAndrumTom(2,.92);}
        else if(step===9)playAndrumTom(0,.90);
        else if(step===10)playAndrumTom(1,.98);
        else if(step===11)playAndrumTom(2,1.05);
        else if(step===12)playAndrumSnare(1.15);
        else if(step===13)playAndrumTom(0,1.02);
        else if(step===14)playAndrumTom(1,1.10);
        else if(step===15)playAndrumTom(2,1.20);
      }else{
        if(step===0){andrumKick(f,1.15,true);playAndrumTom(2,.92);}
        else if(step===1)playAndrumTom(2,.96);
        else if(step===2)playAndrumSnare(.72);
        else if(step===3)playAndrumTom(0,.92);
        else if(step===4)playAndrumSnare(1.18);
        else if(step===5)playAndrumTom(0,1.00);
        else if(step===6)playAndrumTom(1,1.06);
        else if(step===7)playAndrumTom(2,1.12);
        else if(step===8)andrumKick(f,1.20,true);
        else if(step===9)playAndrumTom(0,.98);
        else if(step===10)playAndrumTom(0,1.04);
        else if(step===11)playAndrumTom(1,1.08);
        else if(step===12){playAndrumSnare(1.20);andrumKick(f,1.12,true);}
        else if(step===13)playAndrumTom(1,1.08);
        else if(step===14)playAndrumTom(2,1.14);
        else if(step===15)playAndrumTom(2,1.26);
      }
    }

    function updateAndrumDrums(f,dt) {
      const a=f?.andrum;
      if(!a || !andrumRhythmReady())return;

      const sixteenth=15/ANDRUM.bpm;
      const eighth=sixteenth*2;
      a.drumClock-=dt;
      let safety=0;

      while(a.drumClock<=0 && safety++<12){
        if(a.whiplash){
          const s=a.whiplashStep;
          playAndrumWhiplashStep(f,s);
          a.whiplashStep+=1;
          if(a.whiplashStep>=ANDRUM.whiplashSteps){
            finishAndrumWhiplash(f);
            a.drumClock+=eighth;
          }else{
            a.drumClock+=sixteenth;
          }
          continue;
        }

        const cycle=a.drumStep%(ANDRUM.fillBars*16);
        const step=cycle%16;

        // 쿨타임이 끝나도 현재 마디를 자르지 않는다. 다음 마디의 1박에서만 솔로 진입.
        if(a.whiplashReady && step===0){
          startAndrumWhiplash(f);
          continue;
        }

        if(step===0 && a.fillCrashPending){
          playAndrumCrash(.92);
          a.fillCrashPending=false;
        }

        const bar=Math.floor(cycle/16);
        if(bar===ANDRUM.fillBars-1)playAndrumFillStep(f,step);
        else playAndrumStageGroove(f,step);

        a.drumStep=(cycle+1)%(ANDRUM.fillBars*16);
        a.drumClock+=sixteenth;
      }
    }

    function updateAndrum(f, dt) {
      const a=f?.andrum;
      if(!a || !f.alive)return;
      a.pulse=Math.max(0,a.pulse-dt);

      const taken=f.damageTaken||0;
      if(taken>a.lastDamageTaken+.001){
        a.groove*=.5;
        spawnFloatingText(f.x,f.y-f.r-36,"그루브 진행 -50%","#fca5a5");
      }
      a.lastDamageTaken=taken;

      if(!a.whiplash){
        a.whiplashCd=Math.max(0,a.whiplashCd-dt);
        if(a.whiplashCd<=0)a.whiplashReady=true;

        a.groove+=dt;
        if(a.stage<2 && a.groove>=ANDRUM.grooveRise){
          a.stage+=1;
          a.groove=0;
          spawnFloatingText(f.x,f.y-f.r-36,andrumStageName(a.stage),"#fde68a");
        }
      }

      updateAndrumDrums(f,dt);
    }

'''
between('''    const ANDRUM = {''','''    function drawAndrumCharacter(f) {''',new_block)

rep(
'''      const a = f.andrum || {stage:0,pulse:0,whiplash:0};
      if (!f.portraitOnly && a.pulse > 0) {
        const alpha = clamp(a.pulse / .20, 0, 1);
        ctx.save();
        ctx.globalAlpha = alpha * .75;
        ctx.strokeStyle = a.whiplash > 0 ? "#fde68a" : (a.stage >= 2 ? "#fb923c" : "#fbbf24");
        ctx.lineWidth = 3;
        ctx.beginPath();
        ctx.arc(f.x, f.y, Math.max(f.r+8, (a.pulseRadius||60) * (1.08-alpha*.08)), 0, Math.PI*2);
        ctx.stroke();
        ctx.restore();
      }''',
'''      const a = f.andrum || {stage:0,pulse:0,whiplash:false,pulseColor:"#fbbf24"};
      if (!f.portraitOnly && a.pulse > 0) {
        const alpha=clamp(a.pulse/.11,0,1);
        ctx.save();
        ctx.globalAlpha=.88*alpha;
        ctx.strokeStyle=a.pulseColor||(a.whiplash?"#fde68a":a.stage>=2?"#fb923c":"#fbbf24");
        ctx.lineWidth=4;
        ctx.beginPath();
        // 실제 피해 반경과 같은 단 하나의 원. 좌표는 매 프레임 현재 앤드럼 위치를 사용하므로 이동해도 몸에 붙어 다닌다.
        ctx.arc(f.x,f.y,a.pulseRadius||ANDRUM.radii[a.stage],0,Math.PI*2);
        ctx.stroke();
        ctx.restore();
      }'''
)

rep(
'''      if(f.andrum){const a=f.andrum;return {ratio:a.whiplash>0?clamp(a.whiplash/ANDRUM.whiplashDuration,0,1):clamp(a.groove/ANDRUM.grooveRise,0,1),className:a.whiplash>0?"rage-fill":"skill-fill",
        text:a.whiplash>0?"WHIPLASH 솔로 "+a.whiplash.toFixed(1)+"초":andrumStageName(a.stage)+" · 다음 그루브 "+Math.max(0,ANDRUM.grooveRise-a.groove).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">킥 공격 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · 고정 ${ANDRUM.bpm}BPM · WHIPLASH까지 ${a.whiplashCd.toFixed(1)}초</div>`};}''',
'''      if(f.andrum){const a=f.andrum,remain=a.whiplash?(ANDRUM.whiplashSteps-a.whiplashStep)*(15/ANDRUM.bpm):0;return {ratio:a.whiplash?clamp(a.whiplashStep/ANDRUM.whiplashSteps,0,1):clamp(a.groove/ANDRUM.grooveRise,0,1),className:a.whiplash?"rage-fill":"skill-fill",
        text:a.whiplash?"WHIPLASH 솔로 · "+remain.toFixed(1)+"초":a.whiplashReady?"WHIPLASH 준비 · 다음 마디에서 시작":andrumStageName(a.stage)+" · 다음 그루브 "+Math.max(0,ANDRUM.grooveRise-a.groove).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">킥 공격 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · 고정 ${ANDRUM.bpm}BPM · ${a.whiplashReady?"다음 마디 WHIPLASH":"WHIPLASH까지 "+a.whiplashCd.toFixed(1)+"초"}</div>`};}'''
)

rep(
'''      if(c.id==="andrum")return {damage:"킥 음파 5/6/7 · 반경110/135/160 · WHIPLASH 킥3/반경170 · 피날레 크래시16/반경210",
        tick:"140BPM 고정 · 하이햇8비트 / 스네어2·4 / 킥1·3 · 4마디마다 1마디 탐 필인 · 연주 유지8초마다 그루브 강화 · 피격 시 단계 유지·진행도50% 감소 · WHIPLASH 16초마다 4초",
        tip:"공격 판정은 킥 사운드가 나는 순간과 정확히 동시에 발생한다. 평상시는 140BPM을 유지하며 4번째 마디에 하이→미드→플로어 탐 필인을 넣고 다음 1박을 크래시로 연다. WHIPLASH도 BPM 자체는 140으로 고정하고 16비트 세분화 솔로를 연주하며, 솔로 중 킥마다 광역3 피해가 발생한다. 마지막에는 새 크래시 사운드와 반경210 피해16으로 마무리한다."};''',
'''      if(c.id==="andrum")return {damage:"킥 음파 5/6/7 · 반경110/135/160 · WHIPLASH 킥3/반경170 · 피날레 크래시16/반경210",
        tick:"140BPM 고정 · 모든 공격은 실제 킥과 동시 · 4마디마다 뒤 2박 16비트 탐 필인 · 그루브 유지8초마다 단계 상승 · 피격 시 단계 유지·진행도50% 감소 · WHIPLASH 쿨16초 후 다음 마디에서 2마디 솔로",
        tip:"공격 원은 킥 순간에만 짧게 나타나는 단일 원이며 항상 앤드럼 현재 위치를 중심으로 따라다닌다. 기본 단계는 8비트 하이햇·2/4 스네어·1/3 킥, 몰입 단계는 오픈 하이햇·고스트 스네어·하이탐 픽업, 광란 단계는 16비트 하이햇·고스트 스네어·탐 악센트가 추가된다. 필인은 하이→미드→플로어 탐으로 명확히 하강하며 다음 마디 크래시로 복귀한다. WHIPLASH는 쿨이 차도 박자를 자르지 않고 다음 마디 1박에서 시작하는 고정 2마디 솔로다."};'''
)

rep(
'''      const patchNotes = [
      "v88: 앤드럼 리듬 시스템 개편.''',
'''      const patchNotes = [
      "v89: 앤드럼 리듬/판정 동기화 개선. 오디오 컨텍스트가 실제 재생 상태가 되기 전에는 평상시 공격 이펙트와 킥 판정을 시작하지 않아 경기 시작 시 시각 공격이 소리보다 먼저 나가던 현상을 제거. 공격 이펙트는 기존 spawnBlast와 본체 원이 겹치던 이중 원을 없애고 킥 순간 0.11초간 실제 피해 반경과 동일한 단일 원만 앤드럼 현재 위치에 부착 표시. 4마디 필인은 뒤 2박을 16비트 하이→미드→플로어 탐으로 재구성하고 다음 마디 크래시로 복귀. WHIPLASH는 쿨 완료 즉시가 아니라 다음 마디 1박에서 시작하며 랜덤성 없는 2마디 정형 솔로로 변경. 단계별 BPM은 140 고정하되 기본→몰입→광란에서 오픈 하이햇·고스트 스네어·탐 악센트·16비트 하이햇이 추가되도록 편곡. 크래시는 어택·5개 비정수 금속 공명·다중 고역 꼬리로 다시 합성. 피해/반경 수치는 v88 유지.",
      "v88: 앤드럼 리듬 시스템 개편.'''
)

p.write_text(t,encoding="utf-8")
