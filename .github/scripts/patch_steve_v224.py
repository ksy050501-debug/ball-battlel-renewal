from pathlib import Path
import re

p = Path('index.html')
s = p.read_text(encoding='utf-8')


def rep(old: str, new: str, label: str):
    global s
    count = s.count(old)
    if count != 1:
        raise SystemExit(f'{label}: expected 1 anchor, found {count}')
    s = s.replace(old, new, 1)


rep('<title>볼배틀 리뉴얼 v223</title>', '<title>볼배틀 리뉴얼 v224</title>', 'title version')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v223</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v224</h1>', 'header version')

old_entry = '''      { id:"steve_miner", name:"스티브", mark:"⛏", role:"게임", color:"#3b82f6", hp:170, attack:0, speed:2.6, range:0,
        skillName:"채굴 · 장비 진화 · 네더 원정", condition:"자원 1개 랜덤 생성 · 단계별 자동이동 5/7/9/11초 · 나무1→돌2→철3→다이아4 · 다이아 이후 네더 포탈", desc:"맨손으로 시작한다. 현재 단계에 필요한 자원은 맵의 랜덤 위치에 항상 1개만 존재하고 평소에는 추적하지 않는다. 나무는 5초, 돌은 7초, 철은 9초, 다이아는 11초 동안 습득하지 못했을 때만 해당 자원으로 이동한다. 나무1개, 돌2개, 철3개, 다이아4개를 차례로 모아 맨손→나무→돌→철→다이아 장비로 진화하며, 자원을 얻은 뒤 다음 자원은 1초 후 새로운 랜덤 위치에 생성된다. 다이아 장비가 되면 랜덤한 벽 일부에 네더 포탈이 나타나고, 포탈에 닿으면 10초간 전장을 떠난 뒤 랜덤한 벽에서 네더라이트 장비로 귀환하며 체력30을 잃는다." },'''
new_entry = '''      { id:"steve_miner", name:"스티브", mark:"⛏", role:"게임", color:"#3b82f6", hp:170, attack:0, speed:2.6, range:0,
        skillName:"채굴 · 장비 진화 · 네더 원정", condition:"자원 추적 없음 · 채굴 0.6/0.9/1.2/1.6초 · 충돌 시 중단/진행도 누적 · 나무1→돌2→철3→다이아4", desc:"맨손으로 시작한다. 현재 단계에 필요한 자원은 맵의 랜덤 위치에 항상 1개만 존재하며 자원을 향해 추적 이동하지 않는다. 조금 넓어진 습득 반경 안에 자원이 들어오면 제자리에서 곡괭이질을 시작하고, 채굴 중에는 이동과 공격을 할 수 없다. 적 본체와 충돌하면 채굴이 중단되지만 진행도는 해당 자원에 누적되어 다음에 다시 닿으면 남은 시간만 채굴한다. 나무0.6초, 돌0.9초, 철1.2초, 다이아1.6초가 필요하다. 나무1개, 돌2개, 철3개, 다이아4개를 차례로 모으며 성장할수록 공격범위도 넓어진다. 다이아 장비가 되면 네더 포탈이 나타나고, 포탈에 닿으면 10초간 전장을 떠난 뒤 네더라이트 장비로 귀환하며 체력30을 잃는다." },'''
rep(old_entry, new_entry, 'Steve encyclopedia')

old_const = '''    const STEVE = {
      pickupBonus:20, resourceRadius:10, forceWaits:[5,7,9,11], resourceSpawnDelay:1,
      attackPeriod:1.05, meleeBonus:12,
      portalFirst:5, portalLife:4.5, portalGap:4.5, portalLength:96,
      netherTime:10, netherCost:30
    };'''
new_const = '''    const STEVE = {
      pickupBonus:22, resourceRadius:10, resourceSpawnDelay:1,
      mineTime:{wood:.6,stone:.9,iron:1.2,diamond:1.6},
      attackPeriod:1.05, attackReach:[12,18,23,28,31,34],
      portalFirst:5, portalLife:4.5, portalGap:4.5, portalLength:96,
      netherTime:10, netherCost:30
    };'''
rep(old_const, new_const, 'Steve constants')

old_init = '      f.steve={tier:0,count:0,resource:null,resourceSpawnCd:0,attackCd:.35,swing:0,forcing:false,portal:null,portalCd:0,nether:0,baseSpeed:f.baseSpeed||f.speed||2.6};'
new_init = '      f.steve={tier:0,count:0,resource:null,resourceSpawnCd:0,attackCd:.35,swing:0,mining:false,portal:null,portalCd:0,nether:0,baseSpeed:f.baseSpeed||f.speed||2.6};'
rep(old_init, new_init, 'Steve init')

old_helpers = '''    function steveTier(f){return STEVE_TIERS[f?.steve?.tier||0]||STEVE_TIERS[0];}
    function steveForceWait(f){const t=clamp(f?.steve?.tier||0,0,3);return STEVE.forceWaits[t]||STEVE.forceWaits[0];}
    function steveBlocked(f){return !f?.alive||isStunned(f)||(f.hardFreeze||0)>0||(f.bindStun||0)>0||(f.punchHold||0)>0||(f.punchFlight||0)>0||(f.vampSuppressed||0)>0||(f.joltStop||0)>0||isCasting(f);}'''
new_helpers = '''    function steveTier(f){return STEVE_TIERS[f?.steve?.tier||0]||STEVE_TIERS[0];}
    function steveAttackReach(f){const t=clamp(f?.steve?.tier||0,0,STEVE.attackReach.length-1);return STEVE.attackReach[t]||STEVE.attackReach[0];}
    function steveBlocked(f){return !f?.alive||isStunned(f)||(f.hardFreeze||0)>0||(f.bindStun||0)>0||(f.punchHold||0)>0||(f.punchFlight||0)>0||(f.vampSuppressed||0)>0||(f.joltStop||0)>0||isCasting(f);}'''
rep(old_helpers, new_helpers, 'Steve helpers')

old_spawn = '      s.resource={type:t.resource,x:rand(arena.x+r+18,arena.x2-r-18),y:rand(arena.y+r+18,arena.y2-r-18),r,age:0};s.forcing=false;'
new_spawn = '      s.resource={type:t.resource,x:rand(arena.x+r+18,arena.x2-r-18),y:rand(arena.y+r+18,arena.y2-r-18),r,mineProgress:0};s.mining=false;'
rep(old_spawn, new_spawn, 'Steve resource spawn')

rep('      s.count++;s.resource=null;s.forcing=false;s.resourceSpawnCd=STEVE.resourceSpawnDelay;',
    '      s.count++;s.resource=null;s.mining=false;s.resourceSpawnCd=STEVE.resourceSpawnDelay;',
    'Steve collect state')

old_collect_tail = '''      return true;
    }
    function steveSpawnPortal(f){'''
new_collect_tail = '''      return true;
    }
    function steveMiningCollision(f){
      return enemiesOf(f).some(e=>e?.alive&&Math.hypot(f.x-e.x,f.y-e.y)<=f.r+e.r);
    }
    function steveMineResource(f,dt){
      const s=f?.steve,t=steveTier(f),r=s?.resource;
      if(!s||!r||!t.resource||r.type!==t.resource){if(s)s.mining=false;return false;}
      const pickup=f.r+r.r+STEVE.pickupBonus;
      if(Math.hypot(f.x-r.x,f.y-r.y)>pickup){s.mining=false;return false;}
      if(steveMiningCollision(f)){s.mining=false;return false;}
      if(steveBlocked(f)){s.mining=false;return false;}
      s.mining=true;f.vx=0;f.vy=0;
      const need=STEVE.mineTime[r.type]||1;
      r.mineProgress=Math.min(need,(r.mineProgress||0)+dt);
      if(r.mineProgress+1e-9>=need){steveCollectResource(f);return false;}
      return true;
    }
    function steveSpawnPortal(f){'''
rep(old_collect_tail, new_collect_tail, 'Steve mining helpers')

rep('      s.nether=STEVE.netherTime;s.portal=null;s.portalCd=0;s.forcing=false;f.vx=0;f.vy=0;f.x=arena.x-5000;f.y=arena.y-5000;',
    '      s.nether=STEVE.netherTime;s.portal=null;s.portalCd=0;s.mining=false;f.vx=0;f.vy=0;f.x=arena.x-5000;f.y=arena.y-5000;',
    'Steve nether enter')
rep('      s.tier=5;s.count=0;s.resource=null;s.resourceSpawnCd=0;s.portal=null;s.portalCd=0;',
    '      s.tier=5;s.count=0;s.resource=null;s.resourceSpawnCd=0;s.mining=false;s.portal=null;s.portalCd=0;',
    'Steve nether exit')

attack_pat = re.compile(r'''    function steveAttack\(f,dt\)\{.*?\n    \}\n    function updateSteve\(f,dt\)\{.*?\n      return false;\n    \}\n    function stevePortalEndpoints''', re.S)
new_attack_update = '''    function steveAttack(f,dt){
      const s=f.steve;s.attackCd=Math.max(0,s.attackCd-dt);s.swing=Math.max(0,(s.swing||0)-dt);if(s.attackCd>0||s.mining||steveBlocked(f))return;
      const q=nearestEnemy(f),e=q.enemy;if(!e||q.d>f.r+e.r+steveAttackReach(f))return;
      const tier=steveTier(f),dealt=damage(e,tier.damage,f,tier.name+" 검");s.attackCd=STEVE.attackPeriod;s.swing=.22;
      if(dealt>0&&!fastSimMode){spawnHitFlash(e.x,e.y,tier.color,34);playSound("hit",.48);}
    }
    function updateSteve(f,dt){
      const s=f?.steve;if(!s||!f.alive)return false;
      if(s.nether>0){s.nether=Math.max(0,s.nether-dt);s.mining=false;f.vx=0;f.vy=0;if(s.nether<=0){steveExitNether(f);return false;}return true;}
      if(s.tier<4){
        if(!s.resource){s.resourceSpawnCd=Math.max(0,(s.resourceSpawnCd||0)-dt);if(s.resourceSpawnCd<=0)steveSpawnResource(f);}
        if(s.resource&&steveMineResource(f,dt))return true;
        if(!s.resource)s.mining=false;
        steveAttack(f,dt);
      }else{
        s.mining=false;steveAttack(f,dt);
        if(s.tier===4){if(s.portal){s.portal.life=Math.max(0,s.portal.life-dt);if(steveTouchingPortal(f,s.portal)){steveEnterNether(f);return true;}if(s.portal.life<=0){s.portal=null;s.portalCd=STEVE.portalGap;}}else{s.portalCd=Math.max(0,(s.portalCd||0)-dt);if(s.portalCd<=0)steveSpawnPortal(f);}}
      }
      return false;
    }
    function stevePortalEndpoints'''
s, n = attack_pat.subn(new_attack_update, s, count=1)
if n != 1:
    raise SystemExit(f'Steve attack/update block expected 1, found {n}')

old_draw = '''      const swing=(s.swing||0)>0?-1.0+((.22-s.swing)/.22)*1.65:-.45;ctx.save();ctx.translate(9,2);ctx.rotate(swing);if(s.tier===0){ctx.fillStyle="#b77956";ctx.fillRect(0,-4,15,8);ctx.fillStyle="#8b5e3c";ctx.fillRect(12,-6,8,12);ctx.strokeStyle="#5b3a29";ctx.lineWidth=1.2;ctx.strokeRect(12,-6,8,12);}else{ctx.strokeStyle=tier.color;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(22,0);ctx.stroke();ctx.strokeStyle="#f8fafc";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(4,-1);ctx.lineTo(22,-1);ctx.stroke();ctx.fillStyle="#78350f";ctx.fillRect(-3,-3,7,6);}ctx.restore();ctx.restore();drawHealthBar(f);drawName(f);'''
new_draw = '''      const mining=!!s.mining,swing=mining?-1.12+(.5+.5*Math.sin(battleTime*15))*1.18:((s.swing||0)>0?-1.0+((.22-s.swing)/.22)*1.65:-.45);ctx.save();ctx.translate(9,2);ctx.rotate(swing);if(mining){ctx.strokeStyle="#8b5a2b";ctx.lineWidth=4;ctx.lineCap="round";ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(22,0);ctx.stroke();ctx.strokeStyle="#cbd5e1";ctx.lineWidth=4;ctx.beginPath();ctx.moveTo(17,-8);ctx.lineTo(24,0);ctx.lineTo(17,8);ctx.stroke();}else if(s.tier===0){ctx.fillStyle="#b77956";ctx.fillRect(0,-4,15,8);ctx.fillStyle="#8b5e3c";ctx.fillRect(12,-6,8,12);ctx.strokeStyle="#5b3a29";ctx.lineWidth=1.2;ctx.strokeRect(12,-6,8,12);}else{ctx.strokeStyle=tier.color;ctx.lineWidth=5;ctx.beginPath();ctx.moveTo(0,0);ctx.lineTo(22,0);ctx.stroke();ctx.strokeStyle="#f8fafc";ctx.lineWidth=1;ctx.beginPath();ctx.moveTo(4,-1);ctx.lineTo(22,-1);ctx.stroke();ctx.fillStyle="#78350f";ctx.fillRect(-3,-3,7,6);}ctx.restore();ctx.restore();drawHealthBar(f);drawName(f);'''
rep(old_draw, new_draw, 'Steve mining animation')

old_status = '''      if(f.steve){const s=f.steve,t=steveTier(f);if(s.nether>0)return {ratio:clamp(1-s.nether/STEVE.netherTime,0,1),className:"skill-fill",text:`네더 탐험 · ${s.nether.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">귀환 시 네더라이트 · 체력 -30</div>'};if(s.tier<4){const r=s.resource,wait=r?Math.max(0,steveForceWait(f)-r.age):Math.max(0,s.resourceSpawnCd||0);return {ratio:t.need?clamp(s.count/t.need,0,1):1,className:"skill-fill",text:`${t.name} · ${t.resourceName} ${s.count}/${t.need}`,extraTextHtml:`<div class="status-skill-label">${r?(s.forcing?"자원으로 이동 중":`자동 이동까지 ${wait.toFixed(1)}초`):`다음 자원 ${wait.toFixed(1)}초`}</div>`};}if(s.tier===4)return {ratio:s.portal?clamp(s.portal.life/s.portal.maxLife,0,1):clamp(1-(s.portalCd||0)/STEVE.portalGap,0,1),className:"skill-fill",text:s.portal?`다이아 장비 · 포탈 ${s.portal.life.toFixed(1)}초`:`다이아 장비 · 포탈 대기 ${(s.portalCd||0).toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">포탈 접촉 → 네더 10초</div>'};return {ratio:1,className:"skill-fill",text:"네더라이트 장비 · 최종 단계",extraTextHtml:'<div class="status-skill-label">검17 · 일반 피해 20% 감소</div>'};}'''
new_status = '''      if(f.steve){const s=f.steve,t=steveTier(f);if(s.nether>0)return {ratio:clamp(1-s.nether/STEVE.netherTime,0,1),className:"skill-fill",text:`네더 탐험 · ${s.nether.toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">귀환 시 네더라이트 · 체력 -30</div>'};if(s.tier<4){const r=s.resource,spawn=Math.max(0,s.resourceSpawnCd||0),needTime=r?(STEVE.mineTime[r.type]||1):0,prog=r?(r.mineProgress||0):0,remain=Math.max(0,needTime-prog);return {ratio:s.mining&&needTime?clamp(prog/needTime,0,1):(t.need?clamp(s.count/t.need,0,1):1),className:"skill-fill",text:`${t.name} · ${t.resourceName} ${s.count}/${t.need}`,extraTextHtml:`<div class="status-skill-label">${r?(s.mining?`채굴 중 · ${remain.toFixed(1)}초 남음`:prog>0?`채굴 누적 ${prog.toFixed(1)}/${needTime.toFixed(1)}초`:`자원 접근 시 ${needTime.toFixed(1)}초 채굴`):`다음 자원 ${spawn.toFixed(1)}초`}</div>`};}if(s.tier===4)return {ratio:s.portal?clamp(s.portal.life/s.portal.maxLife,0,1):clamp(1-(s.portalCd||0)/STEVE.portalGap,0,1),className:"skill-fill",text:s.portal?`다이아 장비 · 포탈 ${s.portal.life.toFixed(1)}초`:`다이아 장비 · 포탈 대기 ${(s.portalCd||0).toFixed(1)}초`,extraTextHtml:'<div class="status-skill-label">포탈 접촉 → 네더 10초</div>'};return {ratio:1,className:"skill-fill",text:"네더라이트 장비 · 최종 단계",extraTextHtml:'<div class="status-skill-label">검17 · 일반 피해 20% 감소</div>'};}'''
rep(old_status, new_status, 'Steve status panel')

old_info = '      if(c.id==="steve_miner")return {damage:"맨손5 / 나무검7 / 돌검9 / 철검11 / 다이아검14 / 네더라이트검17",tick:"근접 공격1.05초 · 자원 1개만 존재 · 자동이동 5/7/9/11초 · 나무1→돌2→철3→다이아4 · 다음 자원1초 후 생성 · 네더10초",tip:"맨손에서 나무를 1개 얻어 나무 장비가 열린다. 이후 돌2개, 철3개, 다이아4개가 필요하며 단계가 높을수록 자동 이동까지 더 오래 기다린다. 습득 반경은 몸체+자원 반경에 20을 더한다. 기존 장비별 공격력과 피해 감소는 유지하며, 다이아 이후 랜덤 벽 포탈에 닿으면 10초 뒤 네더라이트로 귀환하고 현재 체력30을 잃는다."};'
new_info = '      if(c.id==="steve_miner")return {damage:"맨손5 / 나무검7 / 돌검9 / 철검11 / 다이아검14 / 네더라이트검17 · 공격 추가범위 +12/+18/+23/+28/+31/+34",tick:"근접 공격1.05초 · 채굴 나무0.6/돌0.9/철1.2/다이아1.6초 · 충돌 시 중단/진행도 유지 · 나무1→돌2→철3→다이아4 · 다음 자원1초 후 생성 · 네더10초",tip:"자원 추적 이동은 하지 않는다. 습득 반경은 몸체+자원 반경에 22를 더하며, 범위 안에서는 이동·공격을 멈추고 곡괭이질한다. 적 본체와 충돌하면 채굴이 즉시 중단되지만 진행도는 자원에 누적되어 다음 접촉 때 이어진다. 성장할수록 공격범위가 증가해 철 장비는 +28, 네더라이트는 +34가 된다. 기존 장비별 공격력·피해감소·HP170·네더 귀환 체력30 감소는 유지한다."};'
rep(old_info, new_info, 'Steve damage info')

patch_anchor = '''      const patchNotes = [
      "v223:'''
patch_new = '''      const patchNotes = [
      "v224: 스티브 채굴·공격범위 구조 조정. 자원 추적 자동이동을 완전히 제거하고 습득 추가반경을 20→22로 소폭 상향. 자원별 채굴시간을 나무0.6/돌0.9/철1.2/다이아1.6초로 적용하며 채굴 중 이동·공격 불가, 적 본체 충돌 시 채굴 중단, 같은 자원 재접촉 시 누적 진행도부터 이어서 채굴. 채굴 중 곡괭이질 모션 추가. 장비 단계별 공격 추가범위를 맨손12→나무18→돌23→철28→다이아31→네더라이트34로 확대해 성장할수록 사거리가 증가. 기존 공격력·피해감소·HP170·필요 자원 수·자원 재생성1초·네더10초·귀환 체력30 감소는 유지.",
      "v223:'''
rep(patch_anchor, patch_new, 'patch notes')

for forbidden in ('forceWaits:[5,7,9,11]', 'steveForceWait(f)', 'r.age>=steveForceWait(f)', 's.forcing'):
    if forbidden in s:
        raise SystemExit(f'old Steve tracking logic remains: {forbidden}')

for needle in (
    '볼배틀 리뉴얼 v224',
    'pickupBonus:22',
    'mineTime:{wood:.6,stone:.9,iron:1.2,diamond:1.6}',
    'attackReach:[12,18,23,28,31,34]',
    'steveMiningCollision',
    'mineProgress',
):
    if needle not in s:
        raise SystemExit(f'new Steve marker missing: {needle}')

p.write_text(s, encoding='utf-8')
print('Steve v224 patch applied successfully')
