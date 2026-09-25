from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def once(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 marker, found {n}')
    s = s.replace(old, new, 1)

def exact_count(old, new, count, label):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f'{label}: expected {count} markers, found {n}')
    s = s.replace(old, new)

exact_count('볼배틀 리뉴얼 v143', '볼배틀 리뉴얼 v144', 2, 'version')

once(
    'condition:"등껍질 11초 주기 · 불기둥 20초 주기 · 저체력일수록 불기둥 1→4개", desc:"거대한 몸집의 마왕형 캐릭터. 등껍질 돌진으로 적을 강하게 날리고 벽충돌 피해를 만들며, 마지막 3초에는 상대를 추적한다. 상대와 충돌하면 즉시 돌진을 끝내고 제자리에서 3초 기절하며, 기절 중 받는 피해가 2배가 된다. 맵 중앙을 축으로 회전하는 불기둥은 체력이 낮을수록 늘어난다."',
    'condition:"등껍질 11초 주기 · 불기둥 20초 주기 · 저체력일수록 불기둥 1→4개", desc:"거대한 몸집의 마왕형 캐릭터. 등껍질 돌진으로 적을 강하게 날리고 벽충돌 피해를 만들며, 마지막 3초에는 상대를 추적한다. 상대와 충돌하면 즉시 돌진을 끝내고 제자리에서 3초 기절한다. 맵 중앙을 축으로 회전하는 불기둥은 체력이 낮을수록 늘어나며, 각 불기둥은 같은 상대를 1회만 적중한다."',
    'character description'
)

once(
    'tip: "등껍질은 돌진 1회 동안 같은 상대를 최대 1회만 타격하며, 마지막 3초 동안 적을 추적한다. 상대와 충돌해 기절한 3초 동안 쿱하가 받는 피해는 2배다. 중앙 회전 불기둥은 HP 75% 초과 1개, 50~75% 2개, 25~50% 3개, 25% 이하 4개다. 넉백 저항은 없다."',
    'tip: "등껍질은 돌진 1회 동안 같은 상대를 최대 1회만 타격하며, 마지막 3초 동안 적을 추적한다. 충돌 후 3초 기절은 유지된다. 중앙 회전 불기둥은 HP 75% 초과 1개, 50~75% 2개, 25~50% 3개, 25% 이하 4개이며 각 기둥마다 같은 상대를 1회만 적중한다. 따라서 4개일 때 같은 상대에게 최대 4회 적중할 수 있다. 넉백 저항은 없다."',
    'damage info'
)

once(
    '      if (target.koopa?.recovery > 0) amount *= 2;\n',
    '',
    'remove koopa recovery vulnerability'
)

once(
    '        if(k.recovery>0)return {ratio:clamp(k.recovery/KOOPA.recoveryStun,0,1),className:"rage-fill",text:`등껍질 후 기절 ${k.recovery.toFixed(1)}초 · 받는 피해 ×2`,extraTextHtml:`<div class="status-skill-label">불기둥 ${fire?`발동 중 · ${fireCount}개 · ${fire.life.toFixed(1)}초`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
    '        if(k.recovery>0)return {ratio:clamp(k.recovery/KOOPA.recoveryStun,0,1),className:"rage-fill",text:`등껍질 후 기절 ${k.recovery.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">불기둥 ${fire?`발동 중 · ${fireCount}개 · ${fire.life.toFixed(1)}초`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
    'recovery status'
)

once(
    '        if(k.shellActive)return {ratio:clamp(k.shellTime/KOOPA.shellDuration,0,1),className:"skill-fill",text:`등껍질 돌진 ${k.shellTime.toFixed(1)}초${k.shellTime<=KOOPA.shellTrackAt?" · 추적 중":""}`,extraTextHtml:`<div class="status-skill-label">충돌 시 즉시 3초 기절(받피×2) · 불기둥 ${fire?`${fireCount}개 발동 중`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
    '        if(k.shellActive)return {ratio:clamp(k.shellTime/KOOPA.shellDuration,0,1),className:"skill-fill",text:`등껍질 돌진 ${k.shellTime.toFixed(1)}초${k.shellTime<=KOOPA.shellTrackAt?" · 추적 중":""}`,extraTextHtml:`<div class="status-skill-label">충돌 시 즉시 3초 기절 · 불기둥 ${fire?`${fireCount}개 발동 중`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};',
    'shell status'
)

once(
    '      k.fire={life:KOOPA.fireDuration,angle:rand(0,Math.PI*2),hitCd:{}};k.fireCd=KOOPA.firePeriod;',
    '      k.fire={life:KOOPA.fireDuration,angle:rand(0,Math.PI*2),hitOnce:{}};k.fireCd=KOOPA.firePeriod;',
    'fire state'
)

old_fire = '''    function updateKoopaFire(f,dt){
      const k=f.koopa,fire=k.fire;if(!fire)return;
      fire.life=Math.max(0,fire.life-dt);fire.angle+=KOOPA.fireTurn*dt;
      Object.keys(fire.hitCd).forEach(id=>{fire.hitCd[id]=Math.max(0,(fire.hitCd[id]||0)-dt);});
      const c=arenaCenter(),count=koopaFireCount(f),len=arena.size*.72;
      for(const e of enemiesOf(f)){
        if(!e.alive||(fire.hitCd[e.id]||0)>0)continue;
        let hit=false;
        for(let i=0;i<count;i++){
          const a=fire.angle+i*Math.PI*2/count,x2=c.x+Math.cos(a)*len,y2=c.y+Math.sin(a)*len;
          if(koopaSegmentDistance(c.x,c.y,x2,y2,e.x,e.y)<=e.r+KOOPA.fireWidth){hit=true;break;}
        }
        if(hit){const dealt=damage(e,KOOPA.fireDamage,f,"회전 불기둥");if(dealt>0)koopaApplyBurn(e,f);fire.hitCd[e.id]=KOOPA.fireHitCd;if(!fastSimMode)spawnHitFlash(e.x,e.y,"#fb923c",40);}
      }
      if(fire.life<=0)k.fire=null;
    }'''
new_fire = '''    function updateKoopaFire(f,dt){
      const k=f.koopa,fire=k.fire;if(!fire)return;
      fire.life=Math.max(0,fire.life-dt);fire.angle+=KOOPA.fireTurn*dt;
      const c=arenaCenter(),count=koopaFireCount(f),len=arena.size*.72;
      for(const e of enemiesOf(f)){
        if(!e.alive)continue;
        for(let i=0;i<count;i++){
          const key=`${i}:${e.id}`;if(fire.hitOnce[key])continue;
          const a=fire.angle+i*Math.PI*2/count,x2=c.x+Math.cos(a)*len,y2=c.y+Math.sin(a)*len;
          if(koopaSegmentDistance(c.x,c.y,x2,y2,e.x,e.y)>e.r+KOOPA.fireWidth)continue;
          fire.hitOnce[key]=true;
          const dealt=damage(e,KOOPA.fireDamage,f,"회전 불기둥");if(dealt>0)koopaApplyBurn(e,f);
          if(!fastSimMode)spawnHitFlash(e.x,e.y,"#fb923c",40);
        }
      }
      if(fire.life<=0)k.fire=null;
    }'''
once(old_fire, new_fire, 'per-pillar fire hit logic')

anchor = '      const patchNotes = [\n'
if anchor not in s:
    raise SystemExit('patch notes anchor missing')
s = s.replace(anchor, anchor + '      "v144: 쿱하 상성 폭 조정. 등껍질 충돌 후 3초 기절은 유지하되 기절 중 받는 피해 2배를 제거. 회전 불기둥은 한 번의 소환 동안 각 기둥마다 같은 상대를 최대 1회만 적중하도록 변경하여, 4개일 경우 각 기둥 1회씩 최대 4회 적중. 불기둥 20초 주기와 나머지 수치는 유지.",\n', 1)

p.write_text(s, encoding='utf-8')
print('v144 patch applied')
