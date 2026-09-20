from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:200]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v86</title>','<title>볼배틀 리뉴얼 v87</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v86</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v87</h1>')

rep(
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 100,
        skillName: "템포 · Caravan", condition: "연주 8초 유지마다 템포 상승 · 피격 시 1단계 하락 · 20초마다 Caravan", desc: "주변 적에게 드럼 음파를 반복해서 퍼뜨린다. 연주를 끊기지 않고 이어갈수록 기본→업템포→광란으로 빨라지고 강해지며, 피해를 받으면 템포가 한 단계 떨어진다. 20초마다 4초간 Caravan 솔로에 돌입해 빠른 광역 비트를 연속으로 울리고 마지막 심벌 크래시로 마무리한다." },''',
'''      { id: "andrum", name: "앤드럼", mark: "🥁", role: "영화", color: "#d6a85f", hp: 150, attack: 0, speed: 2.7, range: 210,
        skillName: "템포 · Caravan", condition: "연주 8초 유지마다 템포 상승 · 피격 시 상승 진행도 절반 · 16초마다 Caravan", desc: "주변 적에게 드럼 음파를 반복해서 퍼뜨린다. 연주를 이어갈수록 기본→업템포→광란으로 빨라지고 범위가 넓어진다. 피해를 받아도 단계는 내려가지 않고 다음 템포까지의 진행도만 절반으로 줄어든다. 16초마다 4초간 Caravan 솔로에 돌입해 넓은 광역 비트를 연속으로 울리고 마지막 대형 심벌 크래시로 마무리한다. 실제 드럼 패턴은 하이햇 8비트, 2·4박 스네어, 1·3박 킥으로 연주한다." },'''
)

rep(
'''    function noise(duration = 0.14, volume = 0.06, startOffset = 0, filterFreq = 900, filterType = "lowpass") {
      if (!audioCtx) return;
      const now = audioCtx.currentTime + startOffset;
      const size = Math.max(1, Math.floor(audioCtx.sampleRate * duration));
      const buffer = audioCtx.createBuffer(1, size, audioCtx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < size; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / size);
      const src = audioCtx.createBufferSource();
      const filter = audioCtx.createBiquadFilter();
      const gain = audioCtx.createGain();
      filter.type = filterType;
      filter.frequency.setValueAtTime(filterFreq, now);
      gain.gain.setValueAtTime(volume * masterVolume, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
      src.buffer = buffer;
      src.connect(filter);
      filter.connect(gain);
      gain.connect(audioCtx.destination);
      src.start(now);
      src.stop(now + duration + 0.025);
    }

    function playSound(name, strength = 1) {''',
'''    function noise(duration = 0.14, volume = 0.06, startOffset = 0, filterFreq = 900, filterType = "lowpass") {
      if (!audioCtx) return;
      const now = audioCtx.currentTime + startOffset;
      const size = Math.max(1, Math.floor(audioCtx.sampleRate * duration));
      const buffer = audioCtx.createBuffer(1, size, audioCtx.sampleRate);
      const data = buffer.getChannelData(0);
      for (let i = 0; i < size; i++) data[i] = (Math.random() * 2 - 1) * (1 - i / size);
      const src = audioCtx.createBufferSource();
      const filter = audioCtx.createBiquadFilter();
      const gain = audioCtx.createGain();
      filter.type = filterType;
      filter.frequency.setValueAtTime(filterFreq, now);
      gain.gain.setValueAtTime(volume * masterVolume, now);
      gain.gain.exponentialRampToValueAtTime(0.0001, now + duration);
      src.buffer = buffer;
      src.connect(filter);
      filter.connect(gain);
      gain.connect(audioCtx.destination);
      src.start(now);
      src.stop(now + duration + 0.025);
    }

    // 앤드럼 전용 드럼 합성. 기존 magic 효과음을 쓰지 않고 킥/스네어/하이햇을 분리한다.
    function playAndrumKick(strength = 1) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const s=Math.max(.5,Math.min(1.5,strength));
      tone(145,.16,"sine",.15*s,0,48);
      tone(62,.20,"sine",.085*s,.01,38);
      noise(.035,.022*s,0,900,"lowpass");
    }
    function playAndrumSnare(strength = 1) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const s=Math.max(.5,Math.min(1.5,strength));
      noise(.15,.12*s,0,2400,"bandpass");
      noise(.075,.055*s,0,6500,"highpass");
      tone(185,.11,"triangle",.055*s,0,125);
    }
    function playAndrumHiHat(accent = false) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      noise(accent?.065:.045,accent?.040:.026,0,7200,"highpass");
      noise(.025,accent?.018:.012,0,10500,"bandpass");
    }
    function playAndrumCrash() {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      noise(.75,.13,0,5200,"highpass");
      noise(.55,.07,.01,8500,"bandpass");
      tone(310,.32,"triangle",.035,0,210);
    }

    function playSound(name, strength = 1) {'''
)

rep(
'''    const ANDRUM = {
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
    };''',
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
    };'''
)

rep(
'''        caravanCd: ANDRUM.caravanPeriod,
        caravan: 0,
        caravanBeat: 0,
        lastDamageTaken: f.damageTaken || 0''',
'''        caravanCd: ANDRUM.caravanPeriod,
        caravan: 0,
        caravanBeat: 0,
        drumStep: 0,
        drumClock: 0,
        lastDamageTaken: f.damageTaken || 0'''
)

rep(
'''    function andrumWave(f, power, radius, label, color = "#fbbf24") {
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

    function updateAndrum(f, dt) {''',
'''    function andrumWave(f, power, radius, label, color = "#fbbf24") {
      const victims = enemiesOf(f).filter(e => Math.hypot(e.x-f.x,e.y-f.y) <= radius + e.r);
      victims.forEach(e => {
        damage(e, power, f, label);
        spawnHitFlash(e.x, e.y, color, 20);
      });
      spawnBlast(f.x, f.y, radius, color);
      spawnParticles(f.x, f.y, color, 8);
      if (f.andrum) {
        f.andrum.pulse = .20;
        f.andrum.pulseRadius = radius;
      }
      return victims.length;
    }

    function updateAndrumDrums(f, dt) {
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
    }

    function updateAndrum(f, dt) {'''
)

rep(
'''      a.pulse = Math.max(0, a.pulse - dt);

      const taken = f.damageTaken || 0;
      if (taken > a.lastDamageTaken + .001) {
        if (a.stage > 0) {
          a.stage -= 1;
          spawnFloatingText(f.x, f.y-f.r-36, "템포 흔들림", "#fca5a5");
        }
        a.tempo = 0;
      }
      a.lastDamageTaken = taken;''',
'''      a.pulse = Math.max(0, a.pulse - dt);
      updateAndrumDrums(f,dt);

      const taken = f.damageTaken || 0;
      if (taken > a.lastDamageTaken + .001) {
        a.tempo *= .5;
        spawnFloatingText(f.x, f.y-f.r-36, "템포 진행 -50%", "#fca5a5");
      }
      a.lastDamageTaken = taken;'''
)

rep(
'''        if (before > 0 && a.caravan <= 0) {
          andrumWave(f, ANDRUM.crashDamage, ANDRUM.crashRadius, "Caravan 심벌 크래시", "#f59e0b");
          spawnFloatingText(f.x, f.y-f.r-46, "CRASH!", "#fef3c7");''',
'''        if (before > 0 && a.caravan <= 0) {
          andrumWave(f, ANDRUM.crashDamage, ANDRUM.crashRadius, "Caravan 심벌 크래시", "#f59e0b");
          playAndrumCrash();
          spawnFloatingText(f.x, f.y-f.r-46, "CRASH!", "#fef3c7");'''
)

rep(
'''      if(c.id==="andrum")return {damage:"드럼 비트 5/6/7 · 반경58/66/74 · Caravan 연타3(0.45초마다) · 마지막 심벌 크래시16/반경100",
        tick:"연주 유지8초마다 기본→업템포→광란 · 비트 간격1.20/0.90/0.68초 · 피격 시 템포 1단계 하락 · Caravan 20초마다 4초",
        tip:"직접 접촉 공격 없이 자기 주변에 원형 음파를 반복한다. 피해를 받으면 현재 템포가 한 단계 떨어지고 상승 진행도도 초기화된다. Caravan 동안 일반 비트 대신 0.45초마다 광역3 피해를 주며 종료 순간 반경100 심벌 크래시16으로 마무리한다."};''',
'''      if(c.id==="andrum")return {damage:"드럼 비트 5/6/7 · 반경110/135/160 · Caravan 연타3(0.45초마다, 반경170) · 마지막 심벌 크래시16/반경210",
        tick:"연주 유지8초마다 기본→업템포→광란 · 비트 간격1.20/0.90/0.68초 · 피격 시 단계 유지·상승 진행도 50% 감소 · Caravan 16초마다 4초 · 드럼 110/145/180BPM(솔로220)",
        tip:"직접 접촉 공격 없이 넓은 원형 음파를 반복한다. 피해를 받아도 템포 단계는 내려가지 않고 다음 단계 진행도만 절반으로 줄어든다. 실제 드럼 사운드는 하이햇 8비트, 2·4박 스네어, 1·3박 킥 패턴이며 템포 단계가 오를수록 BPM도 빨라진다. Caravan 종료 순간 반경210 심벌 크래시16으로 마무리한다."};'''
)

rep(
'''      if(f.andrum){const a=f.andrum;return {ratio:a.caravan>0?clamp(a.caravan/ANDRUM.caravanDuration,0,1):clamp(a.tempo/ANDRUM.tempoRise,0,1),className:a.caravan>0?"rage-fill":"skill-fill",
        text:a.caravan>0?"Caravan 솔로 "+a.caravan.toFixed(1)+"초":andrumStageName(a.stage)+" · 다음 템포 "+Math.max(0,ANDRUM.tempoRise-a.tempo).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">비트 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · Caravan까지 ${a.caravanCd.toFixed(1)}초</div>`};}''',
'''      if(f.andrum){const a=f.andrum;return {ratio:a.caravan>0?clamp(a.caravan/ANDRUM.caravanDuration,0,1):clamp(a.tempo/ANDRUM.tempoRise,0,1),className:a.caravan>0?"rage-fill":"skill-fill",
        text:a.caravan>0?"Caravan 솔로 "+a.caravan.toFixed(1)+"초":andrumStageName(a.stage)+" · 다음 템포 "+Math.max(0,ANDRUM.tempoRise-a.tempo).toFixed(1)+"초",
        extraTextHtml:`<div class="status-skill-label">비트 ${ANDRUM.damages[a.stage]} / 반경 ${ANDRUM.radii[a.stage]} · ${a.caravan>0?ANDRUM.caravanBpm:ANDRUM.bpms[a.stage]}BPM · Caravan까지 ${a.caravanCd.toFixed(1)}초</div>`};}'''
)

rep(
'''      const patchNotes = [
      "v86: 영화 캐릭터 앤드럼 추가.''',
'''      const patchNotes = [
      "v87: 앤드럼 대규모 상향 및 드럼 사운드 교체. 기본/업템포/광란 음파 반경58/66/74→110/135/160, 피해5/6/7은 유지. 피격 시 단계 하락·진행도 초기화 대신 단계 유지 및 다음 템포 진행도 50% 감소. Caravan 주기20→16초, 연타 반경82→170, 마지막 크래시 반경100→210(피해3연타·크래시16 유지). 기존 뾱뾱 magic 효과음을 제거하고 WebAudio 킥·스네어·하이햇 합성으로 교체. 하이햇 8비트, 2·4박 스네어, 1·3박 킥 패턴을 기본110/업145/광란180BPM, Caravan220BPM으로 연주.",
      "v86: 영화 캐릭터 앤드럼 추가.'''
)

p.write_text(t,encoding="utf-8")
