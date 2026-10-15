from pathlib import Path
import re
p=Path("/app/src/components/caja/caja-view.tsx")
s=p.read_text(encoding="utf-8")
pattern=r'<span className="num">\{money\.count\}</span>\s+(?:cobros|payments)\s+·\s+(?:servicios|services)\s+<span className="num">\{formatARS\(money\.services\)\}</span>'
replacement='<span className="num">{money.count===1?"1 payment":\u0060\u0024{money.count} payments\u0060}</span> · Service revenue <span className="num">{formatARS(money.services)}</span>'
s,n=re.subn(pattern,lambda _:replacement,s,count=1)
if n!=1:raise RuntimeError("Cash receipt summary changed: expected exactly one source template")
p.write_text(s,encoding="utf-8")
print("BOOKING_CASH_SUMMARY_SINGLE_REACT_TEXT_NODE_OK")
