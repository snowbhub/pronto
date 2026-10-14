from pathlib import Path
from collections import Counter
import json,re
root=Path("/app/src")
rows=[]
for p in sorted(Path("/tmp/booking-patch").glob("rows*.json")):rows+=json.loads(p.read_text(encoding="utf-8"))
dictionary={r[1] for r in rows}
candidates={}
for p in sorted(root.rglob("*.tsx")):
 if ".test." in p.name or "/api/" in str(p):continue
 body=p.read_text(encoding="utf-8")
 body=re.sub(r"/\*[\s\S]*?\*/","",body)
 visible=[]
 for m in re.finditer(r">([^<>{}\n]{2,250})<",body):
  visible.append(m.group(1).strip())
 for m in re.finditer(r'\b(?:aria-label|placeholder|title|description|label|eyebrow|hint|emptyLabel)=(["\'])(.*?)\1',body):
  visible.append(m.group(2).strip())
 visible=[v for v in visible if v and len(v)<200 and re.search("[a-zA-Z]",v) and not v.startswith(("http","/","{","@"))]
 unknown=[v for v in set(visible) if v not in dictionary and not any(k in v and len(k)>5 for k in dictionary)]
 if unknown:candidates[str(p.relative_to(root))]=unknown
print("BOOKING_VISIBLE_ENGLISH_AUDIT files",len(candidates),"unknown",sum(map(len,candidates.values())))
for path,values in list(candidates.items())[:45]:
 print("ENGLISH_UI_GAPS",path,":"," | ".join(sorted(values)[:12]))
