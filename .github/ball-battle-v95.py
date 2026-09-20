from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:260]!r}")
    t=t.replace(old,new,count)

def between(start,end,new):
    global t
    a=t.find(start)
    b=t.find(end,a)
    if a<0 or b<0:
        raise SystemExit(f"markers not found: {start!r} -> {end!r}")
    t=t[:a]+new+t[b:]

rep('<title>볼배틀 리뉴얼 v94</title>','<title>볼배틀 리뉴얼 v95</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v94</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v95</h1>')

# 쟈바미: 큰 텍스트 배지 삭제.
between(
'''    function drawJabamiDebtChanceBadge(f){''',
'''    function drawJabamiCharacter(f) {''',
''''''
)
rep(
'''      drawHealthBar(f); drawName(f); drawJabamiDebtChanceBadge(f);''',
'''      drawHealthBar(f); drawName(f);'''
)

# 쟈바미: 체력바 바로 아래 작은 빨간 다이아몬드 = 남은 빚쟁이 진입 횟수.
rep(
'''      ctx.strokeStyle = "rgba(255,255,255,.56)";
      ctx.lineWidth = 1;
      roundRect(ctx, x, y, w, h, 4, false, true);

      const visibleShieldMax = f.baseId === "wind_rio" ? (f.rioWindShieldMax || 0) : f.shieldMax;''',
'''      ctx.strokeStyle = "rgba(255,255,255,.56)";
      ctx.lineWidth = 1;
      roundRect(ctx, x, y, w, h, 4, false, true);

      if (f.jabami) {
        const chances=Math.max(0,Math.floor(f.jabami.debtChances||0));
        if(chances>0){
          const size=5,gap=5,total=chances*size+Math.max(0,chances-1)*gap;
          const start=f.x-total/2+size/2;
          const dy=y+h+8;
          ctx.save();
          for(let i=0;i<chances;i++){
            ctx.save();
            ctx.translate(start+i*(size+gap),dy);
            ctx.rotate(Math.PI/4);
            ctx.fillStyle="#ef4444";
            ctx.strokeStyle="#fecaca";
            ctx.lineWidth=.8;
            ctx.fillRect(-size/2,-size/2,size,size);
            ctx.strokeRect(-size/2,-size/2,size,size);
            ctx.restore();
          }
          ctx.restore();
        }
      }

      const visibleShieldMax = f.baseId === "wind_rio" ? (f.rioWindShieldMax || 0) : f.shieldMax;'''
)

# 정의의 아군: 분석 화면에서 소환수 기록을 별도 항목이 아니라 본체 피해/처치에 합산.
between(
'''    function showBattleAnalysis() {''',
'''    function checkEnd() {''',
'''    function showBattleAnalysis() {
      if (fastSimMode) return;
      const modal = $("analysisModal");
      const body = $("analysisModalBody");
      if (!modal || !body || !fighters.length) return;
      const rows = fighters
        .filter(f => !f.isSummon)
        .sort((a, b) => {
          const sa=a.baseId==="justice_ally"?justiceSummonBattleStats(a):{damage:0,kills:0};
          const sb=b.baseId==="justice_ally"?justiceSummonBattleStats(b):{damage:0,kills:0};
          return ((b.damageDealt||0)+sb.damage)-((a.damageDealt||0)+sa.damage);
        });

      const combined=new Map(rows.map(f=>{
        const summon=f.baseId==="justice_ally"?justiceSummonBattleStats(f):{damage:0,kills:0};
        return [f.id,{
          damage:(f.damageDealt||0)+summon.damage,
          kills:(f.kills||0)+summon.kills
        }];
      }));
      const maxDamage=Math.max(1,...rows.map(f=>combined.get(f.id).damage));
      const maxKills=Math.max(1,...rows.map(f=>combined.get(f.id).kills));

      body.innerHTML = rows.map(f => {
        const total=combined.get(f.id);
        const dealt=Math.round(total.damage);
        const taken=Math.round(f.damageTaken||0);
        const kills=total.kills;
        return `
          <div class="analysis-row">
            <div class="analysis-face" style="background:${f.color}">${escapeHtml(f.mark)}</div>
            <div>
              <div class="analysis-name">${escapeHtml(f.name)}</div>
              <div class="analysis-stat"><span>피해</span><div class="analysis-bar"><span style="width:${clamp(dealt / maxDamage * 100, 0, 100)}%"></span></div><span>${dealt}</span></div>
              <div class="analysis-stat"><span>처치</span><div class="analysis-bar"><span style="width:${clamp(kills / maxKills * 100, 0, 100)}%"></span></div><span>${kills}</span></div>
              <div class="analysis-stat"><span>피격</span><div class="analysis-bar"><span style="width:${clamp(taken / Math.max(1, f.maxHp) * 100, 0, 100)}%"></span></div><span>${taken}</span></div>
            </div>
          </div>`;
      }).join("");
      modal.classList.add("show");
    }

'''
)

# 오벨리스크: 대사만 오래 남기지 않고, 실제 정지 시간을 3.4초로 늘리고 말풍선도 그 시간에만 노출.
rep(
'''      triggerHitStop(1.25);screenShake=Math.max(screenShake,1.8);playSound("explosion",1.5);
      d.speech="몬스터가 아니다, 신이다! 나와라 오벨리스크의 거신병!";d.speechTime=5.8;''',
'''      triggerHitStop(3.4);screenShake=Math.max(screenShake,1.8);playSound("explosion",1.5);
      d.speech="몬스터가 아니다, 신이다! 나와라 오벨리스크의 거신병!";
      d.speechTime=0;
      d.obeliskSpeechUntil=performance.now()+3400;'''
)

rep(
'''      if(!f.portraitOnly&&d?.speechTime>0&&d.speech){
        const lines=d.speech.includes("오벨리스크")?["몬스터가 아니다, 신이다!","나와라 오벨리스크의 거신병!"]:[d.speech];''',
'''      if(!f.portraitOnly&&d?.obeliskSpeechUntil>performance.now()&&d.speech){
        const lines=["몬스터가 아니다, 신이다!","나와라 오벨리스크의 거신병!"];'''
)

# 초기값/리셋에서도 오벨리스크 대사 타이머 정리.
rep(
'''      f.duelist = { timer: 6, equipped: false, hand: [], deck: makeJusticeDeck(), drawCd: 0, playCd: 0, speech: "", speechTime: 0, blueSummoned: 0, fusionDone: false, fusion: null, emptyTimer: 0, obeliskUsed:false, godCinematic:null, summonDamageDealt:0, summonKills:0 };''',
'''      f.duelist = { timer: 6, equipped: false, hand: [], deck: makeJusticeDeck(), drawCd: 0, playCd: 0, speech: "", speechTime: 0, obeliskSpeechUntil:0, blueSummoned: 0, fusionDone: false, fusion: null, emptyTimer: 0, obeliskUsed:false, godCinematic:null, summonDamageDealt:0, summonKills:0 };'''
)
rep(
'''d.obeliskUsed=false;d.godCinematic=null;d.justUsed=false;''',
'''d.obeliskUsed=false;d.godCinematic=null;d.obeliskSpeechUntil=0;d.justUsed=false;'''
)

# 패치노트
rep(
'''      const patchNotes = [
      "v94: 쟈바미 공동승리·빚 기회 UI 및 정의의 아군 분석 개선.''',
'''      const patchNotes = [
      "v95: v94 UI/연출 수정. 쟈바미의 큰 '빚 기회' 텍스트 배지를 완전히 제거하고 체력바 바로 아래에 남은 빚쟁이 진입 횟수만큼 작은 빨간 다이아몬드를 표시. 빚쟁이 진입 시 기회를 1회 소비하므로 다이아몬드도 즉시 하나 사라지고, 조커로 기회를 추가 획득하면 그 수만큼 다이아몬드가 늘어남. 정의의 아군 전투분석에서 '소환수 피해/처치' 별도 줄을 제거하고 백룡·융합체·오벨리스크의 누적 피해와 처치를 정의의 아군 본체의 피해/처치 값에 합산. 오벨리스크 소환 연출은 대사만 5.8초 남기던 방식을 폐기하고 실제 시간정지를 1.25→3.4초로 연장, 전용 대사 말풍선도 같은 3.4초 실시간 동안만 표시되어 정지 종료와 함께 사라지도록 변경. v94의 쟈바미 공동승리 빚 처리 규칙은 유지.",
      "v94: 쟈바미 공동승리·빚 기회 UI 및 정의의 아군 분석 개선.'''
)

p.write_text(t,encoding="utf-8")
