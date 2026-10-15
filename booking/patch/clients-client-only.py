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
print("BOOKING_CLIENT_DIRECTORY_CLIENT_ONLY_BOUNDARY_OK")
