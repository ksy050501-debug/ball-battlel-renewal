from pathlib import Path
p=Path("index.html")
t=p.read_text(encoding="utf-8")

def rep(old,new,count=1):
    global t
    n=t.count(old)
    if n!=count:
        raise SystemExit(f"expected {count}, found {n}: {old[:260]!r}")
    t=t.replace(old,new,count)

rep('<title>볼배틀 리뉴얼 v95</title>','<title>볼배틀 리뉴얼 v96</title>')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v95</h1>','<h1 id="mainTitle">볼배틀 리뉴얼 v96</h1>')

# 쟈바미 다이아몬드: 체력바 중앙 정렬 -> 왼쪽 끝부터 오른쪽으로 쌓기.
rep(
'''          const size=5,gap=5,total=chances*size+Math.max(0,chances-1)*gap;
          const start=f.x-total/2+size/2;
          const dy=y+h+8;''',
'''          const size=5,gap=5;
          const start=x+size/2;
          const dy=y+h+8;'''
)

# 정의의 아군 캐릭터 위 말풍선 제거.
old='''      ctx.restore();drawHealthBar(f);drawName(f);
      if(!f.portraitOnly&&d?.obeliskSpeechUntil>performance.now()&&d.speech){
        const lines=["몬스터가 아니다, 신이다!","나와라 오벨리스크의 거신병!"];
        ctx.save();ctx.font="900 11px system-ui";ctx.textAlign="center";ctx.textBaseline="middle";
        const widths=lines.map(s=>ctx.measureText(s).width),w=Math.min(330,Math.max(...widths,80)+20),h=lines.length*15+12;
        const x=clamp(f.x-w/2,arena.x+5,arena.x2-w-5),y=Math.max(arena.y+5,f.y-f.r-72-h);
        ctx.fillStyle="rgba(15,23,42,.94)";ctx.strokeStyle="#93c5fd";ctx.lineWidth=1.5;roundRect(ctx,x,y,w,h,10,true,true);
        ctx.fillStyle="#dbeafe";lines.forEach((s,i)=>ctx.fillText(s,x+w/2,y+11+i*15));
        ctx.restore();
      }
    }
    function initJabami(f) {'''
new='''      ctx.restore();drawHealthBar(f);drawName(f);
    }

    function drawJusticeObeliskOverlay() {
      const now=performance.now();
      const host=fighters.find(f=>f.duelist?.obeliskSpeechUntil>now);
      if(!host)return;
      const remain=clamp((host.duelist.obeliskSpeechUntil-now)/3400,0,1);
      const cx=arena.x+arena.size/2,cy=arena.y+arena.size/2;
      ctx.save();
      ctx.fillStyle=`rgba(2,6,23,${0.32+remain*.22})`;
      ctx.fillRect(arena.x,arena.y,arena.size,arena.size);
      ctx.textAlign="center";ctx.textBaseline="middle";
      ctx.font="900 38px Georgia, serif";
      ctx.lineWidth=3;
      ctx.strokeStyle="rgba(147,197,253,.34)";
      ctx.shadowColor="#60a5fa";ctx.shadowBlur=22;
      ctx.fillStyle="#1e3a8a";
      ctx.strokeText("몬스터가 아니다, 신이다!",cx,cy-27);
      ctx.fillText("몬스터가 아니다, 신이다!",cx,cy-27);
      ctx.font="900 34px Georgia, serif";
      ctx.strokeText("나와라 오벨리스크의 거신병!",cx,cy+26);
      ctx.fillText("나와라 오벨리스크의 거신병!",cx,cy+26);
      ctx.restore();
    }

    function initJabami(f) {'''
rep(old,new)

# 중앙 오버레이를 캐릭터/사망 이펙트 위, 돔 오버레이와 같은 레이어에 출력.
rep(
'''      drawDeathEffects();
      drawOshiDomeOverlay();''',
'''      drawDeathEffects();
      drawJusticeObeliskOverlay();
      drawOshiDomeOverlay();'''
)

# 패치노트
rep(
'''      const patchNotes = [
      "v95: v94 UI/연출 수정.''',
'''      const patchNotes = [
      "v96: 쟈바미/오벨리스크 시각 요소 재정리. 쟈바미의 남은 빚 기회 빨간 다이아몬드는 체력바 중앙이 아니라 체력바 왼쪽 끝에서부터 오른쪽으로 쌓이도록 정렬. 정의의 아군 오벨리스크 대사는 캐릭터 위 말풍선을 제거하고 '돔 공연 축하해.' 연출처럼 경기장 전체를 살짝 어둡게 한 뒤 중앙에 큰 글씨 2줄로 표시. 텍스트는 어두운 푸른색(#1e3a8a)과 옅은 푸른 글로우를 사용하며, 기존 3.4초 시간정지와 정확히 같은 시간 동안만 노출. v95의 소환수 피해/처치 본체 합산 및 v94의 쟈바미 공동승리 빚 처리 규칙은 유지.",
      "v95: v94 UI/연출 수정.'''
)

p.write_text(t,encoding="utf-8")
