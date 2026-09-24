from pathlib import Path

p = Path('index.html')
s = p.read_text(encoding='utf-8')

if 'id:"mario_plumber"' in s or 'id: "mario_plumber"' in s:
    print('already patched')
    raise SystemExit(0)

def one(old, new, label):
    global s
    n = s.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {n}')
    s = s.replace(old, new, 1)

one('const roleLabels = ["전체", "영화", "애니"];', 'const roleLabels = ["전체", "영화", "애니", "게임"];', 'roleLabels')

DUMMY = '''      { id: "dummy_unit", name: "훈련용 더미", mark: "木", role: "더미", color: "#9ca3af", hp: 500, attack: 0, speed: 2.35, range: 0, simOnly: true,
        skillName: "공격 없음", condition: "이동만 함 / 무한 부활", desc: "HP 500. 피해를 받고 사망하면 체력 500으로 부활." }'''
MARIO_CHAR = '''      { id:"mario_plumber", name:"배관공", mark:"M", role:"게임", color:"#ef4444", hp:160, attack:8, speed:2.8, range:0,
        skillName:"? 블록 · 랜덤 파워업", condition:"기본 상태 5초 후 ?블록 · 슈퍼버섯/파이어플라워/슈퍼스타 무작위 · 상대가 블록 파괴 가능", desc:"전장에 나타난 ?블록과 접촉해 무작위 파워업을 얻는다. 버섯·파이어 상태는 5칸 피격 보호막을 얻고, 강한 한 방일수록 보호막이 더 많이 깎인다. 보호막이 깨지면 특유의 깜빡임과 함께 작아진다." },
'''
one(DUMMY, MARIO_CHAR + DUMMY, 'character')

SPIDER_INFO = '''      if (c.id === "spider_man") return {damage:"웹슈터2×6 / 속박 연계 웹스윙 근접타격18",tick:"웹슈터5초마다6발(0.09초 간격) · 웹슈터 넉백 판정0.22초 · 그동안 벽충돌 시 속박0.9초→웹스윙 돌진",tip:"5초마다 웹슈터를 6연사한다. 각 탄은 피해2·약한 넉백·0.9초 10% 둔화를 준다. 웹슈터에 맞아 밀려나는 0.22초 안에 실제로 벽에 충돌한 경우에만 0.9초 속박되며, 예전에 맞은 뒤 한참 후 벽에 닿는 것은 속박되지 않는다. 속박 성공 시 해당 상대에게만 웹스윙 돌진을 사용해 근접타격18과 강한 넉백을 준다. 웹스윙 넉백으로 벽에 충돌해도 추가 피해는 없다. 자동·랜덤 웹스윙과 벽 부채꼴 연쇄 스윙은 없다."};'''
MARIO_INFO = '''
      if (c.id === "mario_plumber") return {damage:"기본 충돌8 / 파이어볼9 / 슈퍼스타 접촉12",tick:"기본 상태 5초 후 ?블록 · 블록HP24 · 파워업 무작위 · 버섯/파이어 보호막5칸 · 피격 시 ceil(피해/10)칸 차감 · 파이어볼1.25초 · 스타4초",tip:"?블록은 실제 전장 오브젝트라 상대 공격으로 파괴할 수 있다. 배관공은 별도 블록 추적 AI 없이 평소 이동 중 블록에 닿으면 획득한다. 슈퍼버섯과 파이어플라워는 피해를 HP 대신 5칸 보호막으로 받으며 1~10 피해는1칸, 11~20은2칸처럼 10을 초과할 때마다 추가 차감된다. 보호막이 깨지는 공격까지는 HP에 들어가지 않고 0.8초간 깜빡이며 작아진다. 파이어볼은 벽을 한 번 반사한다. 슈퍼스타는 4초간 무적·가속·접촉 공격 상태가 된다. 파워업 중에는 새 ?블록이 나오지 않는다."};'''
one(SPIDER_INFO, SPIDER_INFO + MARIO_INFO, 'info')

ANCHOR = '    function drawSpiderWebDecal(w){'
MARIO_CODE = r'''    const MARIO = {
      blockDelay:5, blockHp:24, shieldMax:5, blinkTime:.8,
      fireDamage:9, firePeriod:1.25, fireSpeed:320, fireLife:2.6,
      starDuration:4, starSpeedMult:1.55, starDamage:12, starContactCd:.35
    };
    function initMario(f){
      f.mario={power:"none",shield:0,blockId:null,nextBlock:MARIO.blockDelay,blink:0,fireCd:0,fireballs:[],starTime:0,starHits:{},baseR:f.r||20,baseSpeed:f.baseSpeed||f.speed||2.8};
    }
    function marioSetMotionSpeed(f,mult=1){
      const m=f.mario;if(!m)return;const speed=m.baseSpeed*mult;f.speed=speed;f.baseSpeed=speed;
      const mag=Math.hypot(f.vx,f.vy),a=mag>.01?Math.atan2(f.vy,f.vx):rand(0,Math.PI*2),v=speed*44;
      f.vx=Math.cos(a)*v;f.vy=Math.sin(a)*v;
    }
    function marioResetPower(f,blink=false){
      const m=f?.mario;if(!m)return;m.power="none";m.shield=0;m.starTime=0;m.fireCd=0;m.fireballs=[];m.starHits={};f.r=m.baseR;
      marioSetMotionSpeed(f,1);if(blink)m.blink=Math.max(m.blink,MARIO.blinkTime);m.nextBlock=MARIO.blockDelay;
    }
    function marioSpawnBlock(f){
      const m=f?.mario;if(!m||m.power!=="none"||m.blockId)return;
      const r=16,x=rand(arena.x+r+8,arena.x2-r-8),y=rand(arena.y+r+8,arena.y2-r-8);
      const spec={id:"mario_question_block",name:"? 블록",mark:"?",role:"오브젝트",color:"#fbbf24",hp:MARIO.blockHp,attack:0,speed:0,range:0,skillName:"파워업",condition:""};
      const b=makeFighter(spec,{x,y},fighterSerial++,f.id,f.teamId||null);b.r=r;b.vx=0;b.vy=0;b.speed=0;b.baseSpeed=0;b.marioBlock={ownerId:f.id,anchorX:x,anchorY:y};b.isSummon=true;fighters.push(b);m.blockId=b.id;
      spawnBlast(x,y,42,"#fbbf24");spawnFloatingText(x,y-r-12,"? 블록","#fde68a");
    }
    function marioApplyPower(f,kind){
      const m=f.mario;m.blockId=null;m.nextBlock=MARIO.blockDelay;m.blink=0;m.fireballs=[];m.starHits={};
      if(kind==="star"){
        m.power="star";m.shield=0;m.starTime=MARIO.starDuration;f.r=m.baseR*1.08;marioSetMotionSpeed(f,MARIO.starSpeedMult);
        spawnFloatingText(f.x,f.y-f.r-28,"슈퍼스타!","#fde047");spawnBlast(f.x,f.y,64,"#fde047");return;
      }
      m.power=kind;m.shield=MARIO.shieldMax;m.starTime=0;f.r=m.baseR*1.18;marioSetMotionSpeed(f,1);
      if(kind==="fire"){m.fireCd=.25;spawnFloatingText(f.x,f.y-f.r-28,"파이어플라워!","#fb923c");spawnBlast(f.x,f.y,54,"#fb923c");}
      else {spawnFloatingText(f.x,f.y-f.r-28,"슈퍼버섯!","#fca5a5");spawnBlast(f.x,f.y,54,"#ef4444");}
    }
    function marioCollectBlock(f,b){
      if(!f?.mario||!b?.alive||!b.marioBlock)return;b.alive=false;const roll=Math.floor(Math.random()*3),kind=roll===0?"mushroom":roll===1?"fire":"star";marioApplyPower(f,kind);
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
      m.fireballs.push({x:f.x+dx/d*(f.r+7),y:f.y+dy/d*(f.r+7),vx:dx/d*MARIO.fireSpeed,vy:dy/d*MARIO.fireSpeed,r:6,life:MARIO.fireLife,bounces:1});
      if(!fastSimMode)spawnParticles(f.x+dx/d*f.r,f.y+dy/d*f.r,"#fb923c",5);
    }
    function updateMarioFireballs(f,dt){
      const m=f.mario;
      for(let i=m.fireballs.length-1;i>=0;i--){const p=m.fireballs[i],ox=p.x,oy=p.y;p.x+=p.vx*dt;p.y+=p.vy*dt;p.life-=dt;let wall=false;
        if(p.x-p.r<=arena.x||p.x+p.r>=arena.x2){p.x=clamp(p.x,arena.x+p.r,arena.x2-p.r);p.vx*=-1;wall=true;}
        if(p.y-p.r<=arena.y||p.y+p.r>=arena.y2){p.y=clamp(p.y,arena.y+p.r,arena.y2-p.r);p.vy*=-1;wall=true;}
        if(wall){if(p.bounces>0)p.bounces--;else{m.fireballs.splice(i,1);continue;}}
        let hit=null,best=1;
        for(const e of enemiesOf(f)){if(!e.alive||e.tano?.hidden>0)continue;const h=spiderSegHit(ox,oy,p.x,p.y,e.x,e.y,e.r+p.r);if(h!==null&&h<best){best=h;hit=e;}}
        if(hit){damage(hit,MARIO.fireDamage,f,"파이어볼");if(!fastSimMode)spawnHitFlash(hit.x,hit.y,"#fb923c",45);m.fireballs.splice(i,1);continue;}
        if(p.life<=0)m.fireballs.splice(i,1);
      }
    }
    function updateMario(f,dt){
      const m=f?.mario;if(!m||!f.alive)return;m.blink=Math.max(0,m.blink-dt);updateMarioFireballs(f,dt);
      if(m.blockId){const b=fighterById(m.blockId);if(!b||!b.alive){m.blockId=null;if(m.power==="none")m.nextBlock=MARIO.blockDelay;}else if(m.power==="none"&&Math.hypot(f.x-b.x,f.y-b.y)<=f.r+b.r+3){marioCollectBlock(f,b);}}
      if(m.power==="star"){
        m.starTime-=dt;for(const id of Object.keys(m.starHits))m.starHits[id]=Math.max(0,m.starHits[id]-dt);
        for(const e of enemiesOf(f)){if(!e.alive||Math.hypot(e.x-f.x,e.y-f.y)>f.r+e.r+3||(m.starHits[e.id]||0)>0)continue;const dx=e.x-f.x,dy=e.y-f.y,d=Math.hypot(dx,dy)||1;damage(e,MARIO.starDamage,f,"슈퍼스타");e.vx+=dx/d*220;e.vy+=dy/d*220;m.starHits[e.id]=MARIO.starContactCd;if(!fastSimMode)spawnHitFlash(e.x,e.y,"#fde047",58);}
        if(m.starTime<=0)marioResetPower(f,false);return;
      }
      if(m.power==="fire"){m.fireCd-=dt;if(m.fireCd<=0){marioFire(f);m.fireCd+=MARIO.firePeriod;}return;}
      if(m.power!=="none")return;
      if(m.blink>0)return;m.nextBlock-=dt;if(m.nextBlock<=0)marioSpawnBlock(f);
    }
    function drawMarioBlock(f){
      ctx.save();ctx.translate(f.x,f.y);ctx.fillStyle="#fbbf24";ctx.strokeStyle="#92400e";ctx.lineWidth=3;ctx.fillRect(-f.r,-f.r,f.r*2,f.r*2);ctx.strokeRect(-f.r,-f.r,f.r*2,f.r*2);ctx.fillStyle="#fff7ed";ctx.font="1000 22px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";ctx.fillText("?",0,1);ctx.restore();drawHealthBar(f);
    }
    function drawMarioCharacter(f){
      const m=f.mario||{power:"none",shield:0,blink:0,fireballs:[]};if(!f.portraitOnly&&!fastSimMode){ctx.save();ctx.beginPath();ctx.rect(arena.x,arena.y,arena.size,arena.size);ctx.clip();for(const p of m.fireballs||[]){ctx.shadowColor="#fb923c";ctx.shadowBlur=12;ctx.fillStyle="#f97316";ctx.beginPath();ctx.arc(p.x,p.y,p.r,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fde68a";ctx.beginPath();ctx.arc(p.x-2,p.y-2,p.r*.45,0,Math.PI*2);ctx.fill();}ctx.restore();}
      const flicker=m.blink>0&&Math.floor(battleTime*18)%2===0;ctx.save();if(flicker)ctx.globalAlpha=.28;ctx.translate(f.x,f.y);ctx.scale(f.r/20,f.r/20);
      if(m.power==="star"){ctx.shadowColor="#fde047";ctx.shadowBlur=24;ctx.fillStyle="#fef08a";ctx.beginPath();ctx.arc(0,0,21,0,Math.PI*2);ctx.fill();}
      ctx.fillStyle=m.power==="fire"?"#fff7ed":"#ef4444";ctx.beginPath();ctx.arc(0,-5,14,0,Math.PI*2);ctx.fill();ctx.fillStyle="#dc2626";ctx.beginPath();ctx.arc(0,-13,15,Math.PI,0);ctx.fill();ctx.fillRect(-14,-13,28,5);
      ctx.fillStyle="#fed7aa";ctx.beginPath();ctx.ellipse(0,-3,11,10,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#3f2a1d";ctx.beginPath();ctx.ellipse(0,2,8,3,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#111827";ctx.fillRect(-7,-5,3,3);ctx.fillRect(4,-5,3,3);
      ctx.fillStyle=m.power==="fire"?"#ef4444":"#2563eb";ctx.beginPath();ctx.moveTo(-12,6);ctx.lineTo(-9,19);ctx.lineTo(9,19);ctx.lineTo(12,6);ctx.closePath();ctx.fill();ctx.fillStyle="#fbbf24";ctx.beginPath();ctx.arc(-6,9,1.8,0,Math.PI*2);ctx.arc(6,9,1.8,0,Math.PI*2);ctx.fill();ctx.restore();drawHealthBar(f);drawName(f);
      if(!f.portraitOnly&&(m.power==="mushroom"||m.power==="fire")){const total=5,w=8,g=2,start=f.x-(total*w+(total-1)*g)/2;for(let i=0;i<total;i++){ctx.fillStyle=i<m.shield?(m.power==="fire"?"#fb923c":"#ef4444"):"#374151";ctx.fillRect(start+i*(w+g),f.y-f.r-15,w,5);}}
      if(!f.portraitOnly&&m.power==="star")drawRing(f.x,f.y,f.r+6,"#fde047",3);
    }

'''
one(ANCHOR, MARIO_CODE + ANCHOR, 'functions')

one('''        if (c.id === "spider_man") initSpiderMan(preview);
        if (c.id === "bald_cape") initBaldCape(preview);''', '''        if (c.id === "spider_man") initSpiderMan(preview);
        if (c.id === "mario_plumber") initMario(preview);
        if (c.id === "bald_cape") initBaldCape(preview);''', 'preview')

one('''      if (c.id === "spider_man") initSpiderMan(fighter);
      if (c.id === "bald_cape") initBaldCape(fighter);''', '''      if (c.id === "spider_man") initSpiderMan(fighter);
      if (c.id === "mario_plumber") initMario(fighter);
      if (c.id === "bald_cape") initBaldCape(fighter);''', 'fighter')

one('''      if (f.spider) { drawSpiderCharacter(f); return; }
      if (f.baldCape) { drawBaldCapeCharacter(f); return; }''', '''      if (f.spider) { drawSpiderCharacter(f); return; }
      if (f.marioBlock) { drawMarioBlock(f); return; }
      if (f.mario) { drawMarioCharacter(f); return; }
      if (f.baldCape) { drawBaldCapeCharacter(f); return; }''', 'draw')

one('''      if (f.spider) updateSpiderMan(f, dt);
      if (!f.alive) return;''', '''      if (f.spider) updateSpiderMan(f, dt);
      if (f.mario) updateMario(f, dt);
      if (!f.alive) return;''', 'update')

one('''    function updateFighter(f, dt) {
      if (!f.alive) return;''', '''    function updateFighter(f, dt) {
      if (!f.alive) return;
      if (f.marioBlock) { f.x=f.marioBlock.anchorX; f.y=f.marioBlock.anchorY; f.vx=0; f.vy=0; return; }''', 'block update')

old = '''      amount = songDebuffReducedIncomingDamage(target, amount, source);
      if (target.iron) {'''
new = '''      amount = songDebuffReducedIncomingDamage(target, amount, source);
      if (target.mario) { const marioResult=marioAbsorbDamage(target,amount,source,reason); if (marioResult!==null) return marioResult; }
      if (target.iron) {'''
if s.count(old) != 2:
    raise SystemExit(f'damage intercept: expected 2, found {s.count(old)}')
s = s.replace(old, new)

s = s.replace('볼배틀 리뉴얼 v132', '볼배틀 리뉴얼 v133')

for marker in ['id:"mario_plumber"','function initMario','function updateMario','function drawMarioCharacter','function marioAbsorbDamage']:
    if marker not in s:
        raise SystemExit('missing '+marker)

p.write_text(s, encoding='utf-8')
print('patched')
