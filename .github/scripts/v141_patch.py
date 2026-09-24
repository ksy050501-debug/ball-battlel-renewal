from pathlib import Path

p=Path('index.html')
s=p.read_text(encoding='utf-8')

def once(old,new,label):
    global s
    n=s.count(old)
    if n!=1:
        raise SystemExit(f'{label}: expected 1 marker, found {n}')
    s=s.replace(old,new,1)

once('볼배틀 리뉴얼 v140','볼배틀 리뉴얼 v141','version')

dummy='''      { id: "dummy_unit", name: "훈련용 더미", mark: "木", role: "더미", color: "#9ca3af", hp: 500, attack: 0, speed: 2.35, range: 0, simOnly: true,'''
koopa='''      { id:"koopa_king", name:"쿱하", mark:"K", role:"게임", color:"#65a30d", hp:240, attack:0, speed:2.35, range:0,
        skillName:"등껍질 돌진 · 회전 불기둥", condition:"등껍질 11초 주기 · 불기둥 9초 주기 · 저체력일수록 불기둥 1→4개", desc:"거대한 몸집의 마왕형 캐릭터. 등껍질 돌진으로 적을 강하게 날리고 벽충돌 피해를 만들며, 마지막 3초에는 상대를 추적한다. 돌진이 끝나면 제자리에서 3초 기절한다. 맵 중앙을 축으로 회전하는 불기둥은 체력이 낮을수록 늘어난다." },
'''
once(dummy,koopa+dummy,'character entry')

once('''        dummy_unit: {
          damage: "없음",''','''        koopa_king: {
          damage: "등껍질 충돌 14 + 강넉백 · 넉백 후 벽충돌 8 / 회전 불기둥 접촉 6 + 화상 1×4",
          tick: "등껍질 11초 주기·6초 지속·종료 후 3초 기절 / 불기둥 9초 주기·4.5초 지속",
          tip: "등껍질은 마지막 3초 동안 적을 추적한다. 중앙 회전 불기둥은 HP 75% 초과 1개, 50~75% 2개, 25~50% 3개, 25% 이하 4개다. 넉백 저항은 없다."
        },
        dummy_unit: {
          damage: "없음",''','damage info')

once('''        if (c.id === "mario_plumber") initMario(preview);
        if (c.id === "bald_cape") initBaldCape(preview);''','''        if (c.id === "mario_plumber") initMario(preview);
        if (c.id === "koopa_king") initKoopa(preview);
        if (c.id === "bald_cape") initBaldCape(preview);''','preview init')

once('''      if (c.id === "mario_plumber") initMario(fighter);
      if (c.id === "bald_cape") initBaldCape(fighter);''','''      if (c.id === "mario_plumber") initMario(fighter);
      if (c.id === "koopa_king") initKoopa(fighter);
      if (c.id === "bald_cape") initBaldCape(fighter);''','fighter init')

koopa_code=r'''
    const KOOPA = {
      bodyR:25, shellPeriod:11, shellDuration:6, shellTrackAt:3, shellSpeedMult:1.9, shellTurn:5.0,
      shellDamage:14, shellKnock:720, shellFlight:.65, shellHitCd:.55, shellWallDamage:8, shellWallWindow:.72, recoveryStun:3,
      firePeriod:9, fireDuration:4.5, fireDamage:6, fireBurnDamage:1, fireBurnTicks:4, fireBurnTick:.6,
      fireHitCd:.55, fireTurn:Math.PI*105/180, fireWidth:12
    };
    function initKoopa(f){
      f.r=KOOPA.bodyR;
      f.koopa={shellCd:KOOPA.shellPeriod,shellActive:false,shellTime:0,recovery:0,hitCd:{},fireCd:KOOPA.firePeriod,fire:null,baseSpeed:f.baseSpeed||f.speed||2.35};
    }
    function koopaFireCount(f){const q=f.maxHp>0?f.hp/f.maxHp:1;return q>.75?1:q>.50?2:q>.25?3:4;}
    function koopaStartShell(f){
      const k=f.koopa;if(!k||k.shellActive||k.recovery>0||f.stun>0)return false;
      k.shellActive=true;k.shellTime=KOOPA.shellDuration;k.shellCd=KOOPA.shellPeriod;k.hitCd={};
      const mag=Math.hypot(f.vx,f.vy)||1,a=mag>.01?Math.atan2(f.vy,f.vx):rand(0,Math.PI*2),v=k.baseSpeed*44*KOOPA.shellSpeedMult;
      f.vx=Math.cos(a)*v;f.vy=Math.sin(a)*v;
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-30,"등껍질 돌진!","#bef264");playSound("wind",1.05);}
      return true;
    }
    function koopaEndShell(f){
      const k=f?.koopa;if(!k?.shellActive)return;
      k.shellActive=false;k.shellTime=0;k.recovery=KOOPA.recoveryStun;f.vx=0;f.vy=0;applyStun(f,KOOPA.recoveryStun);
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-34,"기절 3초","#fde68a");spawnBlast(f.x,f.y,48,"#84cc16");}
    }
    function koopaNormalizeShellSpeed(f){
      const k=f.koopa,v=k.baseSpeed*44*KOOPA.shellSpeedMult,mag=Math.hypot(f.vx,f.vy)||1,a=mag>.01?Math.atan2(f.vy,f.vx):rand(0,Math.PI*2);
      f.vx=Math.cos(a)*v;f.vy=Math.sin(a)*v;
    }
    function koopaTrackShell(f,dt){
      const k=f.koopa,target=nearestEnemy(f).enemy;if(!target){koopaNormalizeShellSpeed(f);return;}
      const wanted=Math.atan2(target.y-f.y,target.x-f.x),cur=Math.atan2(f.vy,f.vx),delta=Math.atan2(Math.sin(wanted-cur),Math.cos(wanted-cur));
      const a=cur+clamp(delta,-KOOPA.shellTurn*dt,KOOPA.shellTurn*dt),v=k.baseSpeed*44*KOOPA.shellSpeedMult;
      f.vx=Math.cos(a)*v;f.vy=Math.sin(a)*v;
    }
    function koopaStartFire(f){
      const k=f.koopa;if(!k||k.fire||f.stun>0)return false;
      k.fire={life:KOOPA.fireDuration,angle:rand(0,Math.PI*2),hitCd:{}};k.fireCd=KOOPA.firePeriod;
      if(!fastSimMode){spawnFloatingText(f.x,f.y-f.r-48,`회전 불기둥 ${koopaFireCount(f)}개`,`#fb923c`);playSound("fireball",1.1);}
      return true;
    }
    function koopaApplyBurn(target,source){
      if(!target?.alive||hasHarmfulImmunity(target))return false;
      if(!target.burningTicks)target.burningTicks=[];
      const duration=KOOPA.fireBurnTick*KOOPA.fireBurnTicks,existing=target.burningTicks.find(b=>b.kind==="koopaFire"&&b.source===source);
      if(existing){existing.t=duration;existing.next=Math.min(existing.next>0?existing.next:KOOPA.fireBurnTick,KOOPA.fireBurnTick);existing.power=KOOPA.fireBurnDamage;existing.tick=KOOPA.fireBurnTick;existing.ticksLeft=KOOPA.fireBurnTicks;return true;}
      target.burningTicks.push({kind:"koopaFire",t:duration,next:KOOPA.fireBurnTick,power:KOOPA.fireBurnDamage,source,tick:KOOPA.fireBurnTick,ticksLeft:KOOPA.fireBurnTicks});return true;
    }
    function koopaSegmentDistance(x1,y1,x2,y2,x,y){
      const dx=x2-x1,dy=y2-y1,l2=dx*dx+dy*dy||1,t=clamp(((x-x1)*dx+(y-y1)*dy)/l2,0,1),px=x1+dx*t,py=y1+dy*t;return Math.hypot(x-px,y-py);
    }
    function updateKoopaFire(f,dt){
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
    }
    function updateKoopa(f,dt){
      const k=f?.koopa;if(!k||!f.alive)return;
      k.shellCd=Math.max(0,k.shellCd-dt);k.fireCd=Math.max(0,k.fireCd-dt);k.recovery=Math.max(0,k.recovery-dt);
      Object.keys(k.hitCd).forEach(id=>{k.hitCd[id]=Math.max(0,(k.hitCd[id]||0)-dt);});
      updateKoopaFire(f,dt);
      if(k.shellActive){k.shellTime=Math.max(0,k.shellTime-dt);if(k.shellTime<=0){koopaEndShell(f);return;}if(k.shellTime<=KOOPA.shellTrackAt)koopaTrackShell(f,dt);else koopaNormalizeShellSpeed(f);}
      else if(k.shellCd<=0&&k.recovery<=0&&f.stun<=0)koopaStartShell(f);
      if(k.fireCd<=0&&!k.fire&&f.stun<=0)koopaStartFire(f);
    }
    function koopaShellContact(source,target){
      const k=source?.koopa;if(!k?.shellActive||!target?.alive||!areEnemies(source,target)||(k.hitCd[target.id]||0)>0)return false;
      const dx=target.x-source.x,dy=target.y-source.y,d=Math.hypot(dx,dy)||1,dealt=damage(target,KOOPA.shellDamage,source,"등껍질충돌");k.hitCd[target.id]=KOOPA.shellHitCd;
      if(dealt>0&&target.alive){target.vx=dx/d*KOOPA.shellKnock;target.vy=dy/d*KOOPA.shellKnock;target.punchFlight=Math.max(target.punchFlight||0,KOOPA.shellFlight);target.punchSource=null;target.punchWallPower=0;target.punchWallHits=0;target.koopaWallCrash={sourceId:source.id,t:KOOPA.shellWallWindow};koopaNormalizeShellSpeed(source);}
      if(!fastSimMode){spawnHitFlash(target.x,target.y,"#bef264",58);spawnParticles(target.x,target.y,"#84cc16",10);}
      return dealt>0;
    }
    function koopaWallCrash(f){
      const crash=f?.koopaWallCrash;if(!crash)return false;const source=fighterById(crash.sourceId);f.koopaWallCrash=null;
      if(!source?.alive||!areEnemies(source,f))return false;const dealt=damage(f,KOOPA.shellWallDamage,source,"등껍질 벽충돌");
      if(dealt>0&&!fastSimMode){spawnFloatingText(f.x,f.y-f.r-28,"벽충돌 -"+KOOPA.shellWallDamage,"#bef264");spawnHitFlash(f.x,f.y,"#84cc16",48);}return dealt>0;
    }
    function drawKoopaFirePillars(){
      const c=arenaCenter();fighters.filter(f=>f.alive&&f.koopa?.fire).forEach(f=>{const fire=f.koopa.fire,count=koopaFireCount(f),len=arena.size*.72;ctx.save();ctx.beginPath();ctx.rect(arena.x,arena.y,arena.size,arena.size);ctx.clip();ctx.globalCompositeOperation="lighter";
        for(let i=0;i<count;i++){const a=fire.angle+i*Math.PI*2/count;for(let j=1;j<=18;j++){const t=j/18,x=c.x+Math.cos(a)*len*t,y=c.y+Math.sin(a)*len*t,r=7+3*Math.sin(battleTime*12+j);ctx.globalAlpha=.72;ctx.shadowColor="#f97316";ctx.shadowBlur=16;ctx.fillStyle=j%3===0?"#fde68a":"#f97316";ctx.beginPath();ctx.arc(x,y,r,0,Math.PI*2);ctx.fill();ctx.globalAlpha=.42;ctx.fillStyle="#ef4444";ctx.beginPath();ctx.arc(x-Math.cos(a)*5,y-Math.sin(a)*5,r*.72,0,Math.PI*2);ctx.fill();}}
        ctx.restore();});
    }
    function drawKoopaCharacter(f){
      const k=f.koopa||{},shell=!!k.shellActive,stunned=(k.recovery||0)>0;ctx.save();ctx.translate(f.x,f.y);ctx.scale(f.r/25,f.r/25);
      if(shell){ctx.rotate(battleTime*9);ctx.fillStyle="#3f6212";ctx.strokeStyle="#d9f99d";ctx.lineWidth=2;ctx.beginPath();ctx.arc(0,0,20,0,Math.PI*2);ctx.fill();ctx.stroke();for(let i=0;i<8;i++){const a=i*Math.PI/4;ctx.save();ctx.rotate(a);ctx.fillStyle="#fef3c7";ctx.beginPath();ctx.moveTo(18,-4);ctx.lineTo(29,0);ctx.lineTo(18,4);ctx.closePath();ctx.fill();ctx.restore();}ctx.fillStyle="#84cc16";ctx.beginPath();ctx.arc(0,0,12,0,Math.PI*2);ctx.fill();}
      else{ctx.fillStyle="#d97706";ctx.strokeStyle="#422006";ctx.lineWidth=1.6;ctx.beginPath();ctx.ellipse(0,5,17,20,0,0,Math.PI*2);ctx.fill();ctx.stroke();ctx.fillStyle="#3f6212";ctx.beginPath();ctx.ellipse(0,7,14,16,0,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#bef264";ctx.stroke();for(let i=0;i<5;i++){const a=-Math.PI*.8+i*Math.PI*.4;ctx.save();ctx.rotate(a);ctx.fillStyle="#fef3c7";ctx.beginPath();ctx.moveTo(13,-3);ctx.lineTo(22,0);ctx.lineTo(13,3);ctx.closePath();ctx.fill();ctx.restore();}ctx.fillStyle="#f59e0b";ctx.beginPath();ctx.ellipse(0,-15,14,11,0,0,Math.PI*2);ctx.fill();ctx.strokeStyle="#7c2d12";ctx.stroke();ctx.fillStyle="#fef3c7";for(const x of [-7,7]){ctx.beginPath();ctx.moveTo(x-3,-23);ctx.lineTo(x,-31);ctx.lineTo(x+3,-23);ctx.closePath();ctx.fill();}ctx.fillStyle="#f8fafc";ctx.beginPath();ctx.ellipse(-5,-17,3,4,0,0,Math.PI*2);ctx.ellipse(5,-17,3,4,0,0,Math.PI*2);ctx.fill();ctx.fillStyle="#111827";ctx.beginPath();ctx.arc(-4,-17,1.2,0,Math.PI*2);ctx.arc(4,-17,1.2,0,Math.PI*2);ctx.fill();ctx.fillStyle="#fef3c7";ctx.beginPath();ctx.moveTo(-8,-9);ctx.lineTo(-3,-5);ctx.lineTo(0,-10);ctx.lineTo(3,-5);ctx.lineTo(8,-9);ctx.closePath();ctx.fill();}
      if(stunned){ctx.fillStyle="#fde047";for(let i=0;i<3;i++){const a=battleTime*3+i*Math.PI*2/3;ctx.beginPath();ctx.arc(Math.cos(a)*25,Math.sin(a)*8-27,3,0,Math.PI*2);ctx.fill();}}
      ctx.restore();drawHealthBar(f);drawName(f);
    }
'''
once('''    const MARIO = {''',koopa_code+'\n    const MARIO = {','koopa code')

once('''      f.marioItemSlow = Math.max(0, (f.marioItemSlow || 0) - dt);''','''      f.marioItemSlow = Math.max(0, (f.marioItemSlow || 0) - dt);
      if(f.koopaWallCrash){f.koopaWallCrash.t=Math.max(0,(f.koopaWallCrash.t||0)-dt);if(f.koopaWallCrash.t<=0)f.koopaWallCrash=null;}''','wall crash timer')

once('''      if (f.mario) updateMario(f, dt);
      if (!f.alive) return;''','''      if (f.mario) updateMario(f, dt);
      if (f.koopa) updateKoopa(f, dt);
      if (!f.alive) return;''','koopa update hook')

once('''          || f.baldCape?.dash > 0 || f.baldCape?.serious?.timer > 0 || f.baldCape?.combo
          || f.baseId === "wind_rio") return;''','''          || f.baldCape?.dash > 0 || f.baldCape?.serious?.timer > 0 || f.baldCape?.combo
          || f.koopa?.shellActive || f.baseId === "wind_rio") return;''','speed recovery exclusion')

once('''        baldCapeWallBounce(f);

        if (electricWall) {''','''        baldCapeWallBounce(f);
        if(f.koopaWallCrash)koopaWallCrash(f);

        if (electricWall) {''','wall crash hook')

once('''              marioKartContact(a, b);
              marioKartContact(b, a);
              newhelloContact(a, b);''','''              marioKartContact(a, b);
              marioKartContact(b, a);
              koopaShellContact(a, b);
              koopaShellContact(b, a);
              newhelloContact(a, b);''','shell contact hook')

once('''      if (f.marioBlock) { drawMarioBlock(f); return; }
      if (f.mario) { drawMarioCharacter(f); return; }
      if (f.baldCape) { drawBaldCapeCharacter(f); return; }''','''      if (f.marioBlock) { drawMarioBlock(f); return; }
      if (f.mario) { drawMarioCharacter(f); return; }
      if (f.koopa) { drawKoopaCharacter(f); return; }
      if (f.baldCape) { drawBaldCapeCharacter(f); return; }''','draw fighter hook')

once('''    function skillProgressInfo(f) {
      if(f.mario){''','''    function skillProgressInfo(f) {
      if(f.koopa){
        const k=f.koopa,fire=k.fire,fireCount=koopaFireCount(f);
        if(k.recovery>0)return {ratio:clamp(k.recovery/KOOPA.recoveryStun,0,1),className:"rage-fill",text:`등껍질 후 기절 ${k.recovery.toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">불기둥 ${fire?`발동 중 · ${fireCount}개 · ${fire.life.toFixed(1)}초`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};
        if(k.shellActive)return {ratio:clamp(k.shellTime/KOOPA.shellDuration,0,1),className:"skill-fill",text:`등껍질 돌진 ${k.shellTime.toFixed(1)}초${k.shellTime<=KOOPA.shellTrackAt?" · 추적 중":""}`,extraTextHtml:`<div class="status-skill-label">종료 후 3초 기절 · 불기둥 ${fire?`${fireCount}개 발동 중`:`${Math.max(0,k.fireCd).toFixed(1)}초 후`}</div>`};
        return {ratio:clamp(1-Math.max(0,k.shellCd)/KOOPA.shellPeriod,0,1),className:"skill-fill",text:`등껍질 ${Math.max(0,k.shellCd).toFixed(1)}초`,extraTextHtml:`<div class="status-skill-label">불기둥 ${fire?`${fireCount}개 · ${fire.life.toFixed(1)}초`:`${Math.max(0,k.fireCd).toFixed(1)}초`} · 현재 HP 단계 ${fireCount}개</div>`};
      }
      if(f.mario){''','status hook')

once('''      drawLisaWaves();
      drawJabamiGames();''','''      drawLisaWaves();
      drawKoopaFirePillars();
      drawJabamiGames();''','fire draw hook')

once('''      return ["질풍돌파", "풍압충돌", "분신충돌", "회전격", "불사회전격", "피의난타", "철벽후려치기", "철벽충돌", "용사검격", "초보검사검격", "견습기사검격", "기사검격", "전설원공격", "전설검기", "용사절반참"].includes(reason);''','''      return ["질풍돌파", "풍압충돌", "분신충돌", "회전격", "불사회전격", "피의난타", "철벽후려치기", "철벽충돌", "등껍질충돌", "등껍질 벽충돌", "용사검격", "초보검사검격", "견습기사검격", "기사검격", "전설원공격", "전설검기", "용사절반참"].includes(reason);''','collision damage classification')

once('''      const patchNotes = [
      "v132:''','''      const patchNotes = [
      "v141: 게임 신캐 쿱하 추가. HP240·일반보다 큰 반지름25·넉백 저항 없음. 11초 주기 등껍질 돌진은 6초간 이속×1.9, 충돌14+강넉백, 넉백 후 벽충돌8, 마지막3초 추적 후 제자리 정지·3초 기절. 9초 주기 회전 불기둥은 4.5초 동안 맵 중앙축을 회전하며 HP 단계에 따라 1~4개, 접촉6+화상1×4. 캡틴 방패11·병장 와이어15 유지.",
      "v132:''','patch note')

p.write_text(s,encoding='utf-8')
