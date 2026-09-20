from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:240]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v90</title>','<title>볼배틀 리뉴얼 v91</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v90</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v91</h1>')

rep(
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 210,
        skillName: "그루브 · WHIPLASH", condition: "140BPM 고정 · 4마디마다 16비트 탐 필인 · 킥과 공격 완전 동기화 · WHIPLASH는 쿨 완료 후 다음 마디 시작", desc: "140BPM을 끝까지 유지한다. 기본 그루브는 하이햇 8비트·2/4박 스네어·1/3박 킥으로 시작하지만 그루브 단계가 오르면 오픈 하이햇·고스트 스네어·탐 악센트·16비트 하이햇이 더해져 구성 자체가 복잡해진다. 모든 음파 공격은 실제 킥 소리와 같은 순간에 발생하고 공격 원은 앤드럼 중심에 붙어서 표시된다. 4마디마다 마지막 두 박을 하이→미드→플로어 탐 16비트 필인으로 채운다. WHIPLASH 쿨이 차도 즉시 끼어들지 않고 다음 마디 첫 박에서 2마디짜리 정형 드럼 솔로를 시작한다." },''',
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 210,
        skillName: "그루브 · WHIPLASH", condition: "그루브 0~300 · 피격 피해×3만큼 감소 · 적중 킥마다 솔로게이지+5 · 100에서 다음 마디 WHIPLASH", desc: "140BPM 고정. 그루브는 0~300 수치로 누적되며 0~100 기본, 101~200 몰입, 201~300 광란 단계다. 평소 초당12.5씩 쌓이지만 피해를 받으면 실제 받은 피해의 3배만큼 즉시 깎여 단계가 다시 내려갈 수 있다. 적에게 실제 피해를 준 일반 킥마다 별도 WHIPLASH 게이지가 5씩 오르고 100이 되면 다음 마디 첫 박에서 2마디 솔로를 시작한다. 단계별 편곡·필인·킥 동기화 공격장은 유지된다." },'''
)

rep(
'''    const ANDRUM = {
      grooveRise: 8,
      bpm: 140,
      damages: [5, 6, 7],
      radii: [110, 135, 160],
      fillBars: 4,
      whiplashPeriod: 16,
      whiplashSteps: 32,
      whiplashDamage: 3,
      crashDamage: 16,
      crashRadius: 210
    };''',
'''    const ANDRUM = {
      grooveMax: 300,
      grooveGainPerSecond: 12.5,
      grooveDamageLossMultiplier: 3,
      soloMax: 100,
      soloGainOnHit: 5,
      bpm: 140,
      damages: [5, 6, 7],
      radii: [110, 135, 160],
      fillBars: 4,
      whiplashSteps: 32,
      whiplashDamage: 3,
      crashDamage: 16,
      crashRadius: 210
    };'''
)

rep(
'''        stage: 0,
        groove: 0,
        pulse: 0,
        pulseRadius: 0,
        pulseColor: "#fbbf24",
        whiplashCd: ANDRUM.whiplashPeriod,
        whiplashReady: false,''',
'''        stage: 0,
        groove: 0,
        soloGauge: 0,
        pulse: 0,
        pulseRadius: 0,
        pulseColor: "#fbbf24",
        whiplashReady: false,'''
)

rep(
'''    function andrumStageName(stage) {
      return ["기본 그루브", "몰입 그루브", "광란 그루브"][clamp(stage || 0, 0, 2)] || "기본 그루브";
    }''',
'''    function andrumStageFromGroove(value) {
      const g=clamp(value||0,0,ANDRUM.grooveMax);
      return g<=100?0:g<=200?1:2;
    }

    function andrumStageName(stage) {
      return ["기본 그루브", "몰입 그루브", "광란 그루브"][clamp(stage || 0, 0, 2)] || "기본 그루브";
    }

    function syncAndrumStage(f, announce=false) {
      const a=f?.andrum;
      if(!a)return;
      const old=a.stage||0;
      a.stage=andrumStageFromGroove(a.groove);
      if(announce && old!==a.stage){
        spawnFloatingText(f.x,f.y-f.r-36,andrumStageName(a.stage),a.stage<old?"#fca5a5":"#fde68a");
      }
    }'''
)

rep(
'''    function andrumWave(f, power, radius, label, color = "#fbbf24") {
      const victims = enemiesOf(f).filter(e => Math.hypot(e.x-f.x,e.y-f.y) <= radius + e.r);
      victims.forEach(e => {
        damage(e, power, f, label);
        spawnHitFlash(e.x, e.y, color, 20);
      });
      // 공격 원은 월드 좌표에 남기는 폭발 이펙트가 아니라 앤드럼 본체에 붙은 단일 원만 사용한다.
      if (f.andrum) {
        f.andrum.pulse = .26;
        f.andrum.pulseRadius = radius;
        f.andrum.pulseColor = color;
      }
      return victims.length;
    }''',
'''    function andrumWave(f, power, radius, label, color = "#fbbf24") {
      const victims = enemiesOf(f).filter(e => Math.hypot(e.x-f.x,e.y-f.y) <= radius + e.r);
      let landed=0;
      victims.forEach(e => {
        const dealt=damage(e, power, f, label);
        if(dealt>0)landed+=1;
        spawnHitFlash(e.x, e.y, color, 20);
      });
      // 공격 원은 월드 좌표에 남기는 폭발 이펙트가 아니라 앤드럼 본체에 붙은 단일 원만 사용한다.
      if (f.andrum) {
        f.andrum.pulse = .26;
        f.andrum.pulseRadius = radius;
        f.andrum.pulseColor = color;
      }
      return landed;
    }'''
)

rep(
'''    function andrumKickAttack(f, whiplash=false) {
      const a=f.andrum;
      if(!a || !f.alive)return;
      const radius=ANDRUM.radii[a.stage];
      if(whiplash)andrumWave(f,ANDRUM.whiplashDamage,radius,"WHIPLASH 킥","#fde68a");
      else andrumWave(f,ANDRUM.damages[a.stage],radius,"킥 음파",a.stage===2?"#fb923c":"#fbbf24");
    }''',
'''    function andrumKickAttack(f, whiplash=false) {
      const a=f.andrum;
      if(!a || !f.alive)return;
      const radius=ANDRUM.radii[a.stage];
      if(whiplash){
        andrumWave(f,ANDRUM.whiplashDamage,radius,"WHIPLASH 킥","#fde68a");
        return;
      }
      const landed=andrumWave(f,ANDRUM.damages[a.stage],radius,"킥 음파",a.stage===2?"#fb923c":"#fbbf24");
      if(landed>0 && !a.whiplashReady){
        a.soloGauge=clamp(a.soloGauge+ANDRUM.soloGainOnHit,0,ANDRUM.soloMax);
        if(a.soloGauge>=ANDRUM.soloMax){
          a.soloGauge=ANDRUM.soloMax;
          a.whiplashReady=true;
          spawnFloatingText(f.x,f.y-f.r-54,"WHIPLASH 준비!","#fde68a");
        }
      }
    }'''
)

rep(
'''    function startAndrumWhiplash(f) {
      const a=f.andrum;
      a.whiplash=true;
      a.whiplashReady=false;
      a.whiplashStep=0;
      a.drumClock=0;
      a.fillCrashPending=false;
      spawnFloatingText(f.x,f.y-f.r-46,"WHIPLASH!","#fde68a");
    }''',
'''    function startAndrumWhiplash(f) {
      const a=f.andrum;
      a.whiplash=true;
      a.whiplashReady=false;
      a.soloGauge=0;
      a.whiplashStep=0;
      a.drumClock=0;
      a.fillCrashPending=false;
      spawnFloatingText(f.x,f.y-f.r-46,"WHIPLASH!","#fde68a");
    }'''
)

rep(
'''      a.whiplash=false;
      a.whiplashStep=0;
      a.whiplashCd=ANDRUM.whiplashPeriod;
      a.whiplashReady=false;
      a.drumStep=0;''',
'''      a.whiplash=false;
      a.whiplashStep=0;
      a.whiplashReady=false;
      a.drumStep=0;'''
)

rep(
'''    function updateAndrum(f, dt) {
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
    }''',
'''    function updateAndrum(f, dt) {
      const a=f?.andrum;
      if(!a || !f.alive)return;
      a.pulse=Math.max(0,a.pulse-dt);

      const taken=f.damageTaken||0;
      const incoming=Math.max(0,taken-a.lastDamageTaken);
      if(incoming>.001){
        const loss=incoming*ANDRUM.grooveDamageLossMultiplier;
        a.groove=clamp(a.groove-loss,0,ANDRUM.grooveMax);
        syncAndrumStage(f,true);
        spawnFloatingText(f.x,f.y-f.r-50,"그루브 -"+Math.round(loss),"#fca5a5");
      }
      a.lastDamageTaken=taken;

      if(!a.whiplash){
        const beforeStage=a.stage;
        a.groove=clamp(a.groove+ANDRUM.grooveGainPerSecond*dt,0,ANDRUM.grooveMax);
        syncAndrumStage(f,beforeStage!==andrumStageFromGroove(a.groove));
      }

      updateAndrumDrums(f,dt);
    }'''
)

rep(
'''      if(f.andrum){const a=f.andrum,remain=a.whiplash?(ANDRUM.whiplashSteps-a.whiplashStep)*(15/ANDRUM.bpm):0;return {ratio:a.whiplash?clamp(a.whiplashStep/ANDRUM.whiplashSteps,0,1):clamp(a.groove/ANDRUM.grooveRise,0,1),className:a.whiplash?"rage-fill":"skill-fill",
        text:a.whiplash?"WHIPLASH 솔로 · "+remain.toFixed(1)+"초":a.whiplashReady?"WHIPLASH 준비 · 다음 마디에서 시작":andrumStageName(a.stage)+" · 다음 그루브 "+Math.max(0,ANDRUM.grooveRise-a.groove).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">킥 공격 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · 고정 ${ANDRUM.bpm}BPM · ${a.whiplashReady?"다음 마디 WHIPLASH":"WHIPLASH까지 "+a.whiplashCd.toFixed(1)+"초"}</div>`};}''',
'''      if(f.andrum){const a=f.andrum,remain=a.whiplash?(ANDRUM.whiplashSteps-a.whiplashStep)*(15/ANDRUM.bpm):0;return {
        ratio:clamp(a.groove/ANDRUM.grooveMax,0,1),className:"skill-fill",
        text:a.whiplash?"WHIPLASH 솔로 · "+remain.toFixed(1)+"초":andrumStageName(a.stage)+" · 그루브 "+Math.round(a.groove)+"/"+ANDRUM.grooveMax,
        extraBarsHtml:`<div class="bar" title="WHIPLASH 솔로 게이지"><div class="bar-fill rage-fill" style="width:${clamp(a.soloGauge/ANDRUM.soloMax,0,1)*100}%"></div></div>`,
        extraTextHtml:`<div class="status-skill-label">그루브: 0~100 기본 / 101~200 몰입 / 201~300 광란 · 피격 피해×${ANDRUM.grooveDamageLossMultiplier} 감소</div><div class="status-skill-label">WHIPLASH ${Math.round(a.soloGauge)}/${ANDRUM.soloMax} · 적중 킥 +${ANDRUM.soloGainOnHit} · ${a.whiplashReady?"다음 마디 시작":"게이지 충전 중"}</div>`};}'''
)

rep(
'''      if(c.id==="andrum")return {damage:"킥 음파 5/6/7 · 반경110/135/160 · WHIPLASH 킥3(현재 그루브와 같은 반경) · 피날레 크래시16/반경210",
        tick:"140BPM 고정 · 모든 공격은 실제 킥과 동시 · 4마디마다 뒤 2박 16비트 탐 필인 · 그루브 유지8초마다 단계 상승 · 피격 시 단계 유지·진행도50% 감소 · WHIPLASH 쿨16초 후 다음 마디에서 2마디 솔로",
        tip:"평상시 공격 범위는 테두리만 깜빡이는 원이 아니라 앤드럼에게 계속 붙어 있는 옅은 반투명 원형 공격장으로 보이며, 킥 순간에만 자연스럽게 밝아진다. 필인과 WHIPLASH의 킥도 현재 그루브 단계의 반경110/135/160을 그대로 사용하므로 같은 단계에서는 원 크기가 달라지지 않는다. 피날레 크래시만 별도 특수공격으로 반경210이다. 크래시는 피치 글라이드 없이 짧은 금속성 노이즈 층으로 재합성했다."};''',
'''      if(c.id==="andrum")return {damage:"킥 음파 5/6/7 · 반경110/135/160 · WHIPLASH 킥3(현재 그루브와 같은 반경) · 피날레 크래시16/반경210",
        tick:"그루브0~300: 0~100 기본 / 101~200 몰입 / 201~300 광란 · 초당+12.5 · 피격 시 실제 피해×3 감소 · 솔로게이지0~100 · 실제 적중 킥마다+5 · 100에서 다음 마디 WHIPLASH",
        tip:"그루브는 더 이상 단계별 별도 진행도가 아니라 하나의 0~300 수치다. 피해7을 받으면 21, 피해10을 받으면 30이 즉시 빠지며 경계값 아래로 내려가면 그루브 단계도 곧바로 하락한다. 별도 WHIPLASH 게이지는 일반 킥이 적에게 실제 피해를 준 경우에만 5씩 오르고 솔로 중에는 충전되지 않는다. 100이 되면 다음 마디 첫 박에서 2마디 솔로를 시작하고 게이지를 0으로 소모한다."};'''
)

rep(
'''      const patchNotes = [
      "v90: 앤드럼 공격장/크래시 사운드 정리.''',
'''      const patchNotes = [
      "v91: 앤드럼 그루브/솔로 게이지 재설계. 그루브를 단계별 시간 진행도에서 0~300 단일 수치로 변경: 0~100 기본, 101~200 몰입, 201~300 광란. 평상시 초당12.5 증가해 무피격 시 기존처럼 약8초마다 다음 구간에 진입. 실제 피해를 받으면 피해량×3만큼 그루브가 감소해 임계값 아래로 내려갈 경우 단계도 즉시 하락(예: 피해7→-21). 별도 WHIPLASH 게이지0~100을 추가하고 일반 킥이 적에게 실제 피해를 준 공격 1회당+5, 100에서 준비 상태가 되어 다음 마디 1박에 솔로 시작 후0으로 소모. 기존 16초 자동 솔로 쿨타임 제거. 상태창에 그루브 게이지와 WHIPLASH 게이지를 각각 표시. 공격/반경·리듬·필인·사운드는 v90 유지.",
      "v90: 앤드럼 공격장/크래시 사운드 정리.'''
)

p.write_text(t,encoding="utf-8")
