from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if '<title>볼배틀 리뉴얼 v134</title>' in s:
    print('v134 already applied')
    raise SystemExit(0)

def one(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {n}')
    s = s.replace(old, new, 1)

one('<title>볼배틀 리뉴얼 v133</title>', '<title>볼배틀 리뉴얼 v134</title>', 'title')

old_char = '''      { id:"mario_plumber", name:"배관공", mark:"M", role:"게임", color:"#ef4444", hp:160, attack:8, speed:2.8, range:0,
        skillName:"? 블록 · 랜덤 파워업", condition:"기본 상태 5초 후 ?블록 · 슈퍼버섯/파이어플라워/슈퍼스타 무작위 · 상대가 블록 파괴 가능", desc:"전장에 나타난 ?블록과 접촉해 무작위 파워업을 얻는다. 버섯·파이어 상태는 5칸 피격 보호막을 얻고, 강한 한 방일수록 보호막이 더 많이 깎인다. 보호막이 깨지면 특유의 깜빡임과 함께 작아진다." },'''
new_char = '''      { id:"mario_plumber", name:"배관공", mark:"M", role:"게임", color:"#ef4444", hp:160, attack:8, speed:2.8, range:0,
        skillName:"랜덤박스 · 배관공카트", condition:"5초마다 랜덤박스 · 15초 방치 시 슈퍼스탠스 직진 · 벽 50회 접촉 시 카트 모드", desc:"랜덤박스에서 슈퍼버섯·파이어플라워·슈퍼스타를 무작위로 얻는다. 변신 중에도 새 박스가 등장한다. 벽 접촉을 50회 쌓으면 초록 배관을 거쳐 배관공카트로 전환되어 바나나·초록등껍질·빨간등껍질을 사용한다." },'''
one(old_char, new_char, 'character entry')

old_info = '''      if (c.id === "mario_plumber") return {damage:"기본 충돌8 / 파이어볼9 / 슈퍼스타 접촉12",tick:"기본 상태 5초 후 ?블록 · 블록HP24 · 파워업 무작위 · 버섯/파이어 보호막5칸 · 피격 시 ceil(피해/10)칸 차감 · 파이어볼1.25초 · 스타4초",tip:"?블록은 실제 전장 오브젝트라 상대 공격으로 파괴할 수 있다. 배관공은 별도 블록 추적 AI 없이 평소 이동 중 블록에 닿으면 획득한다. 슈퍼버섯과 파이어플라워는 피해를 HP 대신 5칸 보호막으로 받으며 1~10 피해는1칸, 11~20은2칸처럼 10을 초과할 때마다 추가 차감된다. 보호막이 깨지는 공격까지는 HP에 들어가지 않고 0.8초간 깜빡이며 작아진다. 파이어볼은 벽을 한 번 반사한다. 슈퍼스타는 4초간 무적·가속·접촉 공격 상태가 된다. 파워업 중에는 새 ?블록이 나오지 않는다."};'''
new_info = '''      if (c.id === "mario_plumber") return {damage:"랜덤박스 접촉5 / 슈퍼펀치10 / 파이어볼9+화상2×3 / 슈퍼스타 접촉12 / 카트충돌9 / 바나나4 / 초록등껍질24 / 빨간등껍질14",tick:"랜덤박스 5초 · 박스HP60 · 상대 2회 접촉 시 제거 · 15초 방치 시 슈퍼스탠스 직진 · 버섯/파이어 보호막5칸 · 파이어볼 벽2회 반사 · 스타6초 · 벽50회→배관공카트 · 카트 아이템3개·3.5초마다1개 사용",tip:"변신 상태에서도 랜덤박스는 계속 등장한다. 일반 랜덤박스는 공격으로도 피해를 받지만 파괴 연출 없이 사라지며, 상대가 몸으로 닿을 때마다 피해5를 받고 2번째 접촉에 제거된다. 이 피해는 배관공의 가한 피해로 기록된다. 기본 배관공이 박스를 15초 동안 못 먹으면 슈퍼스탠스로 박스를 향해 직진한다. 슈퍼버섯은 접촉 펀치와 넉백, 파이어플라워는 흰 모자·2회 벽반사·화상, 슈퍼스타는 6초 무적과 무지개 발광을 얻는다. 벽50회 후 카트 모드에서는 통과형 무지개 랜덤아이템에서 아이템3개를 얻고 자동 사용한다."};'''
one(old_info, new_info, 'damage info')

MARIO_CODE = r'''    const MARIO = {
      blockDelay:5, blockHp:60, blockTouchDamage:5, blockTouchNeed:2, blockChaseDelay:15,
      shieldMax:5, blinkTime:.8,
      fireDamage:9, firePeriod:1.25, fireSpeed:320, fireLife:3.2, fireBounces:2,
      fireBurnDamage:2, fireBurnTicks:3, fireBurnTick:.6,
      starDuration:6, starSpeedMult:1.55, starDamage:12, starContactCd:.35,
      superPunchDamage:10, superPunchKnock:260, superPunchCd:.70,
      kartWallNeed:50, kartSpeedMult:1.35, kartContactDamage:9, kartContactKnock:250, kartContactCd:.55,
      kartItemCount:3, kartItemUsePeriod:3.5,
      bananaDamage:4, bananaSlow:2.4, bananaSlowMult:.55, bananaR:9,
      greenDamage:24, greenSpeed:330, greenR:8,
      redDamage:14, redSpeed:290, redTurn:6.5, redR:8,
      shellSpin:.9
    };
    function initMario(f){
      f.mario={
        power:"none",shield:0,blockId:null,nextBlock:MARIO.blockDelay,blink:0,fireCd:0,fireballs:[],starTime:0,starHits:{},
        baseR:f.r||20,baseSpeed:f.baseSpeed||f.speed||2.8,superStance:false,punchCd:0,wallContacts:0,
        kart:false,pipeFx:0,kartContactCd:0,pickup:null,heldType:"",heldCount:0,itemUseCd:0,bananas:[],shells:[]
      };
    }
    function marioSetMotionSpeed(f,mult=1){
      const m=f.mario;if(!m)return;const speed=m.baseSpeed*mult;f.speed=speed;f.baseSpeed=speed;
      const mag=Math.hypot(f.vx,f.vy),a=mag>.01?Math.atan2(f.vy,f.vx):rand(0,Math.PI*2),v=speed*44;
      f.vx=Math.cos(a)*v;f.vy=Math.sin(a)*v;
    }
    function marioResetPower(f,blink=false){
      const m=f?.mario;if(!m)return;m.power="none";m.shield=0;m.starTime=0;m.fireCd=0;m.fireballs=[];m.starHits={};m.superStance=false;f.r=m.baseR;
      marioSetMotionSpeed(f,m.kart?MARIO.kartSpeedMult:1);if(blink)m.blink=Math.max(m.blink,MARIO.blinkTime);
    }
    function marioSpawnBlock(f){
      const m=f?.mario;if(!m||m.kart||m.blockId)return;
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
    function marioApplyPower(f,kind){
      const m=f.mario;m.blink=0;m.fireballs=[];m.starHits={};m.superStance=false;
      if(kind==="star"){
        m.power="star";m.shield=0;m.starTime=MARIO.starDuration;f.r=m.baseR*1.08;marioSetMotionSpeed(f,MARIO.starSpeedMult);
        spawnFloatingText(f.x,f.y-f.r-28,"스타배관공!","#fde047");spawnBlast(f.x,f.y,64,"#fde047");return;
      }
      m.power=kind;m.shield=MARIO.shieldMax;m.starTime=0;f.r=m.baseR*1.18;marioSetMotionSpeed(f,1);
      if(kind==="fire"){m.fireCd=.25;spawnFloatingText(f.x,f.y-f.r-28,"파이어배관공!","#f8fafc");spawnBlast(f.x,f.y,54,"#fb923c");}
      else {spawnFloatingText(f.x,f.y-f.r-28,"슈퍼배관공!","#fca5a5");spawnBlast(f.x,f.y,54,"#ef4444");}
    }
    function marioCollectBlock(f,b){
      if(!f?.mario||f.mario.kart||!b?.alive||!b.marioBlock)return;b.alive=false;f.mario.blockId=null;f.mario.nextBlock=MARIO.blockDelay;
      const roll=Math.floor(Math.random()*3),kind=roll===0?"mushroom":roll===1?"fire":"star";marioApplyPower(f,kind);
    }
    function marioAbsorbDamage(f,amount,source,reason){
      const m=f?.mario;if(!m||amount<=0)return null;
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
      const m=f.mario,target=nearestEnemy(f).enemy;if(!target)return;const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1;
      m.fireballs.push({x:f.x+dx/d*(f.r+7),y:f.y+dy/d*(f.r+7),vx:dx/d*MARIO.fireSpeed,vy:dy/d*MARIO.fireSpeed,r:6,life:MARIO.fireLife,bounces:MARIO.fireBounces});
      if(!fastSimMode)spawnParticles(f.x+dx/d*f.r,f.y+dy/d*f.r,"#fb923c",5);
    }
    function updateMarioFireballs(f,dt){
      const m=f.mario;
      for(let i=m.fireballs.length-1;i>=0;i--){const p=m.fireballs[i],ox=p.x,oy=p.y;p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt;let wall=false;
        if(p.x-p.r<=arena.x||p.x+p.r>=arena.x2){p.x=clamp(p.x,arena.x+p.r,arena.x2-p.r);p.vx*=-1;wall=true;}
        if(p.y-p.r<=arena.y||p.y+p.r>=arena.y2){p.y=clamp(p.y,arena.y+p.r,arena.y2-p.r);p.vy*=-1;wall=true;}
        if(wall){if(p.bounces>0)p.bounces--;else{m.fireballs.splice(i,1);continue;}}
        let hit=null,best=1;
        for(const e of enemiesOf(f)){if(!e.alive||e.tano?.hidden>0||e.marioBlock)continue;const h=spiderSegHit(ox,oy,p.x,p.y,e.x,e.y,e.r+p.r);if(h!==null&&h<best){best=h;hit=e;}}
        if(hit){const dealt=damage(hit,MARIO.fireDamage,f,"파이어볼");if(dealt>0&&hit.alive&&!hasHarmfulImmunity(hit)){hit.burningTicks ||= [];hit.burningTicks.push({t:MARIO.fireBurnTick*MARIO.fireBurnTicks+.05,next:MARIO.fireBurnTick,power:MARIO.fireBurnDamage,source:f,tick:MARIO.fireBurnTick,ticksLeft:MARIO.fireBurnTicks});}if(!fastSimMode)spawnHitFlash(hit.x,hit.y,"#fb923c",45);m.fireballs.splice(i,1);continue;}
        if(p.life<=0)m.fireballs.splice(i,1);
      }
    }
    function marioSuperPunchContact(f,target){
      const m=f?.mario;if(!m||m.kart||m.power!=="mushroom"||m.punchCd>0||!target?.alive||!areEnemies(f,target))return false;
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
      const options=[
        {wall:"left",d:f.x-arena.x},{wall:"right",d:arena.x2-f.x},{wall:"top",d:f.y-arena.y},{wall:"bottom",d:arena.y2-f.y}
      ],mx=Math.max(...options.map(o=>o.d)),choices=options.filter(o=>Math.abs(o.d-mx)<1.5),pick=choices[Math.floor(Math.random()*choices.length)],pad=24;
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
      const m=f.mario;if(!m.kart||m.pickup)return;const r=14;m.pickup={x:rand(arena.x+r+8,arena.x2-r-8),y:rand(arena.y+r+8,arena.y2-r-8),r};m.nextBlock=MARIO.blockDelay;
      if(!fastSimMode)spawnFloatingText(m.pickup.x,m.pickup.y-r-10,"랜덤 아이템","#e9d5ff");
    }
    function marioUseKartItem(f){
      const m=f.mario;if(!m.kart||m.heldCount<=0||!m.heldType)return false;const type=m.heldType;
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
    function enterMarioKart(f){
      const m=f?.mario;if(!m||m.kart)return;if(m.blockId){const b=fighterById(m.blockId);if(b)b.alive=false;}m.blockId=null;marioResetPower(f,false);m.kart=true;m.wallContacts=MARIO.kartWallNeed;m.pipeFx=1.25;m.pickup=null;m.nextBlock=MARIO.blockDelay;m.heldType="";m.heldCount=0;m.itemUseCd=0;m.bananas=[];m.shells=[];marioSetMotionSpeed(f,MARIO.kartSpeedMult);
      spawnFloatingText(f.x,f.y-f.r-44,"초록 배관 → 배관공카트!","#4ade80");if(!fastSimMode){spawnParticles(f.x,f.y,"#22c55e",24);playSound("warp",1);}
    }
    function marioWallContact(f){const m=f?.mario;if(!m||m.kart)return;m.wallContacts=Math.min(MARIO.kartWallNeed,m.wallContacts+1);if(m.wallContacts>=MARIO.kartWallNeed)enterMarioKart(f);}
    function marioKartContact(f,target){
      const m=f?.mario;if(!m?.kart||m.kartContactCd>0||!target?.alive||!areEnemies(f,target))return false;const dx=target.x-f.x,dy=target.y-f.y,d=Math.hypot(dx,dy)||1,dealt=damage(target,MARIO.kartContactDamage,f,"카트충돌");if(dealt>0&&target.alive){target.vx+=dx/d*MARIO.kartContactKnock;target.vy+=dy/d*MARIO.kartContactKnock;}m.kartContactCd=MARIO.kartContactCd;if(!fastSimMode)spawnHitFlash(target.x,target.y,"#60a5fa",42);return true;
    }
    function updateMario(f,dt){
      const m=f?.mario;if(!m||!f.alive)return;m.blink=Math.max(0,m.blink-dt);m.punchCd=Math.max(0,m.punchCd-dt);m.kartContactCd=Math.max(0,m.kartContactCd-dt);m.pipeFx=Math.max(0,m.pipeFx-dt);updateMarioFireballs(f,dt);
      if(m.kart){m.superStance=false;updateMarioKartPickup(f,dt);updateMarioKartHazards(f,dt);return;}
      if(m.blockId){const b=fighterById(m.blockId);if(!b||!b.alive){m.blockId=null;m.superStance=false;m.nextBlock=MARIO.blockDelay;}else if(Math.hypot(f.x-b.x,f.y-b.y)<=f.r+b.r+3){marioCollectBlock(f,b);}else if(m.power==="none"&&(b.marioBlock?.age||0)>=MARIO.blockChaseDelay){m.superStance=true;const dx=b.x-f.x,dy=b.y-f.y,d=Math.hypot(dx,dy)||1,v=m.baseSpeed*44;f.vx=dx/d*v;f.vy=dy/d*v;}else m.superStance=false;
      }else{m.superStance=false;m.nextBlock=Math.max(0,m.nextBlock-dt);if(m.nextBlock<=0)marioSpawnBlock(f);}
      if(m.power==="star"){
        m.starTime-=dt;for(const id of Object.keys(m.starHits))m.starHits[id]=Math.max(0,m.starHits[id]-dt);
        for(const e of enemiesOf(f)){if(!e.alive||e.marioBlock||Math.hypot(e.x-f.x,e.y-f.y)>f.r+e.r+3||(m.starHits[e.id]||0)>0)continue;const dx=e.x-f.x,dy=e.y-f.y,d=Math.hypot(dx,dy)||1;damage(e,MARIO.starDamage,f,"슈퍼스타");e.vx+=dx/d*220;e.vy+=dy/d*220;m.starHits[e.id]=MARIO.starContactCd;if(!fastSimMode)spawnHitFlash(e.x,e.y,`hsl(${(battleTime*180)%360} 90% 65%)`,58);}
        if(m.starTime<=0)marioResetPower(f,false);return;
      }
      if(m.power==="fire"){m.fireCd-=dt;if(m.fireCd<=0){marioFire(f);m.fireCd+=MARIO.firePeriod;}}
    }
    function drawMarioBlock(f){
      ctx.save();ctx.translate(f.x,f.y);ctx.fillStyle="#fbbf24";ctx.strokeStyle="#92400e";ctx.lineWidth=3;ctx.fillRect(-f.r,-f.r,f.r*2,f.r*2);ctx.strokeRect(-f.r,-f.r,f.r*2,f.r*2);ctx.fillStyle="#fff7ed";ctx.font="1000 22px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("?",0,1);ctx.restore();drawHealthBar(f);
    }
    function drawMarioSpinOverlay(f){
      const t=f.marioSpinFx||0;if(t<=0||fastSimMode)return;ctx.save();ctx.translate(f.x,f.y);ctx.rotate(battleTime*12);ctx.globalAlpha=clamp(t/.9,.25,1);ctx.strokeStyle="#fde047";ctx.lineWidth=2.2;for(let i=0;i<3;i++){ctx.beginPath();ctx.arc(0,0,f.r+7+i*5,i*1.7,i*1.7+1.15);ctx.stroke();}ctx.fillStyle="#fff7ae";for(let i=0;i<4;i++){const a=i*Math.PI/2,r=f.r+14;ctx.fillText("✦",Math.cos(a)*r,Math.sin(a)*r);}ctx.restore();
    }
    function drawMarioCharacter(f){
      const m=f.mario||{power:"none",shield:0,blink:0,fireballs:[],bananas:[],shells:[]};
      if(!f.portraitOnly&&!fastSimMode){ctx.save();ctx.beginPath();ctx.rect(arena.x,arena.y,arena.size,arena.size);ctx.clip();
        for(const p of m.fireballs||[]){ctx.shadowColor="#fb923c";ctx.shadowBlur=12;ctx.fillStyle="#f97316";ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fde68a";ctx.beginPath();ctx.arc(p.x-2,p.y-2,p.r*.45,0,Math.PI*2);ctx.fill();}
        for(const b of m.bananas||[]){ctx.fillStyle="#fde047";ctx.strokeStyle="#a16207";ctx.lineWidth=1.5;ctx.beginPath();ctx.moveTo(b.x-8,b.y-5);ctx.quadraticCurveTo(b.x,b.y+10,b.x+8,b.y-5);ctx.quadraticCurveTo(b.x,b.y+3,b.x-8,b.y-5);ctx.fill();ctx.stroke();}
        for(const sh of m.shells||[]){ctx.fillStyle=sh.kind==="green"?"#22c55e":"#ef4444";ctx.strokeStyle="#f8fafc";ctx.lineWidth=1.5;ctx.beginPath();ctx.arc(sh.x,sh.y,sh.r,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.strokeStyle="#14532d";ctx.beginPath();ctx.arc(sh.x,sh.y,sh.r*.55,0,Math.PI*2);ctx.stroke();}
        if(m.pickup){const hue=(battleTime*150)%360;ctx.globalAlpha=.48;ctx.fillStyle=`hsl(${hue} 92% 67%)`;ctx.shadowColor=`hsl(${(hue+90)%360} 95% 70%)`;ctx.shadowBlur=22;ctx.beginPath();ctx.roundRect(m.pickup.x-m.pickup.r,m.pickup.y-m.pickup.r,m.pickup.r*2,m.pickup.r*2,6);ctx.fill();ctx.globalAlpha=.9;ctx.fillStyle="#fff";ctx.font="1000 18px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("?",m.pickup.x,m.pickup.y);}
        ctx.restore();
      }
      const flicker=m.blink>0&&Math.floor(battleTime*18)%2===0,rainbow=`hsl(${(battleTime*180)%360} 92% 64%)`;ctx.save();if(flicker)ctx.globalAlpha=.28;ctx.translate(f.x,f.y);ctx.scale(f.r/20,f.r/20);
      if(m.pipeFx>0){const a=clamp(m.pipeFx/1.25,0,1);ctx.globalAlpha=.35+.55*a;ctx.fillStyle="#16a34a";ctx.strokeStyle="#86efac";ctx.lineWidth=2;ctx.fillRect(-24,-2,48,28);ctx.strokeRect(-24,-2,48,28);ctx.fillStyle="#22c55e";ctx.fillRect(-28,-8,56,10);ctx.strokeRect(-28,-8,56,10);ctx.globalAlpha=1;}
      if(m.kart){ctx.fillStyle="#111827";ctx.beginPath();ctx.arc(-15,17,6,0,Math.PI*2);ctx.arc(15,17,6,0,Math.PI*2);ctx.fill();ctx.fillStyle="#2563eb";ctx.strokeStyle="#93c5fd";ctx.lineWidth=1.5;ctx.beginPath();ctx.roundRect(-19,8,38,13,6);ctx.fill();ctx.stroke();ctx.fillStyle="#facc15";ctx.fillRect(-4,16,8,4);}
      if(m.power==="star"){ctx.shadowColor=rainbow;ctx.shadowBlur=28;ctx.fillStyle=rainbow;ctx.globalAlpha=.42;ctx.beginPath();ctx.arc(0,0,22,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;}
      ctx.fillStyle=m.power==="fire"?"#fff7ed":"#ef4444";ctx.beginPath();ctx.arc(0,-5,14,0,Math.PI*2);ctx.fill();ctx.fillStyle=m.power==="fire"?"#f8fafc":"#dc2626";ctx.beginPath();ctx.arc(0,-13,15,Math.PI,0);ctx.fill();ctx.fillRect(-14,-13,28,5);
      if(m.power==="fire"){ctx.fillStyle="#dc2626";ctx.font="900 8px system-ui";ctx.textAlign="center";ctx.fillText("M",0,-12);}
      ctx.fillStyle="#fed7aa";ctx.beginPath();ctx.ellipse(0,-3,11,10,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#3f2a1d";ctx.beginPath();ctx.ellipse(0,2,8,3,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#111827";ctx.fillRect(-7,-5,3,3);ctx.fillRect(4,-5,3,3);
      ctx.fillStyle=m.power==="fire"?"#ef4444":"#2563eb";ctx.beginPath();ctx.moveTo(-12,6);ctx.lineTo(-9,19);ctx.lineTo(9,19);ctx.lineTo(12,6);ctx.closePath();ctx.fill();ctx.fillStyle="#fbbf24";ctx.beginPath();ctx.arc(-6,9,1.8,0,Math.PI*2);ctx.arc(6,9,1.8,0,Math.PI*2);ctx.fill();ctx.restore();drawHealthBar(f);drawName(f);
      if(!f.portraitOnly&&(m.power==="mushroom"||m.power==="fire")){const total=5,w=8,g=2,start=f.x-(total*w+(total-1)*g)/2;for(let i=0;i<total;i++){ctx.fillStyle=i<m.shield?(m.power==="fire"?"#f8fafc":"#ef4444"):"#374151";ctx.fillRect(start+i*(w+g),f.y-f.r-15,w,5);}}
      if(!f.portraitOnly&&m.power==="star")drawRing(f.x,f.y,f.r+6,rainbow,3);
      if(!f.portraitOnly&&m.kart&&m.heldCount>0){const col=m.heldType==="banana"?"#fde047":m.heldType==="green"?"#22c55e":"#ef4444";for(let i=0;i<m.heldCount;i++){const a=battleTime*2.4+i*Math.PI*2/m.heldCount,rr=f.r+15;ctx.fillStyle=col;ctx.strokeStyle="#f8fafc";ctx.lineWidth=1.2;ctx.beginPath();ctx.arc(f.x+Math.cos(a)*rr,f.y+Math.sin(a)*rr,5,0,Math.PI*2);ctx.fill();ctx.stroke();}}
    }
'''

pattern = r'    const MARIO = \{.*?\n    function drawSpiderWebDecal\(w\)\{'
s, n = re.subn(pattern, MARIO_CODE + '\n    function drawSpiderWebDecal(w){', s, count=1, flags=re.S)
if n != 1:
    raise SystemExit(f'Mario code block: expected 1, found {n}')

status_anchor = '    function skillProgressInfo(f) {\n'
status_branch = r'''      if(f.mario){
        const m=f.mario;
        if(m.kart){
          const held=m.heldCount>0, pickup=!!m.pickup, ratio=held?clamp(1-Math.max(0,m.itemUseCd)/MARIO.kartItemUsePeriod,0,1):pickup?1:clamp(1-Math.max(0,m.nextBlock)/MARIO.blockDelay,0,1);
          const text=held?`배관공카트 · ${marioItemName(m.heldType)} ${m.heldCount}개 · 사용 ${Math.max(0,m.itemUseCd).toFixed(1)}초`:pickup?"배관공카트 · 랜덤 아이템 출현":`배관공카트 · 랜덤 아이템 ${Math.max(0,m.nextBlock).toFixed(1)}초`;
          return {ratio,className:"skill-fill",text,extraTextHtml:`<div class="status-skill-label">벽 접촉 ${m.wallContacts}/${MARIO.kartWallNeed} · 카트 이속 ×${MARIO.kartSpeedMult.toFixed(2)} · 충돌${MARIO.kartContactDamage}+넉백</div><div class="status-skill-label">아이템 획득 시 3개 회전 · ${MARIO.kartItemUsePeriod.toFixed(1)}초마다 1개 자동 사용 · 보유 중 새 랜덤아이템은 소멸만</div>`};
        }
        const block=fighterById(m.blockId), boxReady=!!block, boxAge=block?.marioBlock?.age||0;
        const boxRatio=boxReady?clamp(boxAge/MARIO.blockChaseDelay,0,1):clamp(1-Math.max(0,m.nextBlock)/MARIO.blockDelay,0,1);
        const boxText=boxReady?`랜덤박스 출현 · 접촉 ${block.marioBlock?.touches||0}/${MARIO.blockTouchNeed} · HP ${Math.ceil(block.hp)}/${MARIO.blockHp}`:`랜덤박스 ${Math.max(0,m.nextBlock).toFixed(1)}초`;
        const extraBar=`<div class="bar" title="랜덤박스"><div class="bar-fill skill-fill" style="width:${boxRatio*100}%"></div></div>`;
        if(m.power==="star")return {ratio:clamp(m.starTime/MARIO.starDuration,0,1),className:"rage-fill",text:`스타배관공 · ${Math.max(0,m.starTime).toFixed(1)}초`,extraBarsHtml:extraBar,extraTextHtml:`<div class="status-skill-label">${boxText}</div><div class="status-skill-label">벽 접촉 ${m.wallContacts}/${MARIO.kartWallNeed} · 스타 종료 전까지 무적·가속·접촉12</div>`};
        const state=m.power==="fire"?"파이어배관공":m.power==="mushroom"?"슈퍼배관공":"기본 배관공";
        const chase=m.superStance?" · 슈퍼스탠스 직진":boxReady&&m.power==="none"?` · 직진까지 ${Math.max(0,MARIO.blockChaseDelay-boxAge).toFixed(1)}초`:"";
        return {ratio:boxRatio,className:m.superStance?"rage-fill":"skill-fill",text:`${state} · ${boxText}${chase}`,extraTextHtml:`<div class="status-skill-label">${m.power==="fire"||m.power==="mushroom"?`보호막 ${m.shield}/${MARIO.shieldMax} · `:""}벽 접촉 ${m.wallContacts}/${MARIO.kartWallNeed}</div><div class="status-skill-label">박스는 변신 중에도 등장 · 기본 상태에서 15초 방치 시 슈퍼스탠스 직진</div>`};
      }
'''
one(status_anchor, status_anchor + status_branch, 'skill progress')

old_block_update = '      if (f.marioBlock) { f.x=f.marioBlock.anchorX; f.y=f.marioBlock.anchorY; f.vx=0; f.vy=0; return; }'
new_block_update = '      if (f.marioBlock) { f.marioBlock.age=(f.marioBlock.age||0)+dt; f.contactCd=Math.max(0,(f.contactCd||0)-dt); f.x=f.marioBlock.anchorX; f.y=f.marioBlock.anchorY; f.vx=0; f.vy=0; return; }'
one(old_block_update, new_block_update, 'block updater')

old_stun = '      f.stun = Math.max(0, (f.stun || 0) - dt);'
new_stun = '      f.stun = Math.max(0, (f.stun || 0) - dt);\n      f.marioSpinFx = Math.max(0, (f.marioSpinFx || 0) - dt);\n      f.marioItemSlow = Math.max(0, (f.marioItemSlow || 0) - dt);'
one(old_stun, new_stun, 'Mario item timers')

old_slow = '      const timedCcSlow = timedCcSlowMultiplier(f);\n      const boost = f.baseId === "wind_rio" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);'
new_slow = '      const timedCcSlow = timedCcSlowMultiplier(f);\n      const marioItemSlow = (f.marioItemSlow || 0) > 0 ? MARIO.bananaSlowMult : 1;\n      const boost = f.baseId === "wind_rio" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);'
one(old_slow, new_slow, 'Mario slow multiplier')

one('      if (f.newhello && moveNewhello(f, dt, slow * boost * gardenSlow * irisGlassSlow * songAndConcussionSlow * coldAuraSlow)) return;',
    '      if (f.newhello && moveNewhello(f, dt, slow * boost * gardenSlow * irisGlassSlow * songAndConcussionSlow * coldAuraSlow * marioItemSlow)) return;', 'newhello slow')
one('      f.x += f.vx * slow * boost * gardenSlow * irisGlassSlow * songAndConcussionSlow * coldAuraSlow * dt;\n      f.y += f.vy * slow * boost * gardenSlow * irisGlassSlow * songAndConcussionSlow * coldAuraSlow * dt;',
    '      f.x += f.vx * slow * boost * gardenSlow * irisGlassSlow * songAndConcussionSlow * coldAuraSlow * marioItemSlow * dt;\n      f.y += f.vy * slow * boost * gardenSlow * irisGlassSlow * songAndConcussionSlow * coldAuraSlow * marioItemSlow * dt;', 'movement slow')

one('        f.wallBounces += 1;\n        baldCapeWallBounce(f);', '        f.wallBounces += 1;\n        marioWallContact(f);\n        baldCapeWallBounce(f);', 'wall count')

one('    function handleSummonContact(summon, target) {\n      if (!summon || !target || !summon.alive || !target.alive) return false;',
    '    function handleSummonContact(summon, target) {\n      if (!summon || !target || !summon.alive || !target.alive) return false;\n      if (summon.marioBlock) return false;', 'summon contact')

old_cast = '''            const aCasting = isCasting(a) || !!a.baldCape?.combo || !!a.baldCape?.serious?.timer || (a.hardFreeze||0)>0;
            const bCasting = isCasting(b) || !!b.baldCape?.combo || !!b.baldCape?.serious?.timer || (b.hardFreeze||0)>0;'''
new_cast = '''            const aCasting = isCasting(a) || !!a.baldCape?.combo || !!a.baldCape?.serious?.timer || (a.hardFreeze||0)>0 || !!a.mario?.superStance;
            const bCasting = isCasting(b) || !!b.baldCape?.combo || !!b.baldCape?.serious?.timer || (b.hardFreeze||0)>0 || !!b.mario?.superStance;'''
one(old_cast, new_cast, 'super stance collision')

collision_anchor = '''            if (areEnemies(a, b)) {
              newhelloContact(a, b);'''
collision_new = '''            if (areEnemies(a, b)) {
              marioBlockEnemyContact(a, b);
              marioBlockEnemyContact(b, a);
              if (!a.alive || !b.alive) continue;
              marioSuperPunchContact(a, b);
              marioSuperPunchContact(b, a);
              marioKartContact(a, b);
              marioKartContact(b, a);
              newhelloContact(a, b);'''
one(collision_anchor, collision_new, 'Mario contacts')

old_damage_guard = '''    function damage(target, amount, source, reason = "공격") {
      if (!target || !target.alive || (target.dodoVoid || 0) > 0 || target.tano?.hidden > 0) return 0;'''
new_damage_guard = '''    function damage(target, amount, source, reason = "공격") {
      if (!target || !target.alive || (target.dodoVoid || 0) > 0 || target.tano?.hidden > 0) return 0;
      if (target.marioBlock) return damageMarioBlock(target, amount, source, reason);'''
one(old_damage_guard, new_damage_guard, 'damage block intercept')

old_body_guard = '''      if (!target || !target.alive || (target.tano?.hidden > 0 && reason !== "스톤 소실")) return 0;
      if (target.riddle?.horcruxActive) return damageRiddleHorcrux(target, amount, source, reason);'''
new_body_guard = '''      if (!target || !target.alive || (target.tano?.hidden > 0 && reason !== "스톤 소실")) return 0;
      if (target.marioBlock) return damageMarioBlock(target, amount, source, reason);
      if (target.riddle?.horcruxActive) return damageRiddleHorcrux(target, amount, source, reason);'''
one(old_body_guard, new_body_guard, 'body block intercept')

old_clear = '''      if (target.tano) target.tano.drops.length = 0;
      captainShields = captainShields.filter(o => o.owner !== target);'''
new_clear = '''      if (target.tano) target.tano.drops.length = 0;
      if (target.mario) { const b=fighterById(target.mario.blockId); if(b)b.alive=false; target.mario.blockId=null; target.mario.pickup=null; target.mario.fireballs=[]; target.mario.bananas=[]; target.mario.shells=[]; }
      captainShields = captainShields.filter(o => o.owner !== target);'''
one(old_clear, new_clear, 'death cleanup')

one('      drawIronSuit(f);\n      if (f.duelMonster) { drawDuelMonster(f); return; }',
    '      drawIronSuit(f);\n      drawMarioSpinOverlay(f);\n      if (f.duelMonster) { drawDuelMonster(f); return; }', 'spin overlay')

p.write_text(s, encoding='utf-8')
print('Mario v134 patch applied')
