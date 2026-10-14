from pathlib import Path
import re

root=Path("/app/src")

# The finance paragraph was originally composed from several Spanish fragments.
# Rebuild that visible paragraph in canonical English, preserving all calculations.
p=root/"components/finance/week-view.tsx"
s=p.read_text(encoding="utf-8")
line_pattern=r"(?m)^(\s*)(?:A pagar|To pay|Amount due)\s*=\s*[^\n]*\b(?:la casa|business)\.?\s*$"
match=re.search(line_pattern,s)
if not match:
    raise RuntimeError("Finance explanatory paragraph changed; refusing an unsafe replacement")
indent=match.group(1)
clean="Amount due = commission + tips − advances − payments already made. Owners do not receive commissions; revenue from their services belongs to the business"
s=s[:match.start()]+indent+clean+s[match.end():]
# JSX conditional message stays in place; translate its own visible fragment.
s=s.replace(", y sus vales de esta semana (",", and their advances this week (")
s=s.replace(") son retiros</>",") are withdrawals</>")
p.write_text(s,encoding="utf-8")
print("BOOKING_FINANCE_PARAGRAPH_CANONICAL_ENGLISH")

# Keep user-entered client/staff names as original data; this patch does not
# translate dynamic service names, API/DB fields, or salary calculations.
