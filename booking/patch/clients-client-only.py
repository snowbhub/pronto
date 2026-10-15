from pathlib import Path
root=Path("/app/src")
copy=Path("/tmp/booking-patch/client-directory.tsx")
dest=root/"components/clients/client-directory.tsx"
dest.write_text(copy.read_text(encoding="utf-8"),encoding="utf-8")
p=root/"app/(panel)/clientes/page.tsx"
s=p.read_text(encoding="utf-8")
old='import { ClientsView } from "@/components/clients/clients-view"'
if old not in s:raise RuntimeError("Client-directory import changed")
s=s.replace(old,'import { ClientDirectory } from "@/components/clients/client-directory"',1)
needle='<ClientsView rows={d.rows} now={d.now} services={d.services} staff={d.staff} />'
if needle not in s:raise RuntimeError("Client-directory render changed")
s=s.replace(needle,'<ClientDirectory rows={d.rows} now={d.now} services={d.services} staff={d.staff} />',1)
p.write_text(s,encoding="utf-8")
# Number and grammatical unit must be one locale-aware text node on mobile.
# Separate React text/span nodes produced "1 visits" and "1 відвідувань".
import re
profile=root/"components/clients/clients-view.tsx"
body=profile.read_text(encoding="utf-8")
pattern=r'\{r\.visits\}\s*<span className="text-ivory-3 lg:hidden">\\s*(?:visitas|visits)</span>'
replacement='<span className="num hidden lg:inline">{r.visits}</span><span className="num lg:hidden">{r.visits===1?"1 visit":String(r.visits)+" visits"}</span>'
body,count=re.subn(pattern,lambda _:replacement,body,count=1)
if count!=1:raise RuntimeError("Responsive client-visit count marker changed")
profile.write_text(body,encoding="utf-8")
print("BOOKING_CLIENT_DIRECTORY_PLURAL_COUNTS_OK")
print("BOOKING_CLIENT_DIRECTORY_CLIENT_ONLY_BOUNDARY_OK")
