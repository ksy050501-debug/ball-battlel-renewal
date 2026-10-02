from pathlib import Path

p = Path('index.html')
t = p.read_text(encoding='utf-8')

def rep(old, new, label):
    global t
    n = t.count(old)
    if n != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {n}')
    t = t.replace(old, new, 1)

rep('<title>볼배틀 리뉴얼 v221</title>', '<title>볼배틀 리뉴얼 v222</title>', 'title')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v221</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v222</h1>', 'h1')

char_anchor = '''      { id:"wok_wok", name:"웍웍", mark:"🐺", role:"게임", color:"#7f1d1d", hp:140, attack:0, speed:1.6, range:0,'''
char_new = '''      { id:"steve_miner", name:"스티브", mark:"⛏", role:"게임", color:"#3b82f6", hp:170, attack:0, speed:2.6, range:0,
        skillName:"채굴 · 장비 진화 · 네더 원정", condition:"자원 1개 랜덤 생성 · 7초 미습득 시 자원으로 이동 · 돌2→철2→다이아2 · 다이아 이후 네더 포탈", desc:"나무 장비로 시작한다. 현재 단계에 필요한 자원은 맵의 랜덤 위치에 항상 1개만 존재하며 평소에는 자원을 추적하지 않는다. 7초 동안 습득하지 못하면 그 자원으로 이동하고, 넉넉한 습득 판정으로 자원을 모은다. 돌 2개, 철 2개, 다이아 2개를 차례로 모아 장비가 강화된다. 다이아 장비가 되면 일정 주기로 랜덤한 벽 일부가 네더 포탈로 변하고, 포탈에 닿으면 10초간 전장을 떠난 뒤 랜덤한 벽에서 네더라이트 장비로 귀환하며 체력30을 잃는다." },
      { id:"wok_wok", name:"웍웍", mark:"🐺", role:"게임", color:"#7f1d1d", hp:140, attack:0, speed:1.6, range:0,'''
rep(char_anchor, char_new, 'character')

dmg_anchor = '''      if(c.id==="kirby")return {damage:"소드 회전베기10+출혈1×4 / 빔 채찍7+둔화 / 파이어5+화상1×3 / 밤 폭탄12×2(반경58) / 뱉기 벽충돌12",tick:"기본 흡입10초 주기·3.2초 지속·전방120°·느린 흡입 / 배회형 중립 몬스터6.5초마다·최대2 / 카피 누적피해45에서 별 이탈(연출)·재획득 불가",tip:"중립 몬스터는 적을 추적하지 않고 임의 방향으로 돌아다니다 사거리 안에 캐릭터가 들어왔을 때만 기술을 사용한다. 소드는 회전베기, 빔은 휘어지는 별 채찍, 파이어는 좁은 화염방사, 밤은 한 번 튀는 폭탄이며 카피 자가비는 강화판을 사용한다."};'''
dmg_new = dmg_anchor + '''\n      if(c.id==="steve_miner")return {damage:"나무검7 / 돌검9 / 철검11 / 다이아검14 / 네더라이트검17",tick:"근접 공격1.05초 · 자원 1개만 존재 · 7초 미습득 시 자원 이동 · 돌2→철2→다이아2 · 네더10초",tip:"자원은 랜덤 위치에 한 개만 생기며 처음 7초 동안은 추적하지 않는다. 습득 반경은 몸체+자원 반경에 20을 더한다. 철부터 장비의 일반 피해 감소가 생기며 다이아 이후 랜덤 벽 포탈에 닿으면 10초 뒤 네더라이트로 귀환하고 현재 체력30을 잃는다."};'''
rep(dmg_anchor, dmg_new, 'damage info')

preview_anchor = '''        if (c.id === "kirby") initKirby(preview);\n        if (c.id === "mario_plumber") initMario(preview);'''
preview_new = '''        if (c.id === "kirby") initKirby(preview);\n        if (c.id === "steve_miner") initSteve(preview);\n        if (c.id === "mario_plumber") initMario(preview);'''
rep(preview_anchor, preview_new, 'preview init')

fighter_anchor = '''      if (c.id === "kirby") initKirby(fighter);\n      if (c.id === "mario_plumber") initMario(fighter);'''
fighter_new = '''      if (c.id === "kirby") initKirby(fighter);\n      if (c.id === "steve_miner") initSteve(fighter);\n      if (c.id === "mario_plumber") initMario(fighter);'''
rep(fighter_anchor, fighter_new, 'fighter init')

steve_code = r'''
    const STEVE = {
      pickupBonus:20, resourceRadius:10, forceWait:7,
      attackPeriod:1.05, meleeBonus:12,
      portalFirst:5, portalLife:4.5, portalGap:4.5, portalLength:96,
      netherTime:10, netherCost:30
    };
    const STEVE_TIERS = [
      {name:"나무",resource:"stone",resourceName:"돌",need:2,damage:7,reduction:1.00,color:"#a16207"},
      {name:"돌",resource:"iron",resourceName:"철",need:2,damage:9,reduction:.98,color:"#78716c"},
      {name:"철",resource:"diamond",resourceName:"다이아",need:2,damage:11,reduction:.92,color:"#d1d5db"},
      {name:"다이아",resource:null,resourceName:"",need:0,damage:14,reduction:.86,color:"#22d3ee"},
      {name:"네더라이트",resource:null,resourceName:"",need:0,damage:17,reduction:.80,color:"#4c1d95"}
    ];
    const STEVE_RES = {
      stone:{name:"돌",color:"#78716c",edge:"#44403c"},
      iron:{name:"철",color:"#d1d5db",edge:"#6b7280"},
      diamond:{name:"다이아",color:"#22d3ee",edge:"#0e7490"}
    };
    function initSteve(f){
      f.steve={tier:0,count:0,resource:null,attackCd:.35,swing:0,forcing:false,portal:null,portalCd:0,nether:0,baseSpeed:f.baseSpeed||f.speed||2.6};
      steveSpawnResource(f);
    }
    function steveTier(f){return STEVE_TIERS[f?.steve?.tier||0]||STEVE_TIERS[0];}
    function steveBlocked(f){return !f?.alive||isStunned(f)||(f.hardFreeze||0)>0||(f.bindStun||0)>0||(f.punchHold||0)>0||(f.punchFlight||0)>0||(f.vampSuppressed||0)>0||(f.joltStop||0)>0||isCasting(f);}
    function steveSpawnResource(f){
      const s=f?.steve,t=steveTier(f);if(!s||!t.resource){if(s)s.resource=null;return;}
      const r=STEVE.resourceRadius;
      s.resource={type:t.resource,x:rand(arena.x+r+18,arena.x2-r-18),y:rand(arena.y+r+18,arena.y2-r-18),r,age:0};s.forcing=false;
    }
    function steveCollectResource(f){
      const s=f?.steve,t=steveTier(f),res=s?.resource;if(!s||!res||!t.resource||res.type!==t.resource)return false;
      s.count++;s.resource=null;s.forcing=false;
      const info=STEVE_RES[res.type];
      if(!fastSimMode){spawnBlast(res.x,res.y,28,info.color);spawnParticles(res.x,res.y,info.color,10);spawnFloatingText(f.x,f.y-f.r-30,info.name+" 획득 "+s.count+"/"+t.need,info.color);playSound("hit",.35);}
      if(s.count>=t.need){s.tier=Math.min(3,s.tier+1);s.count=0;const nt=steveTier(f);if(!fastSimMode){spawnBlast(f.x,f.y,50,nt.color);spawnParticles(f.x,f.y,nt.color,18);spawnFloatingText(f.x,f.y-f.r-42,nt.name+" 장비!",nt.color);playSound("summon",.65);}if(s.tier===3){s.portalCd=STEVE.portalFirst;s.resource=null;}else steveSpawnResource(f);}else steveSpawnResource(f);
      return true;
    }
    function steveSpawnPortal(f){
      const s=f?.steve;if(!s||s.tier!==3||s.nether>0)return;
      const side=Math.floor(rand(0,4)),half=STEVE.portalLength/2,margin=half+18;
      const pos=(side<2)?rand(arena.x+margin,arena.x2-margin):rand(arena.y+margin,arena.y2-margin);
      s.portal={side,pos,life:STEVE.portalLife,maxLife:STEVE.portalLife};
      if(!fastSimMode)spawnFloatingText(f.x,f.y-f.r-38,"네더 포탈 생성","#c084fc");
    }
    function steveTouchingPortal(f,p){
      if(!p)return false;const half=STEVE.portalLength/2+f.r;
      if(p.side===0)return f.y-f.r<=arena.y+5&&Math.abs(f.x-p.pos)<=half;
      if(p.side===1)return f.y+f.r>=arena.y2-5&&Math.abs(f.x-p.pos)<=half;
      if(p.side===2)return f.x-f.r<=arena.x+5&&Math.abs(f.y-p.pos)<=half;
      return f.x+f.r>=arena.x2-5&&Math.abs(f.y-p.pos)<=half;
    }
    function steveEnterNether(f){
      const s=f?.steve;if(!s||s.tier!==3||s.nether>0)return false;
      s.nether=STEVE.netherTime;s.portal=null;s.portalCd=0;s.forcing=false;f.vx=0;f.vy=0;f.x=arena.x-5000;f.y=arena.y-5000;
      if(!fastSimMode){spawnFloatingText(arena.x+arena.size/2,arena.y+32,"스티브 · 네더 진입","#c084fc");playSound("magic",.8);}return true;
    }
    function steveExitNether(f){
      const s=f?.steve;if(!s)return;const side=Math.floor(rand(0,4)),pad=f.r+3;
      if(side===0){f.x=rand(arena.x+35,arena.x2-35);f.y=arena.y+pad;f.vx=rand(-45,45);f.vy=Math.abs((s.baseSpeed||2.6)*44);}
      else if(side===1){f.x=rand(arena.x+35,arena.x2-35);f.y=arena.y2-pad;f.vx=rand(-45,45);f.vy=-Math.abs((s.baseSpeed||2.6)*44);}
      else if(side===2){f.x=arena.x+pad;f.y=rand(arena.y+35,arena.y2-35);f.vx=Math.abs((s.baseSpeed||2.6)*44);f.vy=rand(-45,45);}
      else{f.x=arena.x2-pad;f.y=rand(arena.y+35,arena.y2-35);f.vx=-Math.abs((s.baseSpeed||2.6)*44);f.vy=rand(-45,45);}
      s.tier=4;s.count=0;s.resource=null;s.portal=null;s.portalCd=0;
      if(!fastSimMode){spawnBlast(f.x,f.y,72,"#7e22ce");spawnParticles(f.x,f.y,"#c084fc",24);spawnFloatingText(f.x,f.y-f.r-40,"네더라이트 장비 · 체력 -"+STEVE.netherCost,"#c084fc");playSound("summon",1);}
      bodyDirectDamage(f,STEVE.netherCost,f,"네더 원정","#a855f7");
    }
    function steveAttack(f,dt){
      const s=f.steve;s.attackCd=Math.max(0,s.attackCd-dt);s.swing=Math.max(0,(s.swing||0)-dt);if(s.attackCd>0||steveBlocked(f))return;
      const q=nearestEnemy(f),e=q.enemy;if(!e||q.d>f.r+e.r+STEVE.meleeBonus)return;
      const tier=steveTier(f),dealt=damage(e,tier.damage,f,tier.name+" 검");s.attackCd=STEVE.attackPeriod;s.swing=.22;
      if(dealt>0&&!fastSimMode){spawnHitFlash(e.x,e.y,tier.color,34);playSound("hit",.48);}
    }
    function updateSteve(f,dt){
      const s=f?.steve;if(!s||!f.alive)return false;
      if(s.nether>0){s.nether=Math.max(0,s.nether-dt);f.vx=0;f.vy=0;if(s.nether<=0){steveExitNether(f);return false;}return true;}
      steveAttack(f,dt);
      if(s.tier<3){if(!s.resource)steveSpawnResource(f);const r=s.resource;if(r){r.age+=dt;const pickup=f.r+r.r+STEVE.pickupBonus;if(Math.hypot(f.x-r.x,f.y-r.y)<=pickup){steveCollectResource(f);return false;}if(r.age>=STEVE.forceWait&&!steveBlocked(f)){const dx=r.x-f.x,dy=r.y-f.y,d=Math.hypot(dx,dy)||1,sp=(s.baseSpeed||f.baseSpeed||2.6)*44;f.vx=dx/d*sp;f.vy=dy/d*sp;s.forcing=true;}else s.forcing=false;}}
      else if(s.tier===3){if(s.portal){s.portal.life=Math.max(0,s.portal.life-dt);if(steveTouchingPortal(f,s.portal)){steveEnterNether(f);return true;}if(s.portal.life<=0){s.portal=null;s.portalCd=STEVE.portalGap;}}else{s.portalCd=Math.max(0,(s.portalCd||0)-dt);if(s.portalCd<=0)steveSpawnPortal(f);}}
      return false;
    }
    function stevePortalEndpoints(p){
      const h=STEVE.portalLength/2;if(p.side===0)return [p.pos-h,arena.y,p.pos+h,arena.y];if(p.side===1)return [p.pos-h,arena.y2,p.pos+h,arena.y2];if(p.side===2)return [arena.x,p.pos-h,arena.x,p.pos+h];return [arena.x2,p.pos-h,arena.x2,p.pos+h];
    }
    function drawSteveWorld(){
      if(fastSimMode)return;for(const f of fighters){const s=f.alive&&f.steve;if(!s)continue;
        if(s.resource){const r=s.resource,info=STEVE_RES[r.type],pulse=.5+.5*Math.sin(battleTime*5);ctx.save();ctx.translate(r.x,r.y);ctx.shadowColor=info.color;ctx.shadowBlur=8+7*pulse;ctx.fillStyle=info.color;ctx.strokeStyle=info.edge;ctx.lineWidth=2;ctx.fillRect(-9,-9,18,18);ctx.strokeRect(-9,-9,18,18);ctx.globalAlpha=.55;ctx.fillStyle="#fff";ctx.fillRect(-5,-5,4,4);ctx.fillRect(2,1,4,4);ctx.restore();ctx.save();ctx.font="900 10px system-ui";ctx.textAlign="center";ctx.fillStyle=info.color;ctx.strokeStyle="rgba(0,0,0,.8)";ctx.lineWidth=3;ctx.strokeText(info.name,r.x,r.y-16);ctx.fillText(info.name,r.x,r.y-16);ctx.restore();}
        if(s.portal){const p=s.portal,[x1,y1,x2,y2]=stevePortalEndpoints(p),pulse=.5+.5*Math.sin(battleTime*9);ctx.save();ctx.strokeStyle="#a855f7";ctx.shadowColor="#c084fc";ctx.shadowBlur=18;ctx.lineWidth=13+3*pulse;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();ctx.strokeStyle="#e9d5ff";ctx.globalAlpha=.65;ctx.lineWidth=2.2;ctx.setLineDash([8,7]);ctx.lineDashOffset=-battleTime*25;ctx.beginPath();ctx.moveTo(x1,y1);ctx.lineTo(x2,y2);ctx.stroke();ctx.restore();}
      }
    }
    function drawSteveCharacter(f){
      const s=f.steve||{tier:0,swing:0},tier=STEVE_TIERS[s.tier]||STEVE_TIERS[0];ctx.save();ctx.translate(f.x,f.y);applyMarioSpriteSpin(f);ctx.scale(f.r/18,f.r/18);ctx.imageSmoothingEnabled=false;
      ctx.fillStyle="#2563eb";ctx.fillRect(-9,-2,18,15);ctx.fillStyle="#312e81";ctx.fillRect(-9,13,8,9);ctx.fillRect(1,13,8,9);ctx.fillStyle="#b77956";ctx.fillRect(-10,-18,20,17);ctx.fillStyle="#3f2a1d";ctx.fillRect(-10,-18,20,5);ctx.fillRect(-10,-13,4,5);ctx.fillStyle="#fff";ctx.fillRect(-6,-10,5,3);ctx.fillRect(2,-10,5,3);ctx.fillStyle="#2563eb";ctx.fillRect(-4,-10,2,2);ctx.fillRect(3,-10,2,2);
      if(s.tier>=2){ctx.globalAlpha=.82;ctx.fillStyle=tier.color;ctx.fillRect(-10,-19,20,6);ctx.fillRect(-11,-3,22,12);ctx.globalAlpha=1;ctx.strokeStyle="#f8fafc";ctx.lineWidth=.8;ctx.strokeRect(-11,-3,22,12);}else if(s.tier===1){ctx.strokeStyle=tier.color;ctx.lineWidth=2;ctx.strokeRect(-10,-3,20,13);}
      const swing=(s.swing||0)>0?-1.0+((.22-s.swing)/.22)*1.65:-.45;ctx.save();ctx.translate(9,2);ctx.rotate(swing);ctx.strokeStyle=tier.color;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(22,0);ctx.stroke();ctx.strokeStyle="#f8fafc";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(4,-1);ctx.lineTo(22,-1);ctx.stroke();ctx.fillStyle="#78350f";ctx.fillRect(-3,-3,7,6);ctx.restore();ctx.restore();drawHealthBar(f);drawName(f);
    }
'''
steve_anchor = '''    const HINTA = { startDelay: 5, respawn: 5, ballRadius: 10, pickupBonus: 24,'''
rep(steve_anchor, steve_code + '\n' + steve_anchor, 'steve mechanics')

update_anchor = '''      if (f.kirby) updateKirby(f, dt);\n      if (f.mario) updateMario(f, dt);'''
update_new = '''      if (f.kirby) updateKirby(f, dt);\n      if (f.steve && updateSteve(f, dt)) return;\n      if (f.mario) updateMario(f, dt);'''
rep(update_anchor, update_new, 'update hook')

draw_world_anchor = '''      drawHintaBalls();\n      drawRiddleEffects();'''
draw_world_new = '''      drawHintaBalls();\n      drawSteveWorld();\n      drawRiddleEffects();'''
rep(draw_world_anchor, draw_world_new, 'world draw')

draw_body_anchor = '''      if (f.kirby) { drawKirbyCharacter(f); return; }\n      if (f.marioBlock) { drawMarioBlock(f); return; }'''
draw_body_new = '''      if (f.kirby) { drawKirbyCharacter(f); return; }\n      if (f.steve) { drawSteveCharacter(f); return; }\n      if (f.marioBlock) { drawMarioBlock(f); return; }'''
rep(draw_body_anchor, draw_body_new, 'fighter draw')

draw_fighter_anchor = '''    function drawFighter(f) {\n      drawConcussionSlow(f);drawPowerFist(f);drawIronSuit(f);drawConanDeathMark(f);drawCoyoteStatusOverlay(f);'''
draw_fighter_new = '''    function drawFighter(f) {\n      if((f.steve?.nether||0)>0)return;\n      drawConcussionSlow(f);drawPowerFist(f);drawIronSuit(f);drawConanDeathMark(f);drawCoyoteStatusOverlay(f);'''
rep(draw_fighter_anchor, draw_fighter_new, 'hidden draw')

enemy_anchor = '''    function areEnemies(a, b) {\n      if (!a || !b) return false;'''
enemy_new = '''    function areEnemies(a, b) {\n      if (!a || !b) return false;\n      if ((a.steve?.nether||0)>0 || (b.steve?.nether||0)>0) return false;'''
rep(enemy_anchor, enemy_new, 'enemy exclusion')

armor_anchor = '''      // 캡틴은 방패를 들고 있을 때만 일반 피해를 줄인다.\n      if (!fixedDamage && target.captain?.hasShield) final *= CAPTAIN.heldReduction;'''
armor_new = '''      // 캡틴은 방패를 들고 있을 때만 일반 피해를 줄인다.\n      if (!fixedDamage && target.captain?.hasShield) final *= CAPTAIN.heldReduction;\n      if (!fixedDamage && target.steve) final *= (STEVE_TIERS[target.steve.tier||0]?.reduction ?? 1);'''
rep(armor_anchor, armor_new, 'steve armor')

status_anchor = '''      if(f.hinta){\n        const h=f.hinta,b=h.ball;'''
status_new = '''      if(f.steve){const s=f.steve,t=steveTier(f);if(s.nether>0)return {ratio:clamp(1-s.nether/STEVE.netherTime,0,1),className:"skill-fill",text:`네더 탐험 · ${s.nether.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">귀환 시 네더라이트 · 체력 -30</div>'};if(s.tier<3){const r=s.resource,wait=r?Math.max(0,STEVE.forceWait-r.age):STEVE.forceWait;return {ratio:t.need?clamp(s.count/t.need,0,1):1,className:"skill-fill",text:`${t.name} 장비 · ${t.resourceName} ${s.count}/${t.need}`,extraTextHtml:`<div class="status-skill-label">${s.forcing?"자원으로 이동 중":`자동 이동까지 ${wait.toFixed(1)}초`}</div>`};}if(s.tier===3)return {ratio:s.portal?clamp(s.portal.life/s.portal.maxLife,0,1):clamp(1-(s.portalCd||0)/STEVE.portalGap,0,1),className:"skill-fill",text:s.portal?`다이아 장비 · 포탈 ${s.portal.life.toFixed(1)}초`:`다이아 장비 · 포탈 대기 ${(s.portalCd||0).toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">포탈 접촉 → 네더 10초</div>'};return {ratio:1,className:"skill-fill",text:"네더라이트 장비 · 최종 단계",extraTextHtml:'<div class="status-skill-label">검17 · 일반 피해 20% 감소</div>'};}\n      if(f.hinta){\n        const h=f.hinta,b=h.ball;'''
rep(status_anchor, status_new, 'status')

patch_anchor = '''      const patchNotes = [\n      "v221: 캐릭터 표시명 커비→자가비로 변경. 내부 ID와 전투 로직은 유지.",'''
patch_new = '''      const patchNotes = [\n      "v222: 신규 캐릭터 스티브 추가. 자원은 현재 단계에 맞춰 랜덤 위치에 1개만 존재하고 평소에는 추적하지 않으며 7초 미습득 시 자원으로 이동. 돌2→철2→다이아2로 장비가 진화하고, 다이아 단계에서는 랜덤 벽 구간의 네더 포탈에 접촉하면 10초 뒤 랜덤 벽에서 네더라이트 장비로 귀환하며 체력30 감소.",\n      "v221: 캐릭터 표시명 커비→자가비로 변경. 내부 ID와 전투 로직은 유지.",'''
rep(patch_anchor, patch_new, 'patch note')

p.write_text(t, encoding='utf-8')
