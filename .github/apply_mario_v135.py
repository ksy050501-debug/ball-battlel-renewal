from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if '<title>볼배틀 리뉴얼 v135</title>' in s:
    print('v135 already applied')
    raise SystemExit(0)


def sub_one(pattern, repl, label, flags=0):
    global s
    s2, n = re.subn(pattern, repl, s, count=1, flags=flags)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 match, found {n}')
    s = s2


def replace_one(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {n}')
    s = s.replace(old, new, 1)

replace_one('<title>볼배틀 리뉴얼 v134</title>', '<title>볼배틀 리뉴얼 v135</title>', 'title')

# 캐릭터 카드 설명
sub_one(
    r'      \{ id:"mario_plumber", name:"배관공", mark:"M", role:"게임", color:"#ef4444", hp:160, attack:8, speed:2\.8, range:0,\n        skillName:"랜덤박스 · 배관공카트", condition:".*?", desc:".*?" \},',
    '''      { id:"mario_plumber", name:"배관공", mark:"M", role:"게임", color:"#ef4444", hp:160, attack:8, speed:2.8, range:0,\n        skillName:"랜덤박스 · 토관 · 배관공카트", condition:"랜덤박스 파워업 · 벽 50회마다 토관을 통해 기본↔카트 모드 전환", desc:"랜덤박스로 슈퍼·파이어·스타 상태를 오가며 싸운다. 벽 접촉 50회를 채우면 충돌한 벽의 초록 토관으로 느리게 들어가고, 무작위 벽의 토관에서 반대 모드로 나온다. 카트 모드에서는 바나나와 등껍질을 사용한다." },''',
    'character entry',
    re.S,
)

# 피해/설명 카드
sub_one(
    r'      if \(c\.id === "mario_plumber"\) return \{damage:.*?\};',
    '''      if (c.id === "mario_plumber") return {damage:"랜덤박스 접촉5 / 슈퍼펀치10 / 파이어볼9+화상1×3(갱신형) / 슈퍼스타 접촉12 / 카트충돌9 / 바나나4 / 초록등껍질24 / 빨간등껍질14",tick:"랜덤박스5초 · 박스HP60 · 상대2회 접촉 제거 · 파이어볼1.75초·벽2회반사·5발마다 파워업1칸 소모 · 스타6초 후 직전 상태 복귀 · 벽50회마다 토관 전환 · 카트 아이템3개·3.5초마다1개 사용",tip:"파이어 화상은 피해1씩 3틱이며 같은 배관공의 파이어볼을 여러 번 맞아도 화상이 여러 줄로 중첩되지 않고 남은 지속시간만 새로 갱신된다. 파이어볼을 5발 발사할 때마다 파이어 상태 5칸 중 1칸이 소모된다. 스타는 획득 직전의 기본/슈퍼/파이어 상태와 남은 보호막을 기억했다가 6초 뒤 그대로 되돌아간다. 기본 또는 카트 모드에서 벽50회를 채우면 충돌한 벽에 초록 토관이 생기고 감속한 채 토관으로 들어간 뒤 무작위 벽 토관에서 반대 모드로 나온다. 카트 아이템 피격의 회전은 별도 이펙트가 아니라 캐릭터 몸 자체가 회전한다."};''',
    'damage info',
    re.S,
)

# Mario 전체 구현 교체
MARIO_CODE = r'''    const MARIO = {
      blockDelay:5, blockHp:60, blockTouchDamage:5, blockTouchNeed:2, blockChaseDelay:15,
      shieldMax:5, blinkTime:.8,
      fireDamage:9, firePeriod:1.75, fireSpeed:320, fireLife:3.2, fireBounces:2,
      fireBurnDamage:1, fireBurnTicks:3, fireBurnTick:.6, fireShotsPerShield:5,
      starDuration:6, starSpeedMult:1.55, starDamage:12, starContactCd:.35,
      superPunchDamage:10, superPunchKnock:260, superPunchCd:.70,
      kartWallNeed:50, kartSpeedMult:1.35, kartContactDamage:9, kartContactKnock:250, kartContactCd:.55,
      kartItemCount:3, kartItemUsePeriod:3.5,
      bananaDamage:4, bananaSlow:2.4, bananaSlowMult:.55, bananaR:9,
      greenDamage:24, greenSpeed:330, greenR:8,
      redDamage:14, redSpeed:290, redTurn:6.5, redR:8,
      shellSpin:.9,
      pipeApproachMult:.42, pipeEnterDuration:.48, pipeTravelDuration:.52, pipeExitDuration:.48
    };
    function initMario(f){
      f.mario={
        power:"none",shield:0,blockId:null,nextBlock:MARIO.blockDelay,blink:0,fireCd:0,fireShots:0,fireballs:[],starTime:0,starHits:{},starReturn:null,
        baseR:f.r||20,baseSpeed:f.baseSpeed||f.speed||2.8,superStance:false,punchCd:0,wallContacts:0,
        kart:false,pipeFx:0,pipeTransit:null,kartContactCd:0,pickup:null,heldType:"",heldCount:0,itemUseCd:0,bananas:[],shells:[]
      };
    }
    function marioSetMotionSpeed(f,mult=1){
      const m=f.mario;if(!m)return;const speed=m.baseSpeed*mult;f.speed=speed;f.baseSpeed=speed;
      const mag=Math.hypot(f.vx,f.vy),a=mag>.01?Math.atan2(f.vy,f.vx):rand(0,Math.PI*2),v=speed*44;
      f.vx=Math.cos(a)*v;f.vy=Math.sin(a)*v;
    }
    function marioResetPower(f,blink=false){
      const m=f?.mario;if(!m)return;m.power="none";m.shield=0;m.starTime=0;m.starReturn=null;m.fireCd=0;m.fireShots=0;m.fireballs=[];m.starHits={};m.superStance=false;f.r=m.baseR;
      marioSetMotionSpeed(f,m.kart?MARIO.kartSpeedMult:1);if(blink)m.blink=Math.max(m.blink,MARIO.blinkTime);
    }
    function marioSpawnBlock(f){
      const m=f?.mario;if(!m||m.kart||m.blockId||m.pipeTransit)return;
      const r=16,x=rand(arena.x+r+8,arena.x2-r-8),y=rand(arena.y+r+8,arena.y2-r-8);
      const spec={id:"mario_question_block",name:"랜덤박스",mark:"?",role:"오브젝트",color:"#fbbf24",hp:MARIO.blockHp,attack:0,speed:0,range:0,skillName:"랜덤 파워업",condition:""};
      const b=makeFighter(spec,{x,y},fighterSerial++,f.id,f.teamId||null);b.r=r;b.vx=0;b.vy=0;b.speed=0;b.baseSpeed=0;
      b.marioBlock={ownerId:f.id,anchorX:x,anchorY:y,age:0,touches:0};b.isSummon=true;b.contactCd=0;fighters.push(b);m.blockId=b.id;m.nextBlock=MARIO.blockDelay;
      if(!fastSimMode){spawnParticles(x,y,"#fde68a",7);spawnFloatingText(x,y-r-12,"랜덤박스","#fde68a");}
    }
    function damageMarioBlock(block,amount,source,reason){
      if(!block?.alive||!block.marioBlock||amount<=0)return 0;
      const dealt=Math.min(block.hp,Math.max(1,Math.round(amount)));block.hp=Math.max(0,block.hp-dealt);
      if(!fastSimMode){spawnHitFlash(block.x,block.y,"#fde68a",22);spawnFloatingText(block.x,block.y-block.r-18,"-"+dealt,"#fde68a");}
      if(block.hp<=0)block.alive=false;
      return dealt;
    }
    function marioBlockEnemyContact(block,other){
      if(!block?.alive||!block.marioBlock||!other?.alive||block.contactCd>0)return false;
      const owner=fighterById(block.marioBlock.ownerId);if(!owner?.alive||!areEnemies(owner,other))return false;
      damage(other,MARIO.blockTouchDamage,owner,"랜덤박스 충돌");block.marioBlock.touches+=1;block.contactCd=.55;
      if(!fastSimMode)spawnFloatingText(other.x,other.y-other.r-26,"랜덤박스 -"+MARIO.blockTouchDamage,"#fde68a");
      if(block.marioBlock.touches>=MARIO.blockTouchNeed)block.alive=false;
      return true;
    }
    function marioRestoreStarState(f){
      const m=f?.mario;if(!m)return;const back=m.starReturn||{power:"none",shield:0,fireCd:0,fireShots:0};
      m.starReturn=null;m.starTime=0;m.starHits={};m.power=back.power||"none";m.shield=Math.max(0,back.shield||0);m.fireShots=back.fireShots||0;
      if(m.power==="fire"){f.r=m.baseR*1.18;m.fireCd=Math.max(.05,back.fireCd||.25);}
      else if(m.power==="mushroom"){f.r=m.baseR*1.18;m.fireCd=0;}
      else{m.power="none";m.shield=0;m.fireCd=0;m.fireShots=0;f.r=m.baseR;}
      marioSetMotionSpeed(f,1);
      if(!fastSimMode)spawnFloatingText(f.x,f.y-f.r-30,m.power==="fire"?"파이어 상태 복귀":m.power==="mushroom"?"슈퍼 상태 복귀":"기본 상태 복귀","#fef3c7");
    }
    function marioApplyPower(f,kind){
      const m=f.mario;m.blink=0;m.starHits={};m.superStance=false;
      if(kind==="star"){
        if(m.power!=="star")m.starReturn={power:m.power,shield:m.shield,fireCd:m.fireCd,fireShots:m.fireShots||0};
        m.power="star";m.starTime=MARIO.starDuration;f.r=m.baseR*1.08;marioSetMotionSpeed(f,MARIO.starSpeedMult);
        spawnFloatingText(f.x,f.y-f.r-28,"스타배관공!","#fde047");spawnBlast(f.x,f.y,64,"#fde047");return;
      }
      m.starReturn=null;m.starTime=0;m.fireballs=[];m.fireShots=0;m.power=kind;m.shield=MARIO.shieldMax;f.r=m.baseR*1.18;marioSetMotionSpeed(f,1);
      if(kind==="fire"){m.fireCd=.25;spawnFloatingText(f.x,f.y-f.r-28,"파이어배관공!","#f8fafc");spawnBlast(f.x,f.y,54,"#fb923c");}
      else {m.fireCd=0;spawnFloatingText(f.x,f.y-f.r-28,"슈퍼배관공!","#fca5a5");spawnBlast(f.x,f.y,54,"#ef4444");}
    }
    function marioCollectBlock(f,b){
      if(!f?.mario||f.mario.kart||f.mario.pipeTransit||!b?.alive||!b.marioBlock)return;b.alive=false;f.mario.blockId=null;f.mario.nextBlock=MARIO.blockDelay;
      const roll=Math.floor(Math.random()*3),kind=roll===0?"mushroom":roll===1?"fire":"star";marioApplyPower(f,kind);
    }
    function marioAbsorbDamage(f,amount,source,reason){
      const m=f?.mario;if(!m||amount<=0)return null;
      if(m.pipeTransit&&m.pipeTransit.phase!=="approach")return 0;
      if(m.power==="star"||m.blink>0){if(!fastSimMode)spawnFloatingText(f.x,f.y-f.r-20,"무적","#fde047");return 0;}
      if((m.power==="mushroom"||m.power==="fire")&&m.shield>0){
        const cost=Math.max(1,Math.ceil(amount/10));m.shield=Math.max(0,m.shield-cost);
        if(!fastSimMode){spawnHitFlash(f.x,f.y,m.power==="fire"?"#fb923c":"#fca5a5",38);spawnFloatingText(f.x,f.y-f.r-22,"보호막 -"+cost+" ("+m.shield+"/"+MARIO.shieldMax+")","#fef3c7");}
        if(m.shield<=0){marioResetPower(f,true);spawnFloatingText(f.x,f.y-f.r-34,"파워다운!","#fca5a5");}
        return amount;
      }
      return null;
    }
    function marioFire(f){
      const m=f.mario,target=enemiesOf(f).filter(e=>e.alive&&!e.marioBlock).sort((a,b)=>dist(f,a)-dist(f,b))[0];if(!target)return false;
      const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;
      m.fireballs.push({x:f.x+dx/d*(f.r+7),y:f.y+dy/d*(f.r+7),vx:dx/d*MARIO.fireSpeed,vy:dy/d*MARIO.fireSpeed,r:6,life:MARIO.fireLife,bounces:MARIO.fireBounces});
      m.fireShots=(m.fireShots||0)+1;
      if(m.fireShots>=MARIO.fireShotsPerShield){
        m.fireShots=0;m.shield=Math.max(0,m.shield-1);
        if(!fastSimMode)spawnFloatingText(f.x,f.y-f.r-34,"파이어 5발 · 지속칸 -1 ("+m.shield+"/"+MARIO.shieldMax+")","#fef3c7");
        if(m.shield<=0){const live=m.fireballs.slice();marioResetPower(f,true);m.fireballs=live;if(!fastSimMode)spawnFloatingText(f.x,f.y-f.r-48,"파이어 소진!","#fca5a5");}
      }
      if(!fastSimMode)spawnParticles(f.x+dx/d*f.r,f.y+dy/d*f.r,"#fb923c",5);return true;
    }
    function marioRefreshBurn(hit,source){
      if(!hit?.alive||hasHarmfulImmunity(hit))return;hit.burningTicks ||= [];
      const duration=MARIO.fireBurnTick*MARIO.fireBurnTicks+.05;
      const existing=hit.burningTicks.find(b=>b.kind==="marioFire"&&b.source===source);
      if(existing){existing.t=duration;existing.power=MARIO.fireBurnDamage;existing.tick=MARIO.fireBurnTick;existing.ticksLeft=MARIO.fireBurnTicks;existing.next=Math.min(existing.next>0?existing.next:MARIO.fireBurnTick,MARIO.fireBurnTick);return;}
      hit.burningTicks.push({kind:"marioFire",t:duration,next:MARIO.fireBurnTick,power:MARIO.fireBurnDamage,source,tick:MARIO.fireBurnTick,ticksLeft:MARIO.fireBurnTicks});
    }
    function updateMarioFireballs(f,dt){
      const m=f.mario;
      for(let i=m.fireballs.length-1;i>=0;i--){const p=m.fireballs[i],ox=p.x,oy=p.y;p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt;let wall=false;
        if(p.x-p.r<=arena.x||p.x+p.r>=arena.x2){p.x=clamp(p.x,arena.x+p.r,arena.x2-p.r);p.vx*=-1;wall=true;}
        if(p.y-p.r<=arena.y||p.y+p.r>=arena.y2){p.y=clamp(p.y,arena.y+p.r,arena.y2-p.r);p.vy*=-1;wall=true;}
        if(wall){if(p.bounces>0)p.bounces--;else{m.fireballs.splice(i,1);continue;}}
        let hit=null,best=1;
        for(const e of enemiesOf(f)){if(!e.alive||e.tano?.hidden>0||e.marioBlock)continue;const h=spiderSegHit(ox,oy,p.x,p.y,e.x,e.y,e.r+p.r);if(h!==null&&h<best){best=h;hit=e;}}
        if(hit){const dealt=damage(hit,MARIO.fireDamage,f,"파이어볼");if(dealt>0)marioRefreshBurn(hit,f);if(!fastSimMode)spawnHitFlash(hit.x,hit.y,"#fb923c",45);m.fireballs.splice(i,1);continue;}
        if(p.life<=0)m.fireballs.splice(i,1);
      }
    }
    function marioSuperPunchContact(f,target){
      const m=f?.mario;if(!m||m.kart||m.pipeTransit||m.power!=="mushroom"||m.punchCd>0||!target?.alive||!areEnemies(f,target))return false;
      const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;const dealt=damage(target,MARIO.superPunchDamage,f,"슈퍼펀치");
      if(dealt>0&&target.alive){target.vx+=dx/d*MARIO.superPunchKnock;target.vy+=dy/d*MARIO.superPunchKnock;}
      m.punchCd=MARIO.superPunchCd;if(!fastSimMode){spawnHitFlash(target.x,target.y,"#fca5a5",46);spawnFloatingText(target.x,target.y-target.r-28,"슈퍼펀치!","#fca5a5");}return true;
    }
    function marioApplySpin(target,duration=MARIO.shellSpin,slow=0){
      if(!target?.alive)return;target.marioSpinFx=Math.max(target.marioSpinFx||0,duration);if(slow>0)target.marioItemSlow=Math.max(target.marioItemSlow||0,slow);
    }
    function marioKartTarget(f){
      const mains=enemiesOf(f).filter(e=>e.alive&&!e.isSummon&&!e.marioBlock);if(mains.length)return mains.sort((a,b)=>dist(f,a)-dist(f,b))[0];
      return enemiesOf(f).find(e=>e.alive&&!e.marioBlock)||null;
    }
    function marioFarthestWallTarget(f){
      const options=[{wall:"left",d:f.x-arena.x},{wall:"right",d:arena.x2-f.x},{wall:"top",d:f.y-arena.y},{wall:"bottom",d:arena.y2-f.y}],mx=Math.max(...options.map(o=>o.d)),choices=options.filter(o=>Math.abs(o.d-mx)<1.5),pick=choices[Math.floor(Math.random()*choices.length)],pad=24;
      if(pick.wall==="left")return {x:arena.x,y:rand(arena.y+pad,arena.y2-pad)};
      if(pick.wall==="right")return {x:arena.x2,y:rand(arena.y+pad,arena.y2-pad)};
      if(pick.wall==="top")return {x:rand(arena.x+pad,arena.x2-pad),y:arena.y};
      return {x:rand(arena.x+pad,arena.x2-pad),y:arena.y2};
    }
    function marioItemName(type){return type==="banana"?"바나나":type==="green"?"초록등껍질":type==="red"?"빨간등껍질":"없음";}
    function marioGrantKartItem(f){
      const m=f.mario;if(m.heldCount>0)return;const r=Math.floor(Math.random()*3);m.heldType=r===0?"banana":r===1?"green":"red";m.heldCount=MARIO.kartItemCount;m.itemUseCd=MARIO.kartItemUsePeriod;
      spawnFloatingText(f.x,f.y-f.r-38,marioItemName(m.heldType)+" ×"+m.heldCount,"#e9d5ff");
    }
    function marioSpawnKartPickup(f){
      const m=f.mario;if(!m.kart||m.pickup||m.pipeTransit)return;const r=14;m.pickup={x:rand(arena.x+r+8,arena.x2-r-8),y:rand(arena.y+r+8,arena.y2-r-8),r};m.nextBlock=MARIO.blockDelay;
      if(!fastSimMode)spawnFloatingText(m.pickup.x,m.pickup.y-r-10,"랜덤 아이템","#e9d5ff");
    }
    function marioUseKartItem(f){
      const m=f.mario;if(!m.kart||m.pipeTransit||m.heldCount<=0||!m.heldType)return false;const type=m.heldType;
      if(type==="banana"){
        const mag=Math.hypot(f.vx,f.vy)||1,dx=f.vx/mag,dy=f.vy/mag;m.bananas.push({x:clamp(f.x-dx*(f.r+18),arena.x+MARIO.bananaR,arena.x2-MARIO.bananaR),y:clamp(f.y-dy*(f.r+18),arena.y+MARIO.bananaR,arena.y2-MARIO.bananaR),r:MARIO.bananaR,ownerGrace:.65});
      }else if(type==="green"){
        const t=marioFarthestWallTarget(f),dx=t.x-f.x,dy=t.y-f.y,d=Math.hypot(dx,dy)||1;m.shells.push({kind:"green",x:f.x+dx/d*(f.r+9),y:f.y+dy/d*(f.r+9),vx:dx/d*MARIO.greenSpeed,vy:dy/d*MARIO.greenSpeed,r:MARIO.greenR,ownerGrace:.45});
      }else{
        const target=marioKartTarget(f);if(target){const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;m.shells.push({kind:"red",targetId:target.id,x:f.x+dx/d*(f.r+9),y:f.y+dy/d*(f.r+9),vx:dx/d*MARIO.redSpeed,vy:dy/d*MARIO.redSpeed,r:MARIO.redR});}
      }
      m.heldCount-=1;if(m.heldCount<=0){m.heldCount=0;m.heldType="";m.itemUseCd=0;}else m.itemUseCd=MARIO.kartItemUsePeriod;return true;
    }
    function updateMarioKartPickup(f,dt){
      const m=f.mario;if(m.pickup){const p=m.pickup;if(Math.hypot(f.x-p.x,f.y-p.y)<=f.r+p.r){if(m.heldCount<=0)marioGrantKartItem(f);m.pickup=null;m.nextBlock=MARIO.blockDelay;}else{
          const blocker=enemiesOf(f).find(e=>e.alive&&!e.isSummon&&!e.marioBlock&&Math.hypot(e.x-p.x,e.y-p.y)<=e.r+p.r);if(blocker){m.pickup=null;m.nextBlock=MARIO.blockDelay;}
        }}else{m.nextBlock=Math.max(0,m.nextBlock-dt);if(m.nextBlock<=0)marioSpawnKartPickup(f);}
      if(m.heldCount>0){m.itemUseCd-=dt;if(m.itemUseCd<=0)marioUseKartItem(f);}
    }
    function updateMarioKartHazards(f,dt){
      const m=f.mario;
      for(let i=m.bananas.length-1;i>=0;i--){const b=m.bananas[i];b.ownerGrace=Math.max(0,(b.ownerGrace||0)-dt);const candidates=fighters.filter(e=>e.alive&&!e.isSummon&&!e.marioBlock&&(e===f||areEnemies(f,e)));
        const hit=candidates.find(e=>(e!==f||b.ownerGrace<=0)&&Math.hypot(e.x-b.x,e.y-b.y)<=e.r+b.r);if(hit){damage(hit,MARIO.bananaDamage,f,"바나나");marioApplySpin(hit,.9,MARIO.bananaSlow);if(!fastSimMode){spawnFloatingText(hit.x,hit.y-hit.r-26,"바나나!","#fde047");spawnParticles(hit.x,hit.y,"#fde047",10);}m.bananas.splice(i,1);}}
      for(let i=m.shells.length-1;i>=0;i--){const sh=m.shells[i],ox=sh.x,oy=sh.y;sh.ownerGrace=Math.max(0,(sh.ownerGrace||0)-dt);
        if(sh.kind==="red"){let target=fighterById(sh.targetId);if(!target||target.isSummon||target.marioBlock||!areEnemies(f,target)){target=marioKartTarget(f);if(target)sh.targetId=target.id;}if(target){const wanted=Math.atan2(target.y-sh.y,target.x-sh.x),cur=Math.atan2(sh.vy,sh.vx),delta=Math.atan2(Math.sin(wanted-cur),Math.cos(wanted-cur)),a=cur+clamp(delta,-MARIO.redTurn*dt,MARIO.redTurn*dt);sh.vx=Math.cos(a)*MARIO.redSpeed;sh.vy=Math.sin(a)*MARIO.redSpeed;}}
        sh.x+=sh.vx*dt;sh.y+=sh.vy*dt;
        if(sh.x-sh.r<=arena.x||sh.x+sh.r>=arena.x2){sh.x=clamp(sh.x,arena.x+sh.r,arena.x2-sh.r);sh.vx*=-1;}
        if(sh.y-sh.r<=arena.y||sh.y+sh.r>=arena.y2){sh.y=clamp(sh.y,arena.y+sh.r,arena.y2-sh.r);sh.vy*=-1;}
        const candidates=sh.kind==="green"?fighters.filter(e=>e.alive&&!e.marioBlock&&(e===f||areEnemies(f,e))):enemiesOf(f).filter(e=>e.alive&&!e.marioBlock);
        let hit=null,best=2;for(const e of candidates){if(e===f&&(sh.ownerGrace||0)>0)continue;const h=spiderSegHit(ox,oy,sh.x,sh.y,e.x,e.y,e.r+sh.r);if(h!==null&&h<best){best=h;hit=e;}}
        if(hit){const power=sh.kind==="green"?MARIO.greenDamage:MARIO.redDamage;damage(hit,power,f,sh.kind==="green"?"초록등껍질":"빨간등껍질");marioApplySpin(hit,MARIO.shellSpin,0);if(!fastSimMode){spawnHitFlash(hit.x,hit.y,sh.kind==="green"?"#22c55e":"#ef4444",58);spawnFloatingText(hit.x,hit.y-hit.r-28,sh.kind==="green"?"초록등껍질!":"빨간등껍질!",sh.kind==="green"?"#86efac":"#fca5a5");}m.shells.splice(i,1);}
      }
    }
    function marioPipePoint(wall,coord){
      const margin=54;
      if(wall==="left")return {wall,x:arena.x,y:clamp(coord,arena.y+margin,arena.y2-margin)};
      if(wall==="right")return {wall,x:arena.x2,y:clamp(coord,arena.y+margin,arena.y2-margin)};
      if(wall==="top")return {wall,x:clamp(coord,arena.x+margin,arena.x2-margin),y:arena.y};
      return {wall:"bottom",x:clamp(coord,arena.x+margin,arena.x2-margin),y:arena.y2};
    }
    function marioRandomPipe(entry){
      const walls=["left","right","top","bottom"],wall=walls[Math.floor(Math.random()*walls.length)],margin=64;
      let p=wall==="left"?{wall,x:arena.x,y:rand(arena.y+margin,arena.y2-margin)}:wall==="right"?{wall,x:arena.x2,y:rand(arena.y+margin,arena.y2-margin)}:wall==="top"?{wall,x:rand(arena.x+margin,arena.x2-margin),y:arena.y}:{wall,x:rand(arena.x+margin,arena.x2-margin),y:arena.y2};
      if(entry&&p.wall===entry.wall&&Math.hypot(p.x-entry.x,p.y-entry.y)<arena.size*.22){if(p.wall==="left"||p.wall==="right")p.y=clamp(p.y+arena.size*.35,arena.y+margin,arena.y2-margin);else p.x=clamp(p.x+arena.size*.35,arena.x+margin,arena.x2-margin);}
      return p;
    }
    function marioPipeApproachPoint(pipe,r){
      const mouth=34,extra=r*.18;
      if(pipe.wall==="left")return {x:arena.x+mouth+extra,y:pipe.y};if(pipe.wall==="right")return {x:arena.x2-mouth-extra,y:pipe.y};if(pipe.wall==="top")return {x:pipe.x,y:arena.y+mouth+extra};return {x:pipe.x,y:arena.y2-mouth-extra};
    }
    function marioPipeHiddenPoint(pipe,r){
      if(pipe.wall==="left")return {x:arena.x-r*.9,y:pipe.y};if(pipe.wall==="right")return {x:arena.x2+r*.9,y:pipe.y};if(pipe.wall==="top")return {x:pipe.x,y:arena.y-r*.9};return {x:pipe.x,y:arena.y2+r*.9};
    }
    function marioPipeInward(pipe){return pipe.wall==="left"?{x:1,y:0}:pipe.wall==="right"?{x:-1,y:0}:pipe.wall==="top"?{x:0,y:1}:{x:0,y:-1};}
    function marioClearKartKit(m){m.pickup=null;m.heldType="";m.heldCount=0;m.itemUseCd=0;m.bananas=[];m.shells=[];}
    function marioSwitchPipeMode(f,toKart){
      const m=f.mario;
      if(m.blockId){const b=fighterById(m.blockId);if(b)b.alive=false;}m.blockId=null;
      marioClearKartKit(m);m.kart=!!toKart;marioResetPower(f,false);m.kart=!!toKart;m.wallContacts=0;m.nextBlock=MARIO.blockDelay;m.superStance=false;
      marioSetMotionSpeed(f,m.kart?MARIO.kartSpeedMult:1);
    }
    function startMarioPipeTransition(f,hit){
      const m=f?.mario;if(!m||m.pipeTransit)return;const fallback=marioPipePoint("left",f.y),entry=hit?.wall?marioPipePoint(hit.wall,(hit.wall==="left"||hit.wall==="right")?hit.y:hit.x):fallback;
      m.pipeTransit={phase:"approach",toKart:!m.kart,entry,exit:marioRandomPipe(entry),timer:0,phaseMax:0,visualScale:1,visualAlpha:1};m.wallContacts=MARIO.kartWallNeed;m.superStance=false;f.vx=0;f.vy=0;
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-42,(m.kart?"기본":"카트")+" 모드 토관!","#4ade80");playSound("warp",.55);}
    }
    function marioWallContact(f,hit){const m=f?.mario;if(!m||m.pipeTransit)return;m.wallContacts=Math.min(MARIO.kartWallNeed,m.wallContacts+1);if(m.wallContacts>=MARIO.kartWallNeed)startMarioPipeTransition(f,hit);}
    function marioKartContact(f,target){
      const m=f?.mario;if(!m?.kart||m.pipeTransit||m.kartContactCd>0||!target?.alive||!areEnemies(f,target))return false;const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1,dealt=damage(target,MARIO.kartContactDamage,f,"카트충돌");if(dealt>0&&target.alive){target.vx+=dx/d*MARIO.kartContactKnock;target.vy+=dy/d*MARIO.kartContactKnock;}m.kartContactCd=MARIO.kartContactCd;if(!fastSimMode)spawnHitFlash(target.x,target.y,"#60a5fa",42);return true;
    }
    function updateMarioPipeTransit(f,dt){
      const m=f.mario,tr=m.pipeTransit;if(!tr)return false;
      if(tr.phase==="approach"){
        const target=marioPipeApproachPoint(tr.entry,f.r),dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1,speed=m.baseSpeed*44*(m.kart?MARIO.kartSpeedMult:1)*MARIO.pipeApproachMult,step=Math.min(d,speed*dt);
        f.x+=dx/d*step;f.y+=dy/d*step;f.vx=0;f.vy=0;
        if(d<=2.5){tr.phase="enter";tr.timer=MARIO.pipeEnterDuration;tr.phaseMax=MARIO.pipeEnterDuration;tr.start={x:f.x,y:f.y};tr.end=marioPipeHiddenPoint(tr.entry,f.r);}
        return true;
      }
      if(tr.phase==="enter"){
        tr.timer=Math.max(0,tr.timer-dt);const p=clamp(1-tr.timer/tr.phaseMax,0,1);f.x=tr.start.x+(tr.end.x-tr.start.x)*p;f.y=tr.start.y+(tr.end.y-tr.start.y)*p;tr.visualScale=1-p*.72;tr.visualAlpha=1-p*.55;f.vx=0;f.vy=0;
        if(tr.timer<=0){marioSwitchPipeMode(f,tr.toKart);tr.phase="hidden";tr.timer=MARIO.pipeTravelDuration;tr.phaseMax=MARIO.pipeTravelDuration;tr.visualScale=.28;tr.visualAlpha=0;f.x=-10000;f.y=-10000;if(!fastSimMode)playSound("warp",.8);}
        return true;
      }
      if(tr.phase==="hidden"){
        tr.timer=Math.max(0,tr.timer-dt);f.vx=0;f.vy=0;
        if(tr.timer<=0){tr.phase="exit";tr.timer=MARIO.pipeExitDuration;tr.phaseMax=MARIO.pipeExitDuration;tr.start=marioPipeHiddenPoint(tr.exit,f.r);tr.end=marioPipeApproachPoint(tr.exit,f.r);f.x=tr.start.x;f.y=tr.start.y;tr.visualScale=.28;tr.visualAlpha=.45;}
        return true;
      }
      if(tr.phase==="exit"){
        tr.timer=Math.max(0,tr.timer-dt);const p=clamp(1-tr.timer/tr.phaseMax,0,1);f.x=tr.start.x+(tr.end.x-tr.start.x)*p;f.y=tr.start.y+(tr.end.y-tr.start.y)*p;tr.visualScale=.28+.72*p;tr.visualAlpha=.45+.55*p;f.vx=0;f.vy=0;
        if(tr.timer<=0){const exit=tr.exit,inward=marioPipeInward(exit),speed=m.baseSpeed*44*(m.kart?MARIO.kartSpeedMult:1);f.x=tr.end.x;f.y=tr.end.y;f.vx=inward.x*speed;f.vy=inward.y*speed;m.pipeTransit=null;m.wallContacts=0;if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-40,m.kart?"배관공카트 출발!":"기본 배관공 복귀!","#86efac");playSound("warp",.9);}}
        return true;
      }
      return false;
    }
    function updateMario(f,dt){
      const m=f?.mario;if(!m||!f.alive)return;m.blink=Math.max(0,m.blink-dt);m.punchCd=Math.max(0,m.punchCd-dt);m.kartContactCd=Math.max(0,m.kartContactCd-dt);updateMarioFireballs(f,dt);
      if(m.pipeTransit){updateMarioPipeTransit(f,dt);return;}
      if(m.kart){m.superStance=false;updateMarioKartPickup(f,dt);updateMarioKartHazards(f,dt);if(!fastSimMode&&Math.random()<dt*5){const mag=Math.hypot(f.vx,f.vy)||1;spawnParticles(f.x-f.vx/mag*(f.r+10),f.y-f.vy/mag*(f.r+10),"#cbd5e1",1);}return;}
      if(m.blockId){const b=fighterById(m.blockId);if(!b||!b.alive){m.blockId=null;m.superStance=false;m.nextBlock=MARIO.blockDelay;}else if(Math.hypot(f.x-b.x,f.y-b.y)<=f.r+b.r+3){marioCollectBlock(f,b);}else if(m.power==="none"&&(b.marioBlock?.age||0)>=MARIO.blockChaseDelay){m.superStance=true;const dx=b.x-f.x,dy=b.y-f.y,d=Math.hypot(dx,dy)||1,v=m.baseSpeed*44;f.vx=dx/d*v;f.vy=dy/d*v;}else m.superStance=false;
      }else{m.superStance=false;m.nextBlock=Math.max(0,m.nextBlock-dt);if(m.nextBlock<=0)marioSpawnBlock(f);}
      if(m.power==="star"){
        m.starTime-=dt;for(const id of Object.keys(m.starHits))m.starHits[id]=Math.max(0,m.starHits[id]-dt);
        for(const e of enemiesOf(f)){if(!e.alive||e.marioBlock||Math.hypot(e.x-f.x,e.y-f.y)>f.r+e.r+3||(m.starHits[e.id]||0)>0)continue;const dx=e.x-f.x,dy=e.y-f.y,d=Math.hypot(dx,dy)||1;damage(e,MARIO.starDamage,f,"슈퍼스타");e.vx+=dx/d*220;e.vy+=dy/d*220;m.starHits[e.id]=MARIO.starContactCd;if(!fastSimMode)spawnHitFlash(e.x,e.y,`hsl(${(battleTime*180)%360} 90% 65%)`,58);}
        if(m.starTime<=0)marioRestoreStarState(f);return;
      }
      if(m.power==="fire"){m.fireCd-=dt;if(m.fireCd<=0){const fired=marioFire(f);if(fired&&m.power==="fire")m.fireCd+=MARIO.firePeriod;else if(!fired)m.fireCd=.25;}}
    }
    function drawMarioBlock(f){
      ctx.save();ctx.translate(f.x,f.y);ctx.fillStyle="#fbbf24";ctx.strokeStyle="#92400e";ctx.lineWidth=3;ctx.fillRect(-f.r,-f.r,f.r*2,f.r*2);ctx.strokeRect(-f.r,-f.r,f.r*2,f.r*2);ctx.fillStyle="#fff7ed";ctx.font="1000 22px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("?",0,1);ctx.restore();drawHealthBar(f);
    }
    function drawMarioSpinOverlay(f){}
    function drawMarioPipeAt(pipe,alpha=1){
      if(!pipe||fastSimMode)return;const angle=pipe.wall==="left"?0:pipe.wall==="right"?Math.PI:pipe.wall==="top"?Math.PI/2:-Math.PI/2;
      ctx.save();ctx.translate(pipe.x,pipe.y);ctx.rotate(angle);ctx.globalAlpha=alpha;ctx.shadowColor="#14532d";ctx.shadowBlur=10;ctx.fillStyle="#15803d";ctx.strokeStyle="#86efac";ctx.lineWidth=2;ctx.fillRect(0,-12,32,24);ctx.strokeRect(0,-12,32,24);ctx.fillStyle="#22c55e";ctx.beginPath();ctx.roundRect(27,-17,11,34,4);ctx.fill();ctx.stroke();ctx.fillStyle="rgba(255,255,255,.18)";ctx.fillRect(5,-8,5,16);ctx.restore();
    }
    function drawMarioCharacter(f){
      const m=f.mario||{power:"none",shield:0,blink:0,fireballs:[],bananas:[],shells:[]},tr=m.pipeTransit;
      if(!f.portraitOnly&&!fastSimMode){ctx.save();ctx.beginPath();ctx.rect(arena.x,arena.y,arena.size,arena.size);ctx.clip();
        for(const p of m.fireballs||[]){ctx.shadowColor="#fb923c";ctx.shadowBlur=12;ctx.fillStyle="#f97316";ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fde68a";ctx.beginPath();ctx.arc(p.x-2,p.y-2,p.r*.45,0,Math.PI*2);ctx.fill();}
        for(const b of m.bananas||[]){ctx.fillStyle="#fde047";ctx.strokeStyle="#a16207";ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(b.x-8,b.y-5);ctx.quadraticCurveTo(b.x,b.y+10,b.x+8,b.y-5);ctx.quadraticCurveTo(b.x,b.y+3,b.x-8,b.y-5);ctx.fill();ctx.stroke();}
        for(const sh of m.shells||[]){ctx.fillStyle=sh.kind==="green"?"#22c55e":"#ef4444";ctx.strokeStyle="#f8fafc";ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(sh.x,sh.y,sh.r,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.strokeStyle="#14532d";ctx.beginPath();ctx.arc(sh.x,sh.y,sh.r*.55,0,Math.PI*2);ctx.stroke();}
        if(m.pickup){const hue=(battleTime*150)%360;ctx.globalAlpha=.48;ctx.fillStyle=`hsl(${hue} 92% 67%)`;ctx.shadowColor=`hsl(${(hue+90)%360} 95% 70%)`;ctx.shadowBlur=22;ctx.beginPath();ctx.roundRect(m.pickup.x-m.pickup.r,m.pickup.y-m.pickup.r,m.pickup.r*2,m.pickup.r*2,6);ctx.fill();ctx.globalAlpha=.9;ctx.fillStyle="#fff";ctx.font="1000 18px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("?",m.pickup.x,m.pickup.y);}
        if(tr){drawMarioPipeAt(tr.entry,tr.phase==="exit"?.34:1);if(tr.phase==="hidden"||tr.phase==="exit")drawMarioPipeAt(tr.exit,1);}
        ctx.restore();
      }
      if(tr?.phase==="hidden")return;
      const flicker=m.blink>0&&Math.floor(battleTime*18)%2===0,rainbow=`hsl(${(battleTime*180)%360} 92% 64%)`,transitScale=tr?.visualScale||1,transitAlpha=tr?.visualAlpha??1;
      ctx.save();if(flicker)ctx.globalAlpha=.28;ctx.globalAlpha*=transitAlpha;ctx.translate(f.x,f.y);ctx.scale(f.r/20*transitScale,f.r/20*transitScale);
      if(m.kart){
        const a=Math.atan2(f.vy||0,f.vx||1)+Math.PI/2;ctx.save();ctx.rotate(a);ctx.shadowColor="#0f172a";ctx.shadowBlur=6;
        ctx.fillStyle="#111827";for(const [x,y] of [[-18,-8],[18,-8],[-19,13],[19,13]]){ctx.beginPath();ctx.roundRect(x-4,y-6,8,12,3);ctx.fill();}
        ctx.fillStyle="#dc2626";ctx.strokeStyle="#fecaca";ctx.lineWidth=1.5;ctx.beginPath();ctx.roundRect(-22,-12,44,31,8);ctx.fill();ctx.stroke();ctx.fillStyle="#ef4444";ctx.beginPath();ctx.roundRect(-16,-18,32,12,5);ctx.fill();ctx.stroke();
        ctx.fillStyle="#2563eb";ctx.beginPath();ctx.roundRect(-14,4,28,15,5);ctx.fill();ctx.strokeStyle="#93c5fd";ctx.stroke();ctx.fillStyle="#facc15";ctx.fillRect(-7,-18,14,4);
        ctx.strokeStyle="#111827";ctx.lineWidth=2.4;ctx.beginPath();ctx.arc(0,-1,6,0,Math.PI*2);ctx.stroke();ctx.beginPath();ctx.moveTo(0,-1);ctx.lineTo(0,5);ctx.stroke();
        ctx.fillStyle="#475569";ctx.fillRect(-15,19,7,5);ctx.fillRect(8,19,7,5);ctx.restore();
        ctx.translate(0,-7);ctx.scale(.78,.78);
      }
      if(m.power==="star"){ctx.shadowColor=rainbow;ctx.shadowBlur=28;ctx.fillStyle=rainbow;ctx.globalAlpha*=.42;ctx.beginPath();ctx.arc(0,0,22,0,Math.PI*2);ctx.fill();ctx.globalAlpha=transitAlpha*(flicker?.28:1);}
      ctx.fillStyle=m.power==="fire"?"#fff7ed":"#ef4444";ctx.beginPath();ctx.arc(0,-5,14,0,Math.PI*2);ctx.fill();ctx.fillStyle=m.power==="fire"?"#f8fafc":"#dc2626";ctx.beginPath();ctx.arc(0,-13,15,Math.PI,0);ctx.fill();ctx.fillRect(-14,-13,28,5);
      if(m.power==="fire"){ctx.fillStyle="#dc2626";ctx.font="900 8px system-ui";ctx.textAlign="center";ctx.fillText("M",0,-12);}
      ctx.fillStyle="#fed7aa";ctx.beginPath();ctx.ellipse(0,-3,11,10,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#3f2a1d";ctx.beginPath();ctx.ellipse(0,2,8,3,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#111827";ctx.fillRect(-7,-5,3,3);ctx.fillRect(4,-5,3,3);
      ctx.fillStyle=m.power==="fire"?"#ef4444":"#2563eb";ctx.beginPath();ctx.moveTo(-12,6);ctx.lineTo(-9,19);ctx.lineTo(9,19);ctx.lineTo(12,6);ctx.closePath();ctx.fill();ctx.fillStyle="#fbbf24";ctx.beginPath();ctx.arc(-6,9,1.8,0,Math.PI*2);ctx.arc(6,9,1.8,0,Math.PI*2);ctx.fill();ctx.restore();
      if(!tr||tr.phase==="approach"){drawHealthBar(f);drawName(f);}
      if(!f.portraitOnly&&(m.power==="mushroom"||m.power==="fire")){const total=5,w=8,g=2,start=f.x-(total*w+(total-1)*g)/2;for(let i=0;i<total;i++){ctx.fillStyle=i<m.shield?(m.power==="fire"?"#f8fafc":"#ef4444"):"#374151";ctx.fillRect(start+i*(w+g),f.y-f.r-15,w,5);}}
      if(!f.portraitOnly&&m.power==="star")drawRing(f.x,f.y,f.r+6,rainbow,3);
      if(!f.portraitOnly&&m.kart&&m.heldCount>0){const col=m.heldType==="banana"?"#fde047":m.heldType==="green"?"#22c55e":"#ef4444";for(let i=0;i<m.heldCount;i++){const a=battleTime*2.4+i*Math.PI*2/m.heldCount,rr=f.r+15;ctx.fillStyle=col;ctx.strokeStyle="#f8fafc";ctx.lineWidth=1.2;ctx.beginPath();ctx.arc(f.x+Math.cos(a)*rr,f.y+Math.sin(a)*rr,5,0,Math.PI*2);ctx.fill();ctx.stroke();}}
    }
'''

sub_one(r'    const MARIO = \{.*?\n    function drawSpiderWebDecal\(w\)\{', MARIO_CODE + '\n    function drawSpiderWebDecal(w){', 'Mario implementation', re.S)

# 상태창의 Mario 블록 교체
MARIO_STATUS = r'''      if(f.mario){
        const m=f.mario;
        if(m.pipeTransit){
          const tr=m.pipeTransit,phase=tr.phase==="approach"?"토관으로 감속 이동":tr.phase==="enter"?"토관 진입":tr.phase==="hidden"?"토관 이동 중":"토관에서 등장",goal=tr.toKart?"카트 모드":"기본 모드";
          const max=tr.phaseMax||1,ratio=tr.phase==="approach"?1:clamp(1-(tr.timer||0)/max,0,1);
          return {ratio,className:"rage-fill",text:`${phase} · ${goal} 전환`,extraTextHtml:`<div class="status-skill-label">벽 접촉 50/50 · 초록 토관 이동</div><div class="status-skill-label">진입 후 무작위 벽 토관에서 ${goal}로 등장</div>`};
        }
        if(m.kart){
          const held=m.heldCount>0,pickup=!!m.pickup,ratio=held?clamp(1-Math.max(0,m.itemUseCd)/MARIO.kartItemUsePeriod,0,1):pickup?1:clamp(1-Math.max(0,m.nextBlock)/MARIO.blockDelay,0,1);
          const text=held?`배관공카트 · ${marioItemName(m.heldType)} ${m.heldCount}개 · 사용 ${Math.max(0,m.itemUseCd).toFixed(1)}초`:pickup?"배관공카트 · 랜덤 아이템 출현":`배관공카트 · 랜덤 아이템 ${Math.max(0,m.nextBlock).toFixed(1)}초`;
          return {ratio,className:"skill-fill",text,extraTextHtml:`<div class="status-skill-label">벽 접촉 ${m.wallContacts}/${MARIO.kartWallNeed} · 50회 → 토관으로 기본 모드 복귀 · 카트 이속 ×${MARIO.kartSpeedMult.toFixed(2)}</div><div class="status-skill-label">아이템 획득 시 3개 회전 · ${MARIO.kartItemUsePeriod.toFixed(1)}초마다 1개 자동 사용</div>`};
        }
        const block=fighterById(m.blockId),boxReady=!!block,boxAge=block?.marioBlock?.age||0;
        const boxRatio=boxReady?clamp(boxAge/MARIO.blockChaseDelay,0,1):clamp(1-Math.max(0,m.nextBlock)/MARIO.blockDelay,0,1);
        const boxText=boxReady?`랜덤박스 출현 · 접촉 ${block.marioBlock?.touches||0}/${MARIO.blockTouchNeed} · HP ${Math.ceil(block.hp)}/${MARIO.blockHp}`:`랜덤박스 ${Math.max(0,m.nextBlock).toFixed(1)}초`;
        const extraBar=`<div class="bar" title="랜덤박스"><div class="bar-fill skill-fill" style="width:${boxRatio*100}%"></div></div>`;
        if(m.power==="star"){
          const back=m.starReturn?.power==="fire"?"파이어배관공":m.starReturn?.power==="mushroom"?"슈퍼배관공":"기본 배관공";
          return {ratio:clamp(m.starTime/MARIO.starDuration,0,1),className:"rage-fill",text:`스타배관공 · ${Math.max(0,m.starTime).toFixed(1)}초`,extraBarsHtml:extraBar,extraTextHtml:`<div class="status-skill-label">${boxText}</div><div class="status-skill-label">종료 후 ${back} 복귀 · 벽 접촉 ${m.wallContacts}/${MARIO.kartWallNeed}</div>`};
        }
        const state=m.power==="fire"?"파이어배관공":m.power==="mushroom"?"슈퍼배관공":"기본 배관공";
        const chase=m.superStance?" · 슈퍼스탠스 직진":boxReady&&m.power==="none"?` · 직진까지 ${Math.max(0,MARIO.blockChaseDelay-boxAge).toFixed(1)}초`:"";
        const fireInfo=m.power==="fire"?` · 발사 ${(m.fireShots||0)}/${MARIO.fireShotsPerShield}`:"";
        return {ratio:boxRatio,className:m.superStance?"rage-fill":"skill-fill",text:`${state} · ${boxText}${chase}`,extraTextHtml:`<div class="status-skill-label">${m.power==="fire"||m.power==="mushroom"?`보호막 ${m.shield}/${MARIO.shieldMax}${fireInfo} · `:""}벽 접촉 ${m.wallContacts}/${MARIO.kartWallNeed} · 50회 → 토관 카트 전환</div><div class="status-skill-label">파이어 ${MARIO.firePeriod.toFixed(2)}초 간격 · 5발마다 1칸 소모 · 화상1×3 중첩 없이 갱신</div>`};
      }
'''
sub_one(r'      if\(f\.mario\)\{.*?\n      if\(f\.spider\)', MARIO_STATUS + '      if(f.spider)', 'Mario status', re.S)

# 토관 이동 중 일반 이동을 중복 적용하지 않는다.
replace_one(
    '      if (updateCastPause(f, dt)) {\n        return;\n      }\n\n      const slow = f.freeze > 0 ? 0.42 : 1;',
    '      if (updateCastPause(f, dt)) {\n        return;\n      }\n      if (f.mario?.pipeTransit) return;\n\n      const slow = f.freeze > 0 ? 0.42 : 1;',
    'pipe movement stop',
)

# 벽 충돌면을 토관 위치로 넘기고, 기본/카트 모두 50회를 센다.
replace_one('    function bounceWalls(f) {\n      let bounced = false;', '    function bounceWalls(f) {\n      let bounced = false;\n      let marioWall = null;', 'bounce header')
replace_one('        f.vx = Math.abs(f.vx);\n        bounced = true;', '        f.vx = Math.abs(f.vx);\n        bounced = true;\n        if (!marioWall) marioWall = { wall:"left", x:arena.x, y:clamp(f.y,arena.y+54,arena.y2-54) };', 'left wall')
replace_one('        f.vx = -Math.abs(f.vx);\n        bounced = true;', '        f.vx = -Math.abs(f.vx);\n        bounced = true;\n        if (!marioWall) marioWall = { wall:"right", x:arena.x2, y:clamp(f.y,arena.y+54,arena.y2-54) };', 'right wall')
replace_one('        f.vy = Math.abs(f.vy);\n        bounced = true;', '        f.vy = Math.abs(f.vy);\n        bounced = true;\n        if (!marioWall) marioWall = { wall:"top", x:clamp(f.x,arena.x+54,arena.x2-54), y:arena.y };', 'top wall')
replace_one('        f.vy = -Math.abs(f.vy);\n        bounced = true;', '        f.vy = -Math.abs(f.vy);\n        bounced = true;\n        if (!marioWall) marioWall = { wall:"bottom", x:clamp(f.x,arena.x+54,arena.x2-54), y:arena.y2 };', 'bottom wall')
replace_one('        marioWallContact(f);', '        marioWallContact(f, marioWall);', 'wall contact call')

# 토관 안/밖 이동 중에는 물리 충돌하지 않는다. 접근 단계만 충돌 가능.
replace_one('        if (!a.alive || (a.dodoVoid || 0) > 0 || a.punchHold > 0 || a.logo?.jump?.phase === "flight") continue;', '        if (!a.alive || (a.dodoVoid || 0) > 0 || a.punchHold > 0 || a.logo?.jump?.phase === "flight" || (a.mario?.pipeTransit && a.mario.pipeTransit.phase!=="approach")) continue;', 'collision a')
replace_one('          if (!b.alive || (b.dodoVoid || 0) > 0 || b.punchHold > 0 || b.logo?.jump?.phase === "flight") continue;', '          if (!b.alive || (b.dodoVoid || 0) > 0 || b.punchHold > 0 || b.logo?.jump?.phase === "flight" || (b.mario?.pipeTransit && b.mario.pipeTransit.phase!=="approach")) continue;', 'collision b')

# 카트 아이템 회전: 장식 이펙트 대신 뉴헬로처럼 캐릭터 본체를 회전시킨다.
replace_one('    function drawHealthBar(f) {\n      if (f.portraitOnly) return;', '    function drawHealthBar(f) {\n      if (suppressMarioSpinUi) return;\n      if (f.portraitOnly) return;', 'health suppress')
replace_one('    function drawName(f) {\n      if (f.portraitOnly) return;', '    function drawName(f) {\n      if (suppressMarioSpinUi) return;\n      if (f.portraitOnly) return;', 'name suppress')
replace_one(
    '    function drawFighter(f) {\n      drawConcussionSlow(f);\n      drawPowerFist(f);\n      drawIronSuit(f);\n      drawMarioSpinOverlay(f);',
    '''    let suppressMarioSpinUi = false;\n    function drawFighter(f) {\n      drawConcussionSlow(f);\n      drawPowerFist(f);\n      drawIronSuit(f);\n      const marioSpin=(f.marioSpinFx||0)>0&&!fastSimMode&&!f.portraitOnly;\n      if(marioSpin){\n        const prev=suppressMarioSpinUi;suppressMarioSpinUi=true;\n        ctx.save();ctx.translate(f.x,f.y);ctx.rotate((MARIO.shellSpin-f.marioSpinFx)*28);ctx.translate(-f.x,-f.y);drawFighterBody(f);ctx.restore();\n        suppressMarioSpinUi=prev;drawHealthBar(f);drawName(f);return;\n      }\n      drawFighterBody(f);\n    }\n    function drawFighterBody(f) {''',
    'fighter spin wrapper',
)

p.write_text(s, encoding='utf-8')
print('Mario v135 patch applied')
