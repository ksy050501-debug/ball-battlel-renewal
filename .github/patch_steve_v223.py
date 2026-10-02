from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')

def rep(old, new, label, count=1):
    global s
    n = s.count(old)
    if n != count:
        raise SystemExit(f'{label}: expected {count}, got {n}')
    s = s.replace(old, new, count)

rep('<title>볼배틀 리뉴얼 v222</title>', '<title>볼배틀 리뉴얼 v223</title>', 'head title')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v222</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v223</h1>', 'main title')

old_char = '''      { id:"steve_miner", name:"스티브", mark:"⛏", role:"게임", color:"#3b82f6", hp:170, attack:0, speed:2.6, range:0,
        skillName:"채굴 · 장비 진화 · 네더 원정", condition:"자원 1개 랜덤 생성 · 7초 미습득 시 자원으로 이동 · 돌2→철2→다이아2 · 다이아 이후 네더 포탈", desc:"나무 장비로 시작한다. 현재 단계에 필요한 자원은 맵의 랜덤 위치에 항상 1개만 존재하며 평소에는 자원을 추적하지 않는다. 7초 동안 습득하지 못하면 그 자원으로 이동하고, 넉넉한 습득 판정으로 자원을 모은다. 돌 2개, 철 2개, 다이아 2개를 차례로 모아 장비가 강화된다. 다이아 장비가 되면 일정 주기로 랜덤한 벽 일부가 네더 포탈로 변하고, 포탈에 닿으면 10초간 전장을 떠난 뒤 랜덤한 벽에서 네더라이트 장비로 귀환하며 체력30을 잃는다." },'''
new_char = '''      { id:"steve_miner", name:"스티브", mark:"⛏", role:"게임", color:"#3b82f6", hp:170, attack:0, speed:2.6, range:0,
        skillName:"채굴 · 장비 진화 · 네더 원정", condition:"자원 1개 랜덤 생성 · 단계별 자동이동 5/7/9/11초 · 나무1→돌2→철3→다이아4 · 다이아 이후 네더 포탈", desc:"맨손으로 시작한다. 현재 단계에 필요한 자원은 맵의 랜덤 위치에 항상 1개만 존재하고 평소에는 추적하지 않는다. 나무는 5초, 돌은 7초, 철은 9초, 다이아는 11초 동안 습득하지 못했을 때만 해당 자원으로 이동한다. 나무1개, 돌2개, 철3개, 다이아4개를 차례로 모아 맨손→나무→돌→철→다이아 장비로 진화하며, 자원을 얻은 뒤 다음 자원은 1초 후 새로운 랜덤 위치에 생성된다. 다이아 장비가 되면 랜덤한 벽 일부에 네더 포탈이 나타나고, 포탈에 닿으면 10초간 전장을 떠난 뒤 랜덤한 벽에서 네더라이트 장비로 귀환하며 체력30을 잃는다." },'''
rep(old_char, new_char, 'character card')

old_info = '''      if(c.id==="steve_miner")return {damage:"나무검7 / 돌검9 / 철검11 / 다이아검14 / 네더라이트검17",tick:"근접 공격1.05초 · 자원 1개만 존재 · 7초 미습득 시 자원 이동 · 돌2→철2→다이아2 · 네더10초",tip:"자원은 랜덤 위치에 한 개만 생기며 처음 7초 동안은 추적하지 않는다. 습득 반경은 몸체+자원 반경에 20을 더한다. 철부터 장비의 일반 피해 감소가 생기며 다이아 이후 랜덤 벽 포탈에 닿으면 10초 뒤 네더라이트로 귀환하고 현재 체력30을 잃는다."};'''
new_info = '''      if(c.id==="steve_miner")return {damage:"맨손5 / 나무검7 / 돌검9 / 철검11 / 다이아검14 / 네더라이트검17",tick:"근접 공격1.05초 · 자원 1개만 존재 · 자동이동 5/7/9/11초 · 나무1→돌2→철3→다이아4 · 다음 자원1초 후 생성 · 네더10초",tip:"맨손에서 나무를 1개 얻어 나무 장비가 열린다. 이후 돌2개, 철3개, 다이아4개가 필요하며 단계가 높을수록 자동 이동까지 더 오래 기다린다. 습득 반경은 몸체+자원 반경에 20을 더한다. 기존 장비별 공격력과 피해 감소는 유지하며, 다이아 이후 랜덤 벽 포탈에 닿으면 10초 뒤 네더라이트로 귀환하고 현재 체력30을 잃는다."};'''
rep(old_info, new_info, 'damage info')

old_const = '''    const STEVE = {
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
    function steveTier(f){return STEVE_TIERS[f?.steve?.tier||0]||STEVE_TIERS[0];}'''
new_const = '''    const STEVE = {
      pickupBonus:20, resourceRadius:10, forceWaits:[5,7,9,11], resourceSpawnDelay:1,
      attackPeriod:1.05, meleeBonus:12,
      portalFirst:5, portalLife:4.5, portalGap:4.5, portalLength:96,
      netherTime:10, netherCost:30
    };
    const STEVE_TIERS = [
      {name:"맨손",resource:"wood",resourceName:"나무",need:1,damage:5,reduction:1.00,color:"#b77956"},
      {name:"나무",resource:"stone",resourceName:"돌",need:2,damage:7,reduction:1.00,color:"#a16207"},
      {name:"돌",resource:"iron",resourceName:"철",need:3,damage:9,reduction:.98,color:"#78716c"},
      {name:"철",resource:"diamond",resourceName:"다이아",need:4,damage:11,reduction:.92,color:"#d1d5db"},
      {name:"다이아",resource:null,resourceName:"",need:0,damage:14,reduction:.86,color:"#22d3ee"},
      {name:"네더라이트",resource:null,resourceName:"",need:0,damage:17,reduction:.80,color:"#4c1d95"}
    ];
    const STEVE_RES = {
      wood:{name:"나무",color:"#a16207",edge:"#713f12"},
      stone:{name:"돌",color:"#78716c",edge:"#44403c"},
      iron:{name:"철",color:"#d1d5db",edge:"#6b7280"},
      diamond:{name:"다이아",color:"#22d3ee",edge:"#0e7490"}
    };
    function initSteve(f){
      f.steve={tier:0,count:0,resource:null,resourceSpawnCd:0,attackCd:.35,swing:0,forcing:false,portal:null,portalCd:0,nether:0,baseSpeed:f.baseSpeed||f.speed||2.6};
      steveSpawnResource(f);
    }
    function steveTier(f){return STEVE_TIERS[f?.steve?.tier||0]||STEVE_TIERS[0];}
    function steveForceWait(f){const t=clamp(f?.steve?.tier||0,0,3);return STEVE.forceWaits[t]||STEVE.forceWaits[0];}'''
rep(old_const, new_const, 'Steve constants')

start = s.index('    function steveCollectResource(f){')
end = s.index('    function steveSpawnPortal(f){', start)
new_collect = '''    function steveCollectResource(f){
      const s=f?.steve,t=steveTier(f),res=s?.resource;if(!s||!res||!t.resource||res.type!==t.resource)return false;
      s.count++;s.resource=null;s.forcing=false;s.resourceSpawnCd=STEVE.resourceSpawnDelay;
      const info=STEVE_RES[res.type];
      if(!fastSimMode){spawnBlast(res.x,res.y,28,info.color);spawnParticles(res.x,res.y,info.color,10);spawnFloatingText(f.x,f.y-f.r-30,info.name+" 획득 "+s.count+"/"+t.need,info.color);playSound("hit",.35);}
      if(s.count>=t.need){s.tier=Math.min(4,s.tier+1);s.count=0;const nt=steveTier(f);if(!fastSimMode){spawnBlast(f.x,f.y,50,nt.color);spawnParticles(f.x,f.y,nt.color,18);spawnFloatingText(f.x,f.y-f.r-42,nt.name+" 장비!",nt.color);playSound("summon",.65);}if(s.tier===4){s.portalCd=STEVE.portalFirst;s.resource=null;s.resourceSpawnCd=0;}}
      return true;
    }
'''
s = s[:start] + new_collect + s[end:]

rep('const s=f?.steve;if(!s||s.tier!==3||s.nether>0)return;', 'const s=f?.steve;if(!s||s.tier!==4||s.nether>0)return;', 'portal tier check')
rep('const s=f?.steve;if(!s||s.tier!==3||s.nether>0)return false;', 'const s=f?.steve;if(!s||s.tier!==4||s.nether>0)return false;', 'nether entry tier check')
rep('s.tier=4;s.count=0;s.resource=null;s.portal=null;s.portalCd=0;', 's.tier=5;s.count=0;s.resource=null;s.resourceSpawnCd=0;s.portal=null;s.portalCd=0;', 'nether exit tier')

old_update = '''      if(s.tier<3){if(!s.resource)steveSpawnResource(f);const r=s.resource;if(r){r.age+=dt;const pickup=f.r+r.r+STEVE.pickupBonus;if(Math.hypot(f.x-r.x,f.y-r.y)<=pickup){steveCollectResource(f);return false;}if(r.age>=STEVE.forceWait&&!steveBlocked(f)){const dx=r.x-f.x,dy=r.y-f.y,d=Math.hypot(dx,dy)||1,sp=(s.baseSpeed||f.baseSpeed||2.6)*44;f.vx=dx/d*sp;f.vy=dy/d*sp;s.forcing=true;}else s.forcing=false;}}
      else if(s.tier===3){if(s.portal){s.portal.life=Math.max(0,s.portal.life-dt);if(steveTouchingPortal(f,s.portal)){steveEnterNether(f);return true;}if(s.portal.life<=0){s.portal=null;s.portalCd=STEVE.portalGap;}}else{s.portalCd=Math.max(0,(s.portalCd||0)-dt);if(s.portalCd<=0)steveSpawnPortal(f);}}'''
new_update = '''      if(s.tier<4){if(!s.resource){s.resourceSpawnCd=Math.max(0,(s.resourceSpawnCd||0)-dt);if(s.resourceSpawnCd<=0)steveSpawnResource(f);}const r=s.resource;if(r){r.age+=dt;const pickup=f.r+r.r+STEVE.pickupBonus;if(Math.hypot(f.x-r.x,f.y-r.y)<=pickup){steveCollectResource(f);return false;}if(r.age>=steveForceWait(f)&&!steveBlocked(f)){const dx=r.x-f.x,dy=r.y-f.y,d=Math.hypot(dx,dy)||1,sp=(s.baseSpeed||f.baseSpeed||2.6)*44;f.vx=dx/d*sp;f.vy=dy/d*sp;s.forcing=true;}else s.forcing=false;}else s.forcing=false;}
      else if(s.tier===4){if(s.portal){s.portal.life=Math.max(0,s.portal.life-dt);if(steveTouchingPortal(f,s.portal)){steveEnterNether(f);return true;}if(s.portal.life<=0){s.portal=null;s.portalCd=STEVE.portalGap;}}else{s.portalCd=Math.max(0,(s.portalCd||0)-dt);if(s.portalCd<=0)steveSpawnPortal(f);}}'''
rep(old_update, new_update, 'update progression')

old_status = '''if(s.tier<3){const r=s.resource,wait=r?Math.max(0,STEVE.forceWait-r.age):STEVE.forceWait;return {ratio:t.need?clamp(s.count/t.need,0,1):1,className:"skill-fill",text:`${t.name} 장비 · ${t.resourceName} ${s.count}/${t.need}`,extraTextHtml:`<div class="status-skill-label">${s.forcing?"자원으로 이동 중":`자동 이동까지 ${wait.toFixed(1)}초`}</div>`};}if(s.tier===3)return {ratio:s.portal?clamp(s.portal.life/s.portal.maxLife,0,1):clamp(1-(s.portalCd||0)/STEVE.portalGap,0,1),className:"skill-fill",text:s.portal?`다이아 장비 · 포탈 ${s.portal.life.toFixed(1)}초`:`다이아 장비 · 포탈 대기 ${(s.portalCd||0).toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">포탈 접촉 → 네더 10초</div>'};'''
new_status = '''if(s.tier<4){const r=s.resource,wait=r?Math.max(0,steveForceWait(f)-r.age):Math.max(0,s.resourceSpawnCd||0);return {ratio:t.need?clamp(s.count/t.need,0,1):1,className:"skill-fill",text:`${t.name} · ${t.resourceName} ${s.count}/${t.need}`,extraTextHtml:`<div class="status-skill-label">${r?(s.forcing?"자원으로 이동 중":`자동 이동까지 ${wait.toFixed(1)}초`):`다음 자원 ${wait.toFixed(1)}초`}</div>`};}if(s.tier===4)return {ratio:s.portal?clamp(s.portal.life/s.portal.maxLife,0,1):clamp(1-(s.portalCd||0)/STEVE.portalGap,0,1),className:"skill-fill",text:s.portal?`다이아 장비 · 포탈 ${s.portal.life.toFixed(1)}초`:`다이아 장비 · 포탈 대기 ${(s.portalCd||0).toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">포탈 접촉 → 네더 10초</div>'};'''
rep(old_status, new_status, 'status text')

old_draw = '''      if(s.tier>=2){ctx.globalAlpha=.82;ctx.fillStyle=tier.color;ctx.fillRect(-10,-19,20,6);ctx.fillRect(-11,-3,22,12);ctx.globalAlpha=1;ctx.strokeStyle="#f8fafc";ctx.lineWidth=.8;ctx.strokeRect(-11,-3,22,12);}else if(s.tier===1){ctx.strokeStyle=tier.color;ctx.lineWidth=2;ctx.strokeRect(-10,-3,20,13);}
      const swing=(s.swing||0)>0?-1.0+((.22-s.swing)/.22)*1.65:-.45;ctx.save();ctx.translate(9,2);ctx.rotate(swing);ctx.strokeStyle=tier.color;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(22,0);ctx.stroke();ctx.strokeStyle="#f8fafc";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(4,-1);ctx.lineTo(22,-1);ctx.stroke();ctx.fillStyle="#78350f";ctx.fillRect(-3,-3,7,6);ctx.restore();ctx.restore();drawHealthBar(f);drawName(f);'''
new_draw = '''      if(s.tier>=3){ctx.globalAlpha=.82;ctx.fillStyle=tier.color;ctx.fillRect(-10,-19,20,6);ctx.fillRect(-11,-3,22,12);ctx.globalAlpha=1;ctx.strokeStyle="#f8fafc";ctx.lineWidth=.8;ctx.strokeRect(-11,-3,22,12);}else if(s.tier===2){ctx.strokeStyle=tier.color;ctx.lineWidth=2;ctx.strokeRect(-10,-3,20,13);}
      const swing=(s.swing||0)>0?-1.0+((.22-s.swing)/.22)*1.65:-.45;ctx.save();ctx.translate(9,2);ctx.rotate(swing);if(s.tier===0){ctx.fillStyle="#b77956";ctx.fillRect(0,-4,15,8);ctx.fillStyle="#8b5e3c";ctx.fillRect(12,-6,8,12);ctx.strokeStyle="#5b3a29";ctx.lineWidth=1.2;ctx.strokeRect(12,-6,8,12);}else{ctx.strokeStyle=tier.color;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(22,0);ctx.stroke();ctx.strokeStyle="#f8fafc";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(4,-1);ctx.lineTo(22,-1);ctx.stroke();ctx.fillStyle="#78350f";ctx.fillRect(-3,-3,7,6);}ctx.restore();ctx.restore();drawHealthBar(f);drawName(f);'''
rep(old_draw, new_draw, 'Steve sprite')

note = '      "v223: 스티브 성장 구조 개편. 맨손 시작 후 나무1→돌2→철3→다이아4 순서로 단계가 갈수록 더 많은 자원이 필요하도록 변경. 자원 자동 이동 대기시간을 단계별 5/7/9/11초로 설정하고, 자원 획득 후 다음 자원은 1초 뒤 랜덤 위치에 생성. 기존 장비별 공격력·피해감소, HP170, 네더 10초 및 귀환 체력30 감소는 유지.",\n'
rep('      const patchNotes = [\n', '      const patchNotes = [\n' + note, 'patch note insertion')

p.write_text(s, encoding='utf-8')
