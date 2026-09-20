from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:180]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v84</title>','<title>볼배틀 리뉴얼 v85</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v84</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v85</h1>')

rep(
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 근접 범위 자동 광역베기 · 기동 적중 시 즉시 재와이어", desc:"0.45초 준비 후 1초간 초당650으로 고속이동. 몸이 직접 닿지 않아도 몸 충돌 거리보다 8만큼 넓은 검 사거리 안에 적이 들어오면 회전베기가 발동하고, 한 명을 계기로 발동한 베기는 베기 원 안의 모든 적에게 광역 피해와 출혈을 준다. 와이어 기동 중에는 강습16 피해가 적용된다. 출혈은 1피해씩 5회이며, 출혈 중인 상대를 다시 베면 남은 출혈 피해를 즉시 터뜨린 뒤 새 출혈을 건다. 기동 공격에 성공하면 즉시 다음 와이어 준비를 시작한다." },''',
'''        skillName:"입체기동 · 회전베기", condition:"7초마다 벽 2곳에 와이어 · 근접 범위 자동 광역베기 · 와이어 최대 3연속", desc:"0.45초 준비 후 1초간 초당650으로 고속이동. 몸이 직접 닿지 않아도 몸 충돌 거리보다 8만큼 넓은 검 사거리 안에 적이 들어오면 회전베기가 발동하고, 한 명을 계기로 발동한 베기는 베기 원 안의 모든 적에게 광역 피해와 출혈을 준다. 와이어 기동 중에는 강습16 피해가 적용된다. 출혈은 1피해씩 5회이며, 출혈 중인 상대를 다시 베면 남은 출혈 피해를 즉시 터뜨린 뒤 새 출혈을 건다. 와이어 강습이 적중하면 즉시 다음 와이어를 준비하지만 한 사이클 최대 3번까지만 연속 강습하며, 3번째 적중 후에는 정상 7초 쿨타임으로 돌아간다." },'''
)

rep(
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:650,
      contactCooldown:1.2, spinDuration:.45, triggerBonus:8, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:1, bleedTicks:5, bleedDuration:5, gapForCap:200, maxBonus:.6 };''',
'''    const NEWHELLO = { period:7, windup:.45, dashDuration:1, dashSpeed:650,
      contactCooldown:1.2, spinDuration:.45, triggerBonus:8, radiusBonus:28, normalDamage:8,
      dashDamage:16, bleedDamage:1, bleedTicks:5, bleedDuration:5, maxChain:3, gapForCap:200, maxBonus:.6 };'''
)

rep(
'''      f.newhello={cd:NEWHELLO.period, windup:0, dash:0, spin:0, spinFast:false,
        contactCd:0, anchors:[], angle:0, hits:new Set(), trail:[], mutualContactUntil:0};''',
'''      f.newhello={cd:NEWHELLO.period, windup:0, dash:0, spin:0, spinFast:false,
        contactCd:0, anchors:[], angle:0, hits:new Set(), trail:[], mutualContactUntil:0, chainHits:0};'''
)

rep(
'''        if(landed){
          n.mutualContactUntil=battleTime+.08;
          n.dash=0;
          n.anchors=[];
          n.cd=0;
          spawnFloatingText(f.x,f.y-f.r-48,"연속 와이어!","#cffafe");
        }''',
'''        if(landed){
          n.mutualContactUntil=battleTime+.08;
          n.chainHits=(n.chainHits||0)+1;
          n.dash=0;
          n.anchors=[];
          if(n.chainHits<NEWHELLO.maxChain){
            n.cd=0;
            spawnFloatingText(f.x,f.y-f.r-48,`연속 와이어 ${n.chainHits+1}/${NEWHELLO.maxChain}!`,"#cffafe");
          }else{
            n.cd=NEWHELLO.period;
            n.chainHits=0;
            spawnFloatingText(f.x,f.y-f.r-48,"연속 강습 종료","#bae6fd");
          }
        }'''
)

rep(
'''      if(newhelloBlocked(f) && (n.dash>0 || n.windup>0)){
        n.dash=0;n.windup=0;n.anchors=[];n.cd=NEWHELLO.period;
      }''',
'''      if(newhelloBlocked(f) && (n.dash>0 || n.windup>0)){
        n.dash=0;n.windup=0;n.anchors=[];n.cd=NEWHELLO.period;n.chainHits=0;
      }'''
)

rep(
'''      if(n.dash<=0){n.anchors=[];const speed=f.baseSpeed*44;const a=Math.atan2(f.vy,f.vx);f.vx=Math.cos(a)*speed;f.vy=Math.sin(a)*speed;}
      return true;''',
'''      if(n.dash<=0){
        n.anchors=[];
        if(n.cd>0)n.chainHits=0;
        const speed=f.baseSpeed*44;const a=Math.atan2(f.vy,f.vx);f.vx=Math.cos(a)*speed;f.vy=Math.sin(a)*speed;
      }
      return true;'''
)

rep(
'''      if(c.id==="newhello_sergeant")return {damage:"일반 광역 회전베기8 / 와이어 광역 강습16 + 출혈1×5회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",
        tick:"검 발동 사거리: 몸 충돌보다 +8 · 광역 베기 범위: 몸 반경보다 +28 · 기동7초 · 준비0.45초 · 고속이동1초(초당650) · 기동 적중 시 즉시 다음 와이어 준비 · 일반 베기 재사용1.2초 · 출혈 약1초마다 5회",
        tip:"뉴헬로는 상대와 몸이 닿지 않아도 검 사거리(+8)에 들어오면 베기가 발동한다. 공격을 발동시킨 상대가 누구든, 그 순간 병장 중심의 더 큰 베기 원(+28) 안에 있는 모든 적이 같은 베기 피해와 출혈을 받는다. 출혈은 1씩 5회이며, 병장이 건 출혈이 남아 있는 적을 다시 베면 남은 출혈 틱 피해를 즉시 한 번에 터뜨리고 새 5틱 출혈을 건다. 실제 몸 충돌 시 상대의 기존 접촉 반격은 정상 발동한다."};''',
'''      if(c.id==="newhello_sergeant")return {damage:"일반 광역 회전베기8 / 와이어 광역 강습16 + 출혈1×5회 · 재타격 시 남은 출혈 즉시 폭발 후 재적용 · HP 열세 보정 최대 ×1.6",
        tick:"검 발동 사거리: 몸 충돌보다 +8 · 광역 베기 범위: 몸 반경보다 +28 · 기동7초 · 준비0.45초 · 고속이동1초(초당650) · 와이어 강습 최대 3연속 · 일반 베기 재사용1.2초 · 출혈 약1초마다 5회",
        tip:"뉴헬로는 상대와 몸이 닿지 않아도 검 사거리(+8)에 들어오면 베기가 발동한다. 공격을 발동시킨 상대가 누구든, 그 순간 병장 중심의 더 큰 베기 원(+28) 안에 있는 모든 적이 같은 베기 피해와 출혈을 받는다. 와이어 강습 적중 시 즉시 재와이어하지만 한 사이클에서 총 3번까지만 연속 강습할 수 있고, 3번째 적중 뒤에는 7초 쿨타임이 적용된다. 중간 강습이 빗나가거나 끊기면 연속 횟수는 초기화된다. 출혈 폭발과 실제 몸 충돌 시 상대 접촉 반격은 기존대로 유지된다."};'''
)

rep(
'''        extraTextHtml:'<div class="status-skill-label">검 사거리 +8 · 광역범위 +28 · 일반8 / 와이어16 + 출혈1×5 · 적중 시 즉시 재와이어</div>'};}''',
'''        extraTextHtml:'<div class="status-skill-label">검 사거리 +8 · 광역범위 +28 · 일반8 / 와이어16 + 출혈1×5 · 와이어 최대 3연속</div>'};}'''
)

rep(
'''      const patchNotes = [
      "v84: 뉴헬로 병장 체력 170→160으로 10 하향.''',
'''      const patchNotes = [
      "v85: 뉴헬로 병장 연속 와이어 상한 추가. 와이어 강습 적중 시 즉시 재와이어하는 규칙은 유지하되 한 사이클 총 3연속까지만 허용하고, 3번째 강습 적중 뒤에는 정상 7초 쿨타임으로 복귀. 중간 강습이 빗나가거나 끊기면 연속 횟수 초기화. HP160·비접촉 +8·광역 +28·일반8/와이어16·출혈1×5 및 잔여 출혈 폭발·속도650은 유지.",
      "v84: 뉴헬로 병장 체력 170→160으로 10 하향.'''
)

p.write_text(t,encoding="utf-8")
