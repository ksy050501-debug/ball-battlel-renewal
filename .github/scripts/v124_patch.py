from pathlib import Path
import re
import subprocess
import tempfile

p = Path('index.html')
t = p.read_text(encoding='utf-8')

def rep(old, new, label):
    global t
    if old not in t:
        raise SystemExit('missing ' + label)
    t = t.replace(old, new, 1)

rep('<title>볼배틀 리뉴얼 v123</title>', '<title>볼배틀 리뉴얼 v124</title>', 'title')
rep('<h1 id="mainTitle">볼배틀 리뉴얼 v123</h1>', '<h1 id="mainTitle">볼배틀 리뉴얼 v124</h1>', 'main title')

rep('''    function spiderWallPoint(x,y){
      return {x:clamp(x,arena.x,arena.x2),y:clamp(y,arena.y,arena.y2)};
    }''', '''    function spiderWallPoint(x,y){
      const m=72;
      const dl=Math.abs(x-arena.x),dr=Math.abs(x-arena.x2),dt=Math.abs(y-arena.y),db=Math.abs(y-arena.y2);
      const min=Math.min(dl,dr,dt,db);
      if(min===dl)return {x:arena.x,y:clamp(y,arena.y+m,arena.y2-m)};
      if(min===dr)return {x:arena.x2,y:clamp(y,arena.y+m,arena.y2-m)};
      if(min===dt)return {x:clamp(x,arena.x+m,arena.x2-m),y:arena.y};
      return {x:clamp(x,arena.x+m,arena.x2-m),y:arena.y2};
    }''', 'wall anchor')

rep('''    function spiderBeginArc(f,ax,ay){
      const s=f.spider,dx=f.x-ax,dy=f.y-ay;
      const radius=clamp(Math.hypot(dx,dy)||SPIDER.swingMinRadius,SPIDER.swingMinRadius,SPIDER.swingMaxRadius);
      s.mode="arc";s.swingWeb=null;s.chase=null;
      s.arc={ax,ay,radius,start:Math.atan2(dy,dx),dir:Math.random()<.5?-1:1,t:0};
      f.vx=0;f.vy=0;
      if(!fastSimMode)spawnBlast(ax,ay,26,"#e2e8f0");
    }''', '''    function spiderBeginArc(f,ax,ay){
      const s=f.spider,dx=f.x-ax,dy=f.y-ay;
      const radius=Math.max(1,Math.hypot(dx,dy));
      const start=Math.atan2(dy,dx);
      const angle=clamp(155/radius,.34,1.42);
      const cx=(arena.x+arena.x2)/2,cy=(arena.y+arena.y2)/2;
      const score=dir=>{
        const a=start+dir*angle;
        const ex=ax+Math.cos(a)*radius,ey=ay+Math.sin(a)*radius;
        const ox=Math.max(0,arena.x+f.r-ex,ex-(arena.x2-f.r));
        const oy=Math.max(0,arena.y+f.r-ey,ey-(arena.y2-f.r));
        return ox*ox+oy*oy+Math.hypot(ex-cx,ey-cy)*.08;
      };
      const dir=score(1)<=score(-1)?1:-1;
      s.mode="arc";s.swingWeb=null;s.chase=null;
      s.arc={ax,ay,radius,start,dir,angle,t:0};
      f.vx=0;f.vy=0;
      if(!fastSimMode)spawnBlast(ax,ay,26,"#e2e8f0");
    }''', 'arc setup')

rep('''        const a=s.arc;a.t+=dt;const p=clamp(a.t/SPIDER.swingArcTime,0,1),ang=a.start+a.dir*SPIDER.swingArcAngle*p;
        f.x=clamp(a.ax+Math.cos(ang)*a.radius,arena.x+f.r,arena.x2-f.r);''', '''        const a=s.arc;a.t+=dt;const p=clamp(a.t/SPIDER.swingArcTime,0,1),swingAngle=a.angle||SPIDER.swingArcAngle,ang=a.start+a.dir*swingAngle*p;
        f.x=clamp(a.ax+Math.cos(ang)*a.radius,arena.x+f.r,arena.x2-f.r);''', 'arc motion')

note = '      "v124: 거미남 웹스윙 이동 보정. 먼 벽에 거미줄이 걸렸을 때 스윙 반경을 강제로 135로 줄이며 순간이동하던 문제를 수정해 현재 위치-벽 앵커의 실제 거리를 반경으로 사용합니다. 먼 앵커일수록 회전각을 자동으로 줄여 이동거리를 안정화하고, 두 회전 방향 중 경기장 안쪽으로 향하는 방향을 선택합니다. 벽 앵커는 구석에서 72px 떨어진 안전 구간으로 보정해 구석에 거미줄을 걸고 비정상적으로 끼는 움직임도 완화했습니다.",\n'
anchor = '      "v123: 고난 체력을165→160으로 조정.'
if anchor not in t:
    raise SystemExit('missing patch note anchor')
t = t.replace(anchor, note + anchor, 1)

p.write_text(t, encoding='utf-8')

scripts = re.findall(r'<script[^>]*>([\s\S]*?)</script>', t)
with tempfile.NamedTemporaryFile('w', suffix='.js', delete=False, encoding='utf-8') as tmp:
    tmp.write('\n'.join(scripts))
    tmp_path = tmp.name
subprocess.run(['node', '--check', tmp_path], check=True)
print('v124 patch + JS validation OK')
