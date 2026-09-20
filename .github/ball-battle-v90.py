from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:220]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v89</title>','<title>볼배틀 리뉴얼 v90</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v89</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v90</h1>')

rep(
'''    function playAndrumCrash(strength = 1) {
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
    }''',
'''    function playAndrumCrash(strength = 1) {
      if (!soundEnabled || fastSimMode) return;
      ensureAudio();
      const s=Math.max(.55,Math.min(1.5,strength));
      // 피치가 내려가는 '삐유웅'과 긴 바람 꼬리를 없애고 짧고 거친 금속성 어택/잔향만 사용한다.
      noise(.050,.125*s,0,2300,"bandpass");
      noise(.62,.090*s,.002,4300,"bandpass");
      noise(.48,.068*s,.008,6800,"bandpass");
      noise(.34,.050*s,.016,9800,"highpass");
      noise(.20,.028*s,.026,12500,"highpass");
    }'''
)

rep(
'''      whiplashSteps: 32,
      whiplashDamage: 3,
      whiplashRadius: 170,
      crashDamage: 16,''',
'''      whiplashSteps: 32,
      whiplashDamage: 3,
      crashDamage: 16,'''
)

rep(
'''        f.andrum.pulse = .11;
        f.andrum.pulseRadius = radius;
        f.andrum.pulseColor = color;''',
'''        f.andrum.pulse = .26;
        f.andrum.pulseRadius = radius;
        f.andrum.pulseColor = color;'''
)

rep(
'''      if(whiplash)andrumWave(f,ANDRUM.whiplashDamage,ANDRUM.whiplashRadius,"WHIPLASH 킥","#fde68a");
      else andrumWave(f,ANDRUM.damages[a.stage],ANDRUM.radii[a.stage],"킥 음파",a.stage===2?"#fb923c":"#fbbf24");''',
'''      const radius=ANDRUM.radii[a.stage];
      if(whiplash)andrumWave(f,ANDRUM.whiplashDamage,radius,"WHIPLASH 킥","#fde68a");
      else andrumWave(f,ANDRUM.damages[a.stage],radius,"킥 음파",a.stage===2?"#fb923c":"#fbbf24");'''
)

rep(
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
      }''',
'''      const a = f.andrum || {stage:0,pulse:0,whiplash:false,pulseColor:"#fbbf24"};
      if (!f.portraitOnly) {
        const normalRadius=ANDRUM.radii[a.stage]||ANDRUM.radii[0];
        const visualRadius=a.pulse>0?(a.pulseRadius||normalRadius):normalRadius;
        const hit=clamp(a.pulse/.26,0,1);
        const rgb=a.whiplash?"253,230,138":a.stage>=2?"251,146,60":"251,191,36";
        ctx.save();
        // 항상 앤드럼에게 붙어 있는 반투명 '공격장'. 킥 순간에는 잠깐 밝아질 뿐 사라졌다 생기지 않는다.
        const grad=ctx.createRadialGradient(f.x,f.y,Math.max(12,f.r*1.15),f.x,f.y,visualRadius);
        grad.addColorStop(0,`rgba(${rgb},${0.055+hit*.105})`);
        grad.addColorStop(.72,`rgba(${rgb},${0.035+hit*.075})`);
        grad.addColorStop(1,`rgba(${rgb},${0.012+hit*.035})`);
        ctx.fillStyle=grad;
        ctx.beginPath();
        ctx.arc(f.x,f.y,visualRadius,0,Math.PI*2);
        ctx.fill();
        ctx.strokeStyle=`rgba(${rgb},${0.16+hit*.40})`;
        ctx.lineWidth=2.5+hit*1.5;
        ctx.stroke();
        ctx.restore();
      }'''
)

rep(
'''      if(c.id==="andrum")return {damage:"킥 음파 5/6/7 · 반경110/135/160 · WHIPLASH 킥3/반경170 · 피날레 크래시16/반경210",
        tick:"140BPM 고정 · 모든 공격은 실제 킥과 동시 · 4마디마다 뒤 2박 16비트 탐 필인 · 그루브 유지8초마다 단계 상승 · 피격 시 단계 유지·진행도50% 감소 · WHIPLASH 쿨16초 후 다음 마디에서 2마디 솔로",
        tip:"공격 원은 킥 순간에만 짧게 나타나는 단일 원이며 항상 앤드럼 현재 위치를 중심으로 따라다닌다. 기본 단계는 8비트 하이햇·2/4 스네어·1/3 킥, 몰입 단계는 오픈 하이햇·고스트 스네어·하이탐 픽업, 광란 단계는 16비트 하이햇·고스트 스네어·탐 악센트가 추가된다. 필인은 하이→미드→플로어 탐으로 명확히 하강하며 다음 마디 크래시로 복귀한다. WHIPLASH는 쿨이 차도 박자를 자르지 않고 다음 마디 1박에서 시작하는 고정 2마디 솔로다."};''',
'''      if(c.id==="andrum")return {damage:"킥 음파 5/6/7 · 반경110/135/160 · WHIPLASH 킥3(현재 그루브와 같은 반경) · 피날레 크래시16/반경210",
        tick:"140BPM 고정 · 모든 공격은 실제 킥과 동시 · 4마디마다 뒤 2박 16비트 탐 필인 · 그루브 유지8초마다 단계 상승 · 피격 시 단계 유지·진행도50% 감소 · WHIPLASH 쿨16초 후 다음 마디에서 2마디 솔로",
        tip:"평상시 공격 범위는 테두리만 깜빡이는 원이 아니라 앤드럼에게 계속 붙어 있는 옅은 반투명 원형 공격장으로 보이며, 킥 순간에만 자연스럽게 밝아진다. 필인과 WHIPLASH의 킥도 현재 그루브 단계의 반경110/135/160을 그대로 사용하므로 같은 단계에서는 원 크기가 달라지지 않는다. 피날레 크래시만 별도 특수공격으로 반경210이다. 크래시는 피치 글라이드 없이 짧은 금속성 노이즈 층으로 재합성했다."};'''
)

rep(
'''      const patchNotes = [
      "v89: 앤드럼 리듬/판정 동기화 개선.''',
'''      const patchNotes = [
      "v90: 앤드럼 공격장/크래시 사운드 정리. 평상시 공격 범위를 킥 때만 0.11초 깜빡이던 테두리 원에서 앤드럼에게 계속 붙어 이동하는 옅은 반투명 채움 원으로 변경하고, 킥 순간에는 0.26초 동안 부드럽게 밝아지도록 수정. WHIPLASH 킥 반경170 고정을 제거해 필인·기본·솔로 킥 모두 현재 그루브 단계 반경110/135/160을 공통 사용하도록 통일(피날레 크래시16/반경210은 유지). 크래시 사운드는 피치가 내려가는 톤과 1초 이상 긴 고역 꼬리를 완전히 제거하고 짧은 어택+0.2~0.62초 금속성 노이즈 레이어만 사용해 '삐유우웅/바람 빠짐' 느낌을 줄임. 피해 수치와 리듬 구조는 v89 유지.",
      "v89: 앤드럼 리듬/판정 동기화 개선.'''
)

p.write_text(t,encoding="utf-8")
