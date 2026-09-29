from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')
if '볼배틀 리뉴얼 v177' not in s:
    raise SystemExit('v177 marker missing; refusing to patch a different base')

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s = s.replace(old, new, 1)

once('볼배틀 리뉴얼 v177', '볼배틀 리뉴얼 v178', 'version')
once('condition:"깨물기 충전 · 전방120° 피냄새 가속 · 10초마다 직선 돌진"',
     'condition:"깨물기 충전 · 전방120° 피냄새 가속 · 중앙60° 타게팅 돌진 · 저체력 흡혈 강화"', 'card condition')
once('기본 이동은 매우 느리지만 상대가 반피 이하가 되면 폭발적으로 빨라진다. 10초마다 현재 피 냄새 속도에 비례해 돌진하며, 중앙60° 안에 적이 있으면 그 적을 타게팅하고 없으면 진행방향 직선으로 돌진한다. 적중 시 0.9초 제압하고 3회 공격해 흡혈한다.',
     '기본 이동은 매우 느리지만 상대가 반피 이하가 되면 폭발적으로 빨라진다. 10초마다 현재 피 냄새 속도에 비례해 돌진하므로 빠를수록 돌진 거리도 길어진다. 중앙60° 안에 적이 있으면 그 적을 타게팅하고 없으면 진행방향 직선으로 돌진하며, 돌진 중에는 모든 넉백을 무시한다. 적중 시 0.9초 제압하고 3회 공격해 흡혈하며 웍웍 자신의 체력이 낮을수록 깨물기와 난타의 회복량이 최대 2배까지 증가한다.', 'card desc')
once('      maulDuration:.9, maulHits:3, maulInterval:.3, maulDamage:7, maulHeal:4\n    };',
     '      maulDuration:.9, maulHits:3, maulInterval:.3, maulDamage:7, maulHeal:4, healMaxMult:2\n    };', 'constants')
once('f.wok={biteCharge:0,nextDashAt:WOK.dashPeriod,dashUntil:0,dashSpeed:0,dashDirX:1,dashDirY:0,dashTargetId:null,bloodMult:1,bloodHp:1,biteFx:0,maul:null,baseSpeed:f.baseSpeed||f.speed||1.6};',
     'f.wok={biteCharge:0,nextDashAt:WOK.dashPeriod,dashUntil:0,dashSpeed:0,dashDirX:1,dashDirY:0,dashTargetId:null,scentTargetId:null,bloodMult:1,bloodHp:1,biteFx:0,maul:null,baseSpeed:f.baseSpeed||f.speed||1.6};', 'init')

old = '''    function wokBiteCooldown(f){
      const q=clamp((f?.hp||0)/Math.max(1,f?.maxHp||1),0,1);
      return WOK.biteCooldownLow+(WOK.biteCooldownHigh-WOK.biteCooldownLow)*q;
    }
    function wokWokBlocked(f){
      return !f?.alive||f.stun>0||f.hardFreeze>0||f.bindStun>0||f.punchHold>0||f.punchFlight>0||f.vampSuppressed>0||f.joltStop>0||isCasting(f);
    }'''
new = '''    function wokBiteCooldown(f){
      const q=clamp((f?.hp||0)/Math.max(1,f?.maxHp||1),0,1);
      return WOK.biteCooldownLow+(WOK.biteCooldownHigh-WOK.biteCooldownLow)*q;
    }
    function wokHealMultiplier(f){
      const q=clamp((f?.hp||0)/Math.max(1,f?.maxHp||1),0,1);
      return 1+(WOK.healMaxMult-1)*(1-q);
    }
    function wokWokBlocked(f){
      const dashing=!!(f?.wok&&battleTime<(f.wok.dashUntil||0));
      return !f?.alive||f.stun>0||f.hardFreeze>0||f.bindStun>0||f.punchHold>0||(!dashing&&f.punchFlight>0)||f.vampSuppressed>0||f.joltStop>0||isCasting(f);
    }'''
once(old, new, 'heal multiplier and block')

once('if(mag<.01){w.bloodMult=1;w.bloodHp=1;return 1;}',
     'if(mag<.01){w.bloodMult=1;w.bloodHp=1;w.scentTargetId=null;return 1;}', 'zero speed scent')
once('let best=1,found=false;', 'let best=1,found=false,bestTarget=null;', 'scent local')
once('if(!found||q<best){best=q;found=true;}', 'if(!found||q<best){best=q;found=true;bestTarget=e;}', 'scent choose')
once('w.bloodHp=found?best:1;', 'w.scentTargetId=bestTarget?.id||null;w.bloodHp=found?best:1;', 'scent store')

once('w.dashUntil=battleTime+WOK.dashDuration;w.nextDashAt=battleTime+WOK.dashPeriod;\n      f.vx=w.dashDirX*w.dashSpeed;f.vy=w.dashDirY*w.dashSpeed;',
     'w.dashUntil=battleTime+WOK.dashDuration;w.nextDashAt=battleTime+WOK.dashPeriod;\n      f.punchFlight=0;f.punchSource=null;f.punchWallPower=0;f.punchWallHits=0;f.queuedIronImpulse=null;f.webKnockTime=0;f.webKnockSourceId="";\n      f.vx=w.dashDirX*w.dashSpeed;f.vy=w.dashDirY*w.dashSpeed;', 'dash start immunity')

old = '''    function moveWokWokDash(f,dt){
      const w=f?.wok;if(!w||battleTime>=(w.dashUntil||0))return false;
      if(wokWokBlocked(f)){w.dashUntil=0;w.dashTargetId=null;wokRestoreCruise(f);return false;}'''
new = '''    function moveWokWokDash(f,dt){
      const w=f?.wok;if(!w||battleTime>=(w.dashUntil||0))return false;
      // 돌진 중에는 외부 넉백/비행 충격을 매 프레임 제거하고 돌진 벡터를 우선한다.
      f.punchFlight=0;f.punchSource=null;f.punchWallPower=0;f.punchWallHits=0;f.queuedIronImpulse=null;f.webKnockTime=0;f.webKnockSourceId="";
      if(wokWokBlocked(f)){w.dashUntil=0;w.dashTargetId=null;wokRestoreCruise(f);return false;}'''
once(old, new, 'dash move immunity')

once('heal(f,WOK.maulHeal);w.biteFx=.22;',
     'heal(f,Math.round(WOK.maulHeal*wokHealMultiplier(f)));w.biteFx=.22;', 'maul heal')
once('w.biteCharge=0;heal(f,WOK.biteHeal);w.biteFx=.34;',
     'w.biteCharge=0;heal(f,Math.round(WOK.biteHeal*wokHealMultiplier(f)));w.biteFx=.34;', 'bite heal')

marker = '''    function drawWokWokCharacter(f){
      const w=f.wok||{};
      ctx.save();'''
replacement = '''    function drawWokBloodScent(f){
      const w=f?.wok;if(!w||fastSimMode||f.portraitOnly||(w.bloodMult||1)<=1.001||!w.scentTargetId)return;
      const target=fighterById(w.scentTargetId);if(!target?.alive||!areEnemies(f,target))return;
      const dx=f.x-target.x,dy=f.y-target.y,d=Math.hypot(dx,dy)||1,px=-dy/d,py=dx/d;
      const strong=(w.bloodHp||1)<=WOK.scentHalfHp,pulse=.5+.5*Math.sin(battleTime*7);
      ctx.save();ctx.beginPath();ctx.rect(arena.x,arena.y,arena.size,arena.size);ctx.clip();
      for(let i=0;i<3;i++){
        const off=(i-1)*(strong?11:8),wave=Math.sin(battleTime*3.2+i*2.1)*(strong?10:6);
        const cx=(target.x+f.x)/2+px*(off+wave),cy=(target.y+f.y)/2+py*(off+wave);
        ctx.globalAlpha=(strong?.40:.22)+i*.04;ctx.strokeStyle=strong?"#ef4444":"#b91c1c";ctx.lineWidth=strong?2.8:1.8;
        ctx.setLineDash(strong?[9,9]:[5,13]);ctx.lineDashOffset=-(battleTime*(strong?90:55)+i*13);
        ctx.beginPath();ctx.moveTo(target.x,target.y);ctx.quadraticCurveTo(cx,cy,f.x,f.y);ctx.stroke();
      }
      ctx.setLineDash([]);ctx.globalAlpha=strong?.62:.28;ctx.strokeStyle=strong?"#fb7185":"#dc2626";ctx.lineWidth=strong?3:2;
      ctx.beginPath();ctx.arc(target.x,target.y,target.r+7+pulse*5,0,Math.PI*2);ctx.stroke();
      if(strong){
        const mag=Math.hypot(f.vx||0,f.vy||0)||1,ux=(f.vx||0)/mag,uy=(f.vy||0)/mag;
        ctx.lineCap="round";
        for(let i=0;i<3;i++){const side=(i-1)*7;ctx.globalAlpha=.16+i*.05;ctx.strokeStyle="#ef4444";ctx.lineWidth=3-i*.5;ctx.beginPath();ctx.moveTo(f.x-uy*side,f.y+ux*side);ctx.lineTo(f.x-ux*(24+i*10)-uy*side,f.y-uy*(24+i*10)+ux*side);ctx.stroke();}
      }
      ctx.restore();
    }
    function drawWokWokCharacter(f){
      const w=f.wok||{};
      drawWokBloodScent(f);
      ctx.save();'''
once(marker, replacement, 'visual')

oldstatus = '''<div class="status-skill-label">깨물기 ${WOK.biteDamage} · 회복${WOK.biteHeal} · 현재 충전 기준 ${wokBiteCooldown(f).toFixed(1)}초</div><div class="status-skill-label">피 냄새 ×${blood} · 실효 이속 ${(w.effectiveSpeed||w.baseSpeed||f.baseSpeed).toFixed(2)} · 전방120°/420 · 중앙60° 돌진 타게팅 · 감지 최저 HP ${prey}% · 돌진 ${dashLeft.toFixed(1)}초</div>'''
newstatus = '''<div class="status-skill-label">깨물기 ${WOK.biteDamage} · 현재 회복${Math.round(WOK.biteHeal*wokHealMultiplier(f))} · 흡혈배율 ×${wokHealMultiplier(f).toFixed(2)} · 현재 충전 기준 ${wokBiteCooldown(f).toFixed(1)}초</div><div class="status-skill-label">피 냄새 ×${blood} · 실효 이속 ${(w.effectiveSpeed||w.baseSpeed||f.baseSpeed).toFixed(2)} · 전방120°/420 · 중앙60° 돌진 타게팅 · 돌진 중 넉백 면역 · 감지 최저 HP ${prey}% · 돌진 ${dashLeft.toFixed(1)}초</div>'''
once(oldstatus, newstatus, 'status')

note = '      const patchNotes = [\n'
newnote = '      const patchNotes = [\n      "v178: 웍웍 피의 사냥/흡혈 연계 강화. 야수의 돌진 중 외부 넉백·넉백 비행·예약 넉백을 무시하고 돌진 벡터를 유지한다. 기존처럼 돌진 속도는 현재 피 냄새 이동속도에 비례하므로 이동속도가 높을수록 같은 0.55초 동안 더 멀리 돌진한다. 웍웍 자신의 체력이 낮을수록 깨물기와 3연타 난타의 회복량이 연속적으로 증가해 HP100%에서 ×1, HP50%에서 ×1.5, 빈사에서 최대 ×2가 된다. 피 냄새 활성 시 현재 감지 대상에서 웍웍으로 흐르는 붉은 냄새 궤적을 표시하고, 대상이 반피 이하이면 궤적·대상 맥박·웍웍 이동 잔상을 강화한다. 120°/60° 판정 영역 자체는 표시하지 않으며 기존 붉은 눈 연출을 유지한다.",\n'
once(note, newnote, 'patch note')

p.write_text(s, encoding='utf-8')
