from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:260]!r}")
    t=t.replace(old,new,count)

def between(start,end,new):
    global t
    a=t.find(start)
    b=t.find(end,a)
    if a<0 or b<0:
        raise SystemExit(f"markers not found: {start!r} -> {end!r}")
    t=t[:a]+new+t[b:]

rep('<title>볼배틀 리뉴얼 v92</title>','<title>볼배틀 리뉴얼 v93</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v92</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v93</h1>')

rep(
'''    .hud {
      width: min(700px, 100%);
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-bottom: 10px;
    }''',
'''    .hud {
      width: min(700px, 100%);
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin-bottom: 10px;
    }

    .team-scoreboard {
      width: min(700px, 100%);
      display: none;
      grid-template-columns: minmax(0,1fr) auto minmax(0,1fr);
      gap: 10px;
      align-items: stretch;
      margin-bottom: 10px;
    }

    .team-scoreboard.show { display: grid; }

    .team-score-side {
      border-radius: 16px;
      padding: 10px 12px;
      border: 1px solid rgba(255,255,255,.10);
      background: rgba(15,23,42,.94);
      min-width: 0;
    }

    .team-score-side.a {
      border-color: rgba(96,165,250,.42);
      box-shadow: inset 3px 0 0 rgba(96,165,250,.78);
      text-align: left;
    }

    .team-score-side.b {
      border-color: rgba(248,113,113,.42);
      box-shadow: inset -3px 0 0 rgba(248,113,113,.78);
      text-align: right;
    }

    .team-score-name {
      font-size: 13px;
      font-weight: 1000;
      margin-bottom: 3px;
    }

    .team-score-side.a .team-score-name { color:#93c5fd; }
    .team-score-side.b .team-score-name { color:#fca5a5; }

    .team-score-main {
      font-size: 14px;
      font-weight: 900;
      color: #f8fafc;
    }

    .team-score-sub {
      margin-top: 3px;
      color: #94a3b8;
      font-size: 11px;
      white-space: nowrap;
      overflow: hidden;
      text-overflow: ellipsis;
    }

    .team-score-center {
      min-width: 112px;
      border-radius: 16px;
      padding: 8px 12px;
      display: flex;
      flex-direction: column;
      justify-content: center;
      align-items: center;
      border: 1px solid rgba(255,255,255,.12);
      background: rgba(2,6,23,.94);
    }

    .team-score-label {
      color:#94a3b8;
      font-size:10px;
      font-weight:900;
      letter-spacing:.08em;
      margin-bottom:1px;
    }

    .team-score-value {
      font-size: 27px;
      line-height: 1;
      font-weight: 1000;
      letter-spacing: .03em;
    }'''
)

rep(
'''    .status-panel {
      width: min(700px, 100%);
      margin-top: 10px;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }''',
'''    .status-panel {
      width: min(700px, 100%);
      margin-top: 10px;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 8px;
    }

    .status-panel.team-status-panel {
      align-items: start;
      grid-template-columns: minmax(0,1fr) minmax(0,1fr);
      gap: 10px;
    }

    .team-status-column {
      min-width: 0;
      display: flex;
      flex-direction: column;
      gap: 8px;
    }

    .team-status-heading {
      border-radius: 12px;
      padding: 6px 9px;
      font-size: 11px;
      font-weight: 1000;
      text-align: center;
      letter-spacing: .04em;
      background: rgba(15,23,42,.9);
      border: 1px solid rgba(255,255,255,.09);
    }

    .team-status-column.team-a .team-status-heading {
      color: #93c5fd;
      border-color: rgba(96,165,250,.36);
    }

    .team-status-column.team-b .team-status-heading {
      color: #fca5a5;
      border-color: rgba(248,113,113,.36);
    }

    .team-status-column.team-a .fighter-status.current {
      border-color: rgba(96,165,250,.62);
      box-shadow: 0 0 0 1px rgba(96,165,250,.16), 0 8px 22px rgba(37,99,235,.10);
    }

    .team-status-column.team-b .fighter-status.current {
      border-color: rgba(248,113,113,.62);
      box-shadow: 0 0 0 1px rgba(248,113,113,.14), 0 8px 22px rgba(220,38,38,.09);
    }

    .team-status-empty {
      padding: 10px;
      text-align: center;
      color: #64748b;
      font-size: 11px;
      border: 1px dashed rgba(255,255,255,.08);
      border-radius: 12px;
    }'''
)

rep(
'''      <div class="hud">
        <div class="hud-item">''',
'''      <div class="team-scoreboard" id="teamScoreboard">
        <div class="team-score-side a">
          <div class="team-score-name">A팀</div>
          <div class="team-score-main" id="teamAAlive">남은 인원 0/0</div>
          <div class="team-score-sub" id="teamACurrent">현재 · 대기</div>
        </div>
        <div class="team-score-center">
          <div class="team-score-label">탈락 스코어</div>
          <div class="team-score-value" id="teamScoreValue">0 : 0</div>
        </div>
        <div class="team-score-side b">
          <div class="team-score-name">B팀</div>
          <div class="team-score-main" id="teamBAlive">남은 인원 0/0</div>
          <div class="team-score-sub" id="teamBCurrent">현재 · 대기</div>
        </div>
      </div>

      <div class="hud">
        <div class="hud-item">'''
)

rep(
'''      const f = makeFighter(c, teamSpawnPosition(teamId), fighterSerial++, null, teamId);
      fighters.push(f);''',
'''      const f = makeFighter(c, teamSpawnPosition(teamId), fighterSerial++, null, teamId);
      f.teamOrder = state.next - 1;
      fighters.push(f);'''
)

rep(
'''      log(`팀전 시작! A팀 ${teamA.length}명 vs B팀 ${teamB.length}명 · 교대식 전투 · v64`, "시작");''',
'''      log(`팀전 시작! A팀 ${teamA.length}명 vs B팀 ${teamB.length}명 · 교대식 전투 · v93`, "시작");'''
)

# Add a scoreboard helper and replace updateHud.
between(
'''    function updateHud() {''',
'''    const heroLeonStages = [''',
'''    function teamBattleSummary() {
      const main=fighters.filter(f=>!f.isSummon);
      const result={};
      ["A","B"].forEach(teamId=>{
        const state=teamState?.[teamId];
        const total=state?state.queue.length:(teamId==="A"?teamA.length:teamB.length);
        const active=main.find(f=>f.alive&&f.teamId===teamId)||null;
        const used=state?state.next:0;
        const queued=state?Math.max(0,state.queue.length-state.next):Math.max(0,total-(active?1:0));
        const remaining=Math.max(0,queued+(active?1:0));
        result[teamId]={total,active,queued,remaining,eliminated:Math.max(0,total-remaining),used};
      });
      return result;
    }

    function updateTeamScoreboard() {
      const board=$("teamScoreboard");
      if(!board)return;
      if(battleMode!=="team"){
        board.classList.remove("show");
        return;
      }

      board.classList.add("show");
      const s=teamBattleSummary();
      $("teamAAlive").textContent=`남은 인원 ${s.A.remaining}/${s.A.total} · 탈락 ${s.A.eliminated}`;
      $("teamBAlive").textContent=`남은 인원 ${s.B.remaining}/${s.B.total} · 탈락 ${s.B.eliminated}`;
      $("teamACurrent").textContent=`현재 · ${s.A.active?s.A.active.name:"대기"}${s.A.queued>0?" · 대기 "+s.A.queued+"명":""}`;
      $("teamBCurrent").textContent=`현재 · ${s.B.active?s.B.active.name:"대기"}${s.B.queued>0?" · 대기 "+s.B.queued+"명":""}`;
      // A의 점수는 B팀 탈락 인원, B의 점수는 A팀 탈락 인원.
      $("teamScoreValue").textContent=`${s.B.eliminated} : ${s.A.eliminated}`;
    }

    function updateHud() {
      const main = fighters.filter(f => !f.isSummon);
      const aliveMain = main.filter(f => f.alive);

      updateTeamScoreboard();

      if (battleMode === "team") {
        const s=teamBattleSummary();
        if (running || fighters.length || teamState) {
          $("aliveText").textContent = `A ${s.A.remaining}/${s.A.total} · B ${s.B.remaining}/${s.B.total}`;
        } else {
          $("aliveText").textContent = `A ${teamA.length} · B ${teamB.length}`;
        }
      } else {
        $("aliveText").textContent = running || fighters.length ? `${aliveMain.length}/${main.length}` : `${selected.size}명`;
      }

      $("timeText").textContent = battleTime.toFixed(1);
      $("speedText").textContent = `${speedMultiplier}x`;
    }


    const heroLeonStages = ['''
)

# Refactor status renderer so team mode has fixed A-left / B-right columns and current fighters first.
between(
'''    function updateStatusPanel() {''',
'''    function enemiesOf(f) {''',
'''    function fighterStatusCardHtml(f, current=false) {
      const hpView = statusHpView(f);
      const hasStandardShield = f.shieldMax > 0;
      const hasWindShield = f.baseId === "wind_rio" && (f.rioWindShieldMax || 0) > 0;
      const hasJinBarrier = f.baseId === "thunder_jin" && (f.jinElectricBarrierMax || 0) > 0;
      const shieldValue = hasStandardShield ? (f.shieldHp || 0) : (hasWindShield ? (f.rioWindShield || 0) : (hasJinBarrier ? (f.jinElectricBarrier || 0) : 0));
      const shieldMaxValue = hasStandardShield ? f.shieldMax : (hasWindShield ? f.rioWindShieldMax : (hasJinBarrier ? f.jinElectricBarrierMax : 0));
      const shieldRatio = shieldMaxValue > 0 ? clamp(shieldValue / Math.max(1, shieldMaxValue), 0, 1) : 0;
      const shieldLabel = f.baseId === "flame_tori" ? "배리어" : f.baseId === "wind_rio" ? "바람보호막" : f.baseId === "thunder_jin" ? "전기배리어" : "방패";
      const shieldText = shieldRatio > 0 ? ` + ${shieldLabel} ${Math.ceil(shieldValue)}` : "";
      const shieldHtml = shieldMaxValue > 0 ? `
        <div class="bar"><div class="bar-fill shield-fill" style="width:${shieldRatio * 100}%"></div></div>
      ` : "";
      const statusClass = f.alive ? (current ? " current" : "") : " dead";
      const skill = skillProgressInfo(f);
      const skillHtml = skill ? `
        <div class="bar"><div class="bar-fill ${skill.className}" style="width:${skill.ratio * 100}%"></div></div>
        ${skill.extraBarsHtml || ""}
        <div class="status-skill-label">${skill.text}</div>
        ${skill.extraTextHtml || ""}
      ` : `<div class="status-skill-label">주기형 스킬 없음</div>`;
      const teamTag = battleMode==="team" && f.teamId ? `<span style="color:${f.teamId==="A"?"#93c5fd":"#fca5a5"}">${f.teamId}팀 · </span>` : "";

      return `
        <div class="fighter-status${statusClass}">
          <div class="status-top">
            <span class="status-name" style="color:${f.color}">${teamTag}${escapeHtml(f.name)}</span>
            <span class="status-num">${f.logo?.mode==="hulk"?"분노 ":""}${Math.ceil(Math.max(0, f.hp))}/${f.maxHp}${shieldText}</span>
          </div>
          <div class="bar hp-delay-bar">
            <div class="bar-fill ${f.logo?.mode==="hulk"?"logo-rage-fill":"hp-fill"}" style="width:${hpView.actualRatio * 100}%"></div>
            <div class="bar-fill hp-damage-fill" style="left:${hpView.actualRatio * 100}%; width:${hpView.pendingRatio * 100}%"></div>
          </div>
          ${shieldHtml}
          ${skillHtml}
        </div>
      `;
    }

    function teamStatusColumnHtml(teamId, main) {
      const side=main
        .filter(f=>f.teamId===teamId)
        .sort((a,b)=>{
          if(a.alive!==b.alive)return a.alive?-1:1;
          return (a.teamOrder??999)-(b.teamOrder??999);
        });
      const active=side.find(f=>f.alive)||null;
      const cards=side.length
        ? side.map(f=>fighterStatusCardHtml(f,!!active&&f.id===active.id)).join("")
        : '<div class="team-status-empty">아직 출전한 캐릭터가 없습니다.</div>';
      return `
        <div class="team-status-column team-${teamId.toLowerCase()}">
          <div class="team-status-heading">${teamId}팀 · ${active?"현재 "+escapeHtml(active.name):"대기"}</div>
          ${cards}
        </div>
      `;
    }

    function updateStatusPanel() {
      const panel = $("statusPanel");
      if (!panel) return;

      const main = fighters.filter(f => !f.isSummon);
      if (main.length === 0) {
        panel.innerHTML = "";
        panel.classList.toggle("team-status-panel",battleMode==="team");
        statusHpState = {};
        return;
      }

      const activeIds = new Set(main.map(f => f.id));
      Object.keys(statusHpState).forEach(id => {
        if (!activeIds.has(id)) delete statusHpState[id];
      });

      if(battleMode==="team"){
        panel.classList.add("team-status-panel");
        panel.innerHTML=teamStatusColumnHtml("A",main)+teamStatusColumnHtml("B",main);
        return;
      }

      panel.classList.remove("team-status-panel");
      panel.innerHTML = main.map(f => fighterStatusCardHtml(f,false)).join("");
    }

    function enemiesOf(f) {'''
)

rep(
'''      const patchNotes = [
      "v92: 앤드럼 그루브 제동 강화.''',
'''      const patchNotes = [
      "v93: 팀전 HUD/상태창 개편. 팀전에서 경기장 상단에 A/B 전용 스코어보드를 추가해 탈락 스코어(A 점수=B 탈락 인원, B 점수=A 탈락 인원), 각 팀 남은 인원/전체 인원·탈락 수·현재 출전 캐릭터·대기 인원을 실시간 표시. 상태창은 팀전에서 좌측 A팀/우측 B팀으로 고정 분리하고 현재 출전 캐릭터를 각 열 최상단에 유지, 사망 캐릭터는 해당 팀 열 아래쪽에 출전 순서대로 누적되도록 변경. 개인전 상태창 동작은 유지.",
      "v92: 앤드럼 그루브 제동 강화.'''
)

p.write_text(t,encoding="utf-8")
