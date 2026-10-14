from pathlib import Path
import re
root=Path("/app/src")
# English is the canonical SSR source. Keep punctuation between separate date
# tokens so the DOM localization bridge can produce correct dates in DE and UK.
p=root/"lib/time.ts"
s=p.read_text(encoding="utf-8")
old='return longFmt.format(at(day, "12:00"))'
if old not in s:raise RuntimeError("Long-date formatter anchor changed")
s=s.replace(old,'return longFmt.format(at(day, "12:00")).replace(/^(\\S+)\\s+(\\d{1,2})/, "$1, $2")',1)
p.write_text(s,encoding="utf-8")
# Do not transform each word to title case: Ukrainian month names after a day
# are lowercase (14 жовтня), unlike month headings.
p=root/"app/(panel)/agenda/page.tsx"
s=p.read_text(encoding="utf-8")
anchor='font-semibold capitalize text-ivory'
if anchor not in s:raise RuntimeError("Calendar date title typography changed")
s=s.replace(anchor,'font-semibold text-ivory',1)
p.write_text(s,encoding="utf-8")
# Transaction count and word must be a single React text node for plural rules.
p=root/"components/caja/caja-view.tsx"
s=p.read_text(encoding="utf-8")
s,n=re.subn(r'\{l\.services\}\s+(?:servicios|services)\s+·\s+\{formatARS\(l\.revenue\)\}',
  '{`\u0024{l.services} services`} · {formatARS(l.revenue)}',s,count=1)
if n!=1:raise RuntimeError("Cash employee service count anchor changed")
p.write_text(s,encoding="utf-8")
# Avoid CSS uppercasing the second word of a Ukrainian two-word range.
p=root/"app/(panel)/analytics/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('text-xs font-semibold capitalize ','text-xs font-semibold ',1)
p.write_text(s,encoding="utf-8")
print("BOOKING_DATES_CASH_SINGULAR_AND_ANALYTICS_CASE_FIXED")
