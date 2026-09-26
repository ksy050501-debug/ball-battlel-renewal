from pathlib import Path
import re

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def one(old,new,label):
    global s
    if old not in s:
        raise SystemExit('missing '+label)
    s=s.replace(old,new,1)

one('<title>볼배틀 리뉴얼 v164</title>','<title>볼배틀 리뉴얼 v165</title>','title')
one('<h1 id="mainTitle">볼배틀 리뉴얼 v164</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v165</h1>','heading')

old='''    const COYOTE = {
      trailLife:3, trailEvery:.18, trailRadius:24, trailDamage:1, trailTick:.5,
      contactDamage:8, contactCooldown:1, flingDuration:.42, flingGap:10
    };'''
new='''    const COYOTE = {
      trailLife:3, trailEvery:.18, trailRadius:24, trailDamage:1, trailTick:.5,
      contactDamage:8, contactCooldown:1, flingDuration:.42, flingGap:10,
      liandryAt:30, liandryTicks:3, rylaiAt:90, rylaiSlowMult:.8
    };'''
one(old,new,'coyote constants')

one('f.coyote={trailCd:0,contactCd:new Map(),dirX:1,dirY:0};',
    'f.coyote={trailCd:0,contactCd:new Map(),dirX:1,dirY:0,liandry:false,rylai:false};','coyote init')

marker='''      const c=f.coyote;
      for(const [id,cd] of c.contactCd){const n=cd-dt;if(n<=0)c.contactCd.delete(id);else c.contactCd.set(id,n);}'''
insert='''      const c=f.coyote;
      if(!c.liandry&&battleTime>=COYOTE.liandryAt){
        c.liandry=true;
        if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-36,"리안드리 획득!","#f97316");spawnBlast(f.x,f.y,48,"#f97316");}
      }
      if(!c.rylai&&battleTime>=COYOTE.rylaiAt){
        c.rylai=true;
        if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-36,"라일라이 획득!","#60a5fa");spawnBlast(f.x,f.y,52,"#60a5fa");}
      }
      for(const [id,cd] of c.contactCd){const n=cd-dt;if(n<=0)c.contactCd.delete(id);else c.contactCd.set(id,n);}'''
one(marker,insert,'coyote item acquisition')

pat=r'    function updateCoyoteTrails\(dt\)\{.*?\n    \}\n    function coyoteContact\(f,target\)\{'
repl='''    function coyotePoisonSlowMultiplier(f){
      const p=f?.coyotePoison;if(!p)return 1;
      const source=fighterById(p.sourceId);
      return source?.coyote?.rylai?COYOTE.rylaiSlowMult:1;
    }
    function updateCoyoteTrails(dt){
      coyoteTrails.forEach(t=>t.life-=dt);
      coyoteTrails=coyoteTrails.filter(t=>t.life>0);
      fighters.forEach(target=>{
        target.coyotePoisonCd=Math.max(0,(target.coyotePoisonCd||0)-dt);
        if(!target.alive){target.coyotePoison=null;return;}
        const hit=coyoteTrails.find(t=>t.owner&&t.owner!==target&&areEnemies(t.owner,target)&&Math.hypot(target.x-t.x,target.y-t.y)<=COYOTE.trailRadius+target.r);
        if(hit){
          const owner=hit.owner;
          if(owner?.coyote?.liandry){
            target.coyotePoison={sourceId:owner.id,ticksLeft:COYOTE.liandryTicks,next:COYOTE.trailTick};
          }
          if(target.coyotePoisonCd<=0){
            const dealt=damage(target,COYOTE.trailDamage,owner,"독방구");
            if(dealt>0){target.coyotePoisonCd=COYOTE.trailTick;if(!fastSimMode)spawnParticles(target.x,target.y,"#84cc16",3);}
          }
          return;
        }
        const poison=target.coyotePoison;if(!poison)return;
        const source=fighterById(poison.sourceId);
        if(!source?.coyote?.liandry||poison.ticksLeft<=0){target.coyotePoison=null;return;}
        poison.next-=dt;
        while(poison.next<=0&&poison.ticksLeft>0&&target.alive){
          const dealt=damage(target,COYOTE.trailDamage,source,"리안드리 잔류독");
          poison.ticksLeft-=1;poison.next+=COYOTE.trailTick;
          if(dealt>0&&!fastSimMode)spawnParticles(target.x,target.y,"#f97316",3);
        }
        if(poison.ticksLeft<=0)target.coyotePoison=null;
      });
    }
    function coyoteContact(f,target){'''
s,n=re.subn(pat,repl,s,count=1,flags=re.S)
if n!=1:
    raise SystemExit('coyote trail function replacement failed')

old_line='      const marioItemSlow = (f.marioItemSlow || 0) > 0 ? MARIO.bananaSlowMult : 1;'
count=s.count(old_line)
if count<2:
    raise SystemExit(f'expected >=2 mario slow lines, got {count}')
s=s.replace(old_line,old_line+'\n      const coyotePoisonSlow = coyotePoisonSlowMultiplier(f);')
s=s.replace(' * timedCcSlow;',' * timedCcSlow * coyotePoisonSlow;',1)
s=s.replace(' * coldAuraSlow * marioItemSlow)) return;',' * coldAuraSlow * marioItemSlow * coyotePoisonSlow)) return;',1)
s=s.replace(' * coldAuraSlow * marioItemSlow * dt;',' * coldAuraSlow * marioItemSlow * coyotePoisonSlow * dt;',2)

old_card='condition:"이동 경로에 3초 독방구 · 접촉 시 8피해 후 0.42초에 걸쳐 뒤로 넘김", desc:"신지도를 모티브로 한 교란형 캐릭터. 이동한 자리에 잠시 독방구 흔적을 남겨 적에게 지속 피해를 주고, 직접 부딪히면 피해를 준 뒤 상대를 자신의 몸 위로 넘겨 진행방향 뒤쪽에 착지시킨다."'
new_card='condition:"이동 경로에 3초 독방구 · 접촉8+넘기기 · 30초 리안드리 · 90초 라일라이", desc:"신지도를 모티브로 한 교란형 캐릭터. 이동 경로에 독방구를 남기고 접촉한 적을 몸 뒤로 넘긴다. 30초에는 리안드리를 얻어 독에서 벗어난 뒤에도 3틱이 이어지고, 90초에는 라일라이를 얻어 독이 지속되는 적의 이동속도를 20% 낮춘다."'
one(old_card,new_card,'coyote card')

note='      "v165: 코요테드 성장 아이템 추가. 전투 30초에 리안드리를 획득해 독방구 영역을 벗어난 적에게 기존 피해1을 0.5초 간격으로 3틱 더 지속한다. 90초에는 라일라이를 획득해 독방구 안 또는 리안드리 잔류독이 지속 중인 적의 이동속도를 20% 감소시킨다. 기본 독 피해1·접촉8·HP170·0.42초 넘기기는 유지.",\n'
one('      const patchNotes = [\n','      const patchNotes = [\n'+note,'patch note')

p.write_text(s,encoding='utf-8')
