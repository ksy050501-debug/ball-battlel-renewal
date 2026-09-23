from pathlib import Path

p=Path('.github/scripts/v123_patch.py')
src=p.read_text(encoding='utf-8')
old='''old=''' + "'''      const conanSlow = conanKnifeSlowMultiplier(f);\\n      const boost = f.baseId === \"wind_rio\" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);'''" + '''
new=''' + "'''      const conanSlow = conanKnifeSlowMultiplier(f);\\n      const spiderSlow = spiderWebSlowMultiplier(f);\\n      const boost = f.baseId === \"wind_rio\" ? rioMoveBoost(f) : (f.speedBoost > 0 ? 1.45 : 1);'''" + '''
if text.count(old)<2: raise SystemExit('missing movement slow anchors')
text=text.replace(old,new,2)
if text.count('* elsaIce * conanSlow;')<2: raise SystemExit('missing speed product anchors')
text=text.replace('* elsaIce * conanSlow;','* elsaIce * conanSlow * spiderSlow;',2)
rep('*conanKnifeSlowMultiplier(f);','*conanKnifeSlowMultiplier(f)*spiderWebSlowMultiplier(f);',1,'Hinta slow')'''
new='''slow_anchor='      const conanSlow = conanKnifeSlowMultiplier(f);'
if text.count(slow_anchor)<1: raise SystemExit('missing movement slow anchor')
text=text.replace(slow_anchor,'      const conanSlow = conanKnifeSlowMultiplier(f) * spiderWebSlowMultiplier(f);')
rep('*conanKnifeSlowMultiplier(f);','*conanKnifeSlowMultiplier(f)*spiderWebSlowMultiplier(f);',1,'Hinta slow')'''
if old not in src:
    raise SystemExit('patch source anchor missing')
src=src.replace(old,new,1)
exec(compile(src,str(p),'exec'))
