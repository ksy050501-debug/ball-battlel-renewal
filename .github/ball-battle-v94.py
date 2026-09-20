from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:260]!r}")
    t=t.replace(old,new,count)

def insert_after(anchor, addition, count=1):
    global t
    n=t.count(anchor)
    if n!=count:
        raise SystemExit(f"expected anchor {count}, found {n}: {anchor[:220]!r}")
    t=t.replace(anchor,anchor+addition,count)

rep('<title>볼배틀 리뉴얼 v93</title>','<title>볼배틀 리뉴얼 v94</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v93</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v94</h1>')

# 1) 빚쟁이 공동승리: 상금으로만 상환, 남은 빚은 다음 도박까지 이월.
rep(
'''    function rewardJabamiWin(f, baseAmount, debtRecipients = []) {
      const debtMode = f.jabami.debt > 0;
      if (debtMode && debtRecipients.some(p => p?.alive && p !== f)) {
        transferJabamiDebt(f, debtRecipients);
      } else if (debtMode) {
        const cleared = Math.ceil(f.jabami.debt);
        f.jabami.debt = 0; f.jabami.debtUntilRound = 0;
        const recovery = Math.min(cleared, Math.ceil(f.maxHp * .2));
        if (recovery > 0) f.hp = Math.min(f.maxHp, f.hp + recovery);
        spawnFloatingText(f.x, f.y-f.r-48, `부전승 · 빚 ${cleared} 청산`, "#fde68a");
        log(`<strong>${escapeHtml(f.name)}</strong> 상대 전원 탈락 · 빚 ${cleared} 청산`, "도박");
      }
      gainJabamiWinnings(f, Math.round(baseAmount * (debtMode ? 1.5 : 1)));
      if (debtMode) spawnFloatingText(f.x, f.y-f.r-48, "빚쟁이 대역전!", "#fde68a");
      return debtMode;
    }''',
'''    function rewardJabamiWin(f, baseAmount, debtRecipients = [], mode = "normal") {
      const j=f.jabami;
      const debtMode = j.debt > 0;
      const liveRecipients=debtRecipients.filter(p=>p?.alive&&p!==f);
      let transferred=false;
      if (debtMode && liveRecipients.length) {
        transferJabamiDebt(f, liveRecipients);
        transferred=true;
      } else if (debtMode && mode==="autoWin") {
        const cleared = Math.ceil(j.debt);
        j.debt = 0; j.debtUntilRound = 0;
        const recovery = Math.min(cleared, Math.ceil(f.maxHp * .2));
        if (recovery > 0) f.hp = Math.min(f.maxHp, f.hp + recovery);
        spawnFloatingText(f.x, f.y-f.r-48, `부전승 · 빚 ${cleared} 청산`, "#fde68a");
        log(`<strong>${escapeHtml(f.name)}</strong> 상대 전원 탈락 · 빚 ${cleared} 청산`, "도박");
      }

      const debtBeforePrize=j.debt;
      gainJabamiWinnings(f, Math.round(baseAmount * (debtMode ? 1.5 : 1)));

      if(debtMode && mode==="tie" && !transferred){
        const paid=Math.max(0,Math.ceil(debtBeforePrize-j.debt));
        if(j.debt>0){
          j.debtUntilRound=Math.max(j.debtUntilRound||0,j.round+1);
          spawnFloatingText(f.x,f.y-f.r-48,`공동승리 · 빚 ${Math.ceil(j.debt)} 이월`,"#fda4af");
          log(`<strong>${escapeHtml(f.name)}</strong> 공동승리 · 상금으로 빚 ${paid} 상환 · 잔여 빚 ${Math.ceil(j.debt)} 다음 도박까지 이월`,"도박");
        }else{
          spawnFloatingText(f.x,f.y-f.r-48,"공동승리 · 빚 청산!","#fde68a");
          log(`<strong>${escapeHtml(f.name)}</strong> 공동승리 상금으로 빚 전액 청산`,"도박");
        }
      }else if(debtMode && (transferred || mode==="autoWin")){
        spawnFloatingText(f.x, f.y-f.r-48, "빚쟁이 대역전!", "#fde68a");
      }
      return debtMode;
    }'''
)

rep(
'''        rewardJabamiWin(f, prize, []);''',
'''        rewardJabamiWin(f, prize, [], "autoWin");'''
)

rep(
'''            if (p === f) rewardJabamiWin(f, prizeShare, ps.filter(x=>!winners.includes(x))); else p.hp = Math.min(p.maxHp, p.hp + prizeShare);''',
'''            if (p === f) {
              const debtRecipients=ps.filter(x=>!winners.includes(x));
              const allSurvivorsTied=winners.length>1&&debtRecipients.length===0;
              rewardJabamiWin(f,prizeShare,debtRecipients,allSurvivorsTied?"tie":"normal");
            } else p.hp = Math.min(p.maxHp, p.hp + prizeShare);'''
)

# 2) 쟈바미 전장 위 빚 기회 배지.
insert_after(
'''    function convertJabamiDamageToDebt(target, final, source, reason, color = "#fca5a5") {
      if (!target?.jabami || (target.jabami.debt <= 0 && final < target.hp)) return false;
      if (target.jabami.debt <= 0 && target.jabami.debtChances <= 0) return false;
      const value = Math.max(1, Math.round(final));
      const paid = target.jabami.debt > 0 ? 0 : Math.max(0, target.hp - 1);
      target.hp -= paid;
      if (!enterJabamiDebt(target, value - paid)) return false;
      target.damageTaken = (target.damageTaken || 0) + value;
      target.hitsTaken += 1; target.hitsTakenSkill += 1;
      if (source && source.alive && source !== target) {
        source.damageDealt = (source.damageDealt || 0) + value;
        source.hitsDealt += 1; source.hitsDealtSkill += 1;
      }
      spawnParticles(target.x, target.y, color, 6); spawnHitFlash(target.x, target.y, color, 26);
      spawnFloatingText(target.x, target.y - target.r - 8, `빚 +${value}`, color);
      return true;
    }''',
'''
    function drawJabamiDebtChanceBadge(f){
      if(f.portraitOnly||!f.jabami)return;
      const j=f.jabami,chances=Math.max(0,j.debtChances||0);
      const text=j.debt>0?`◆ 빚중 · 다음 기회 ×${chances}`:`◆ 빚 기회 ×${chances}`;
      ctx.save();
      ctx.font="900 10px system-ui";
      ctx.textAlign="center";ctx.textBaseline="middle";
      const w=Math.max(66,ctx.measureText(text).width+14),h=17;
      const x=f.x-w/2,y=f.y+f.r+24;
      ctx.fillStyle=j.debt>0?"rgba(127,29,29,.90)":chances>0?"rgba(88,28,135,.88)":"rgba(51,65,85,.82)";
      ctx.strokeStyle=j.debt>0?"#fca5a5":chances>0?"#f0abfc":"#94a3b8";
      ctx.lineWidth=1.2;roundRect(ctx,x,y,w,h,8,true,true);
      ctx.fillStyle="#fff";ctx.fillText(text,f.x,y+h/2+.2);
      ctx.restore();
    }'''
)

rep(
'''      ctx.restore();
      drawHealthBar(f); drawName(f);
    }
    function activeJabamiGameFor(f)''',
'''      ctx.restore();
      drawHealthBar(f); drawName(f); drawJabamiDebtChanceBadge(f);
    }
    function activeJabamiGameFor(f)'''
)

# 3) 정의의 아군 소환수 누적 전투분석 통계.
rep(
'''      f.duelist = { timer: 6, equipped: false, hand: [], deck: makeJusticeDeck(), drawCd: 0, playCd: 0, speech: "", speechTime: 0, blueSummoned: 0, fusionDone: false, fusion: null, emptyTimer: 0, obeliskUsed:false, godCinematic:null };''',
'''      f.duelist = { timer: 6, equipped: false, hand: [], deck: makeJusticeDeck(), drawCd: 0, playCd: 0, speech: "", speechTime: 0, blueSummoned: 0, fusionDone: false, fusion: null, emptyTimer: 0, obeliskUsed:false, godCinematic:null, summonDamageDealt:0, summonKills:0 };'''
)

insert_after(
'''    function justiceSummons(f,kind=null){return fighters.filter(e=>e.alive&&e.ownerId===f.id&&e.duelMonster&&(!kind||e.duelMonster.kind===kind));}''',
'''
    function archiveJusticeSummonStats(m){
      if(!m?.isSummon||!m.duelMonster||m.justiceStatsArchived)return;
      const owner=fighterById(m.ownerId);
      if(owner?.duelist){
        owner.duelist.summonDamageDealt=(owner.duelist.summonDamageDealt||0)+(m.damageDealt||0);
        owner.duelist.summonKills=(owner.duelist.summonKills||0)+(m.kills||0);
      }
      m.justiceStatsArchived=true;
    }
    function justiceSummonBattleStats(owner){
      if(!owner?.duelist)return {damage:0,kills:0};
      let damage=owner.duelist.summonDamageDealt||0,kills=owner.duelist.summonKills||0;
      fighters.filter(m=>m.isSummon&&m.ownerId===owner.id&&m.duelMonster&&!m.justiceStatsArchived).forEach(m=>{
        damage+=m.damageDealt||0;kills+=m.kills||0;
      });
      return {damage,kills};
    }'''
)

rep(
'''        fighters = fighters.filter(f => f.alive || !f.isSummon);
        checkEnd();''',
'''        fighters.filter(f=>f.isSummon&&!f.alive&&f.duelMonster).forEach(archiveJusticeSummonStats);
        fighters = fighters.filter(f => f.alive || !f.isSummon);
        checkEnd();'''
)

rep(
'''      const maxDamage = Math.max(1, ...rows.map(f => f.damageDealt || 0));
      const maxKills = Math.max(1, ...rows.map(f => f.kills || 0));
      body.innerHTML = rows.map(f => {
        const dealt = Math.round(f.damageDealt || 0);
        const taken = Math.round(f.damageTaken || 0);
        const kills = f.kills || 0;
        return `
          <div class="analysis-row">
            <div class="analysis-face" style="background:${f.color}">${escapeHtml(f.mark)}</div>
            <div>
              <div class="analysis-name">${escapeHtml(f.name)}</div>
              <div class="analysis-stat"><span>피해</span><div class="analysis-bar"><span style="width:${clamp(dealt / maxDamage * 100, 0, 100)}%"></span></div><span>${dealt}</span></div>
              <div class="analysis-stat"><span>처치</span><div class="analysis-bar"><span style="width:${clamp(kills / maxKills * 100, 0, 100)}%"></span></div><span>${kills}</span></div>
              <div class="analysis-stat"><span>피격</span><div class="analysis-bar"><span style="width:${clamp(taken / Math.max(1, f.maxHp) * 100, 0, 100)}%"></span></div><span>${taken}</span></div>
            </div>
          </div>`;
      }).join("");''',
'''      const summonStats=new Map(rows.map(f=>[f.id,f.baseId==="justice_ally"?justiceSummonBattleStats(f):{damage:0,kills:0}]));
      const maxDamage = Math.max(1, ...rows.flatMap(f => [f.damageDealt || 0, summonStats.get(f.id)?.damage || 0]));
      const maxKills = Math.max(1, ...rows.flatMap(f => [f.kills || 0, summonStats.get(f.id)?.kills || 0]));
      body.innerHTML = rows.map(f => {
        const dealt = Math.round(f.damageDealt || 0);
        const taken = Math.round(f.damageTaken || 0);
        const kills = f.kills || 0;
        const summon=summonStats.get(f.id)||{damage:0,kills:0};
        const summonHtml=f.baseId==="justice_ally"?`
              <div class="analysis-stat"><span>소환수 피해</span><div class="analysis-bar"><span style="width:${clamp(summon.damage / maxDamage * 100, 0, 100)}%"></span></div><span>${Math.round(summon.damage)}</span></div>
              <div class="analysis-stat"><span>소환수 처치</span><div class="analysis-bar"><span style="width:${clamp(summon.kills / maxKills * 100, 0, 100)}%"></span></div><span>${summon.kills}</span></div>`:"";
        return `
          <div class="analysis-row">
            <div class="analysis-face" style="background:${f.color}">${escapeHtml(f.mark)}</div>
            <div>
              <div class="analysis-name">${escapeHtml(f.name)}</div>
              <div class="analysis-stat"><span>피해</span><div class="analysis-bar"><span style="width:${clamp(dealt / maxDamage * 100, 0, 100)}%"></span></div><span>${dealt}</span></div>
              <div class="analysis-stat"><span>처치</span><div class="analysis-bar"><span style="width:${clamp(kills / maxKills * 100, 0, 100)}%"></span></div><span>${kills}</span></div>
              ${summonHtml}
              <div class="analysis-stat"><span>피격</span><div class="analysis-bar"><span style="width:${clamp(taken / Math.max(1, f.maxHp) * 100, 0, 100)}%"></span></div><span>${taken}</span></div>
            </div>
          </div>`;
      }).join("");'''
)

# 4) 오벨리스크 소환 진동 강화 + 대사 5.8초, 캔버스 위 지속 말풍선.
rep(
'''      triggerHitStop(1.15);screenShake=Math.max(screenShake,.85);playSound("explosion",1.5);
      d.speech="몬스터가 아니다, 신이다! 나와라 오벨리스크의 거신병!";d.speechTime=3.4;''',
'''      triggerHitStop(1.25);screenShake=Math.max(screenShake,1.8);playSound("explosion",1.5);
      d.speech="몬스터가 아니다, 신이다! 나와라 오벨리스크의 거신병!";d.speechTime=5.8;'''
)

rep(
'''      ctx.restore();drawHealthBar(f);drawName(f);
    }
    function initJabami(f) {''',
'''      ctx.restore();drawHealthBar(f);drawName(f);
      if(!f.portraitOnly&&d?.speechTime>0&&d.speech){
        const lines=d.speech.includes("오벨리스크")?["몬스터가 아니다, 신이다!","나와라 오벨리스크의 거신병!"]:[d.speech];
        ctx.save();ctx.font="900 11px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";
        const widths=lines.map(s=>ctx.measureText(s).width),w=Math.min(330,Math.max(...widths,80)+20),h=lines.length*15+12;
        const x=clamp(f.x-w/2,arena.x+5,arena.x2-w-5),y=Math.max(arena.y+5,f.y-f.r-72-h);
        ctx.fillStyle="rgba(15,23,42,.94)";ctx.strokeStyle="#93c5fd";ctx.lineWidth=1.5;roundRect(ctx,x,y,w,h,10,true,true);
        ctx.fillStyle="#dbeafe";lines.forEach((s,i)=>ctx.fillText(s,x+w/2,y+11+i*15));
        ctx.restore();
      }
    }
    function initJabami(f) {'''
)

rep(
'''      const patchNotes = [
      "v93: 팀전 HUD/상태창 개편.''',
'''      const patchNotes = [
      "v94: 쟈바미 공동승리·빚 기회 UI 및 정의의 아군 분석 개선. 빚쟁이 쟈바미가 하이카드 공동승리하고 실제 패자가 없을 때 더 이상 '상대 전원 탈락'으로 오인해 빚을 전액 청산하지 않음. 공동승리 몫(빚 상태 1.5배)은 우선 빚 상환에 쓰고, 남은 빚은 다음 도박까지 이월하며 전액 갚았을 때만 해제. 실제 패자가 있으면 기존처럼 패자에게 빚 이전, 진짜 상대 전멸 부전승은 기존 전액 청산 유지. 쟈바미 캐릭터 아래에 '빚 기회 ×N' 배지를 상시 표시하고 빚 상태에서는 '빚중 · 다음 기회 ×N'으로 표시. 정의의 아군은 전투분석에 소환수 누적 피해/처치 항목을 별도로 표시하며 이미 사라진 백룡·융합체·오벨리스크 기록도 누적 보존. 오벨리스크 릴리스 소환 시 화면 진동을 강화(1.8)하고 소환 대사를 5.8초간 말풍선으로 유지.",
      "v93: 팀전 HUD/상태창 개편.'''
)

p.write_text(t,encoding="utf-8")
