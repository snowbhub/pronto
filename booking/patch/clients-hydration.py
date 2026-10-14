from pathlib import Path
p=Path("/app/src/components/clients/clients-view.tsx")
s=p.read_text(encoding="utf-8")
old='import { useMemo, useState } from "react"'
new='import { useEffect, useMemo, useState } from "react"'
if old not in s:raise RuntimeError("ClientsView React import changed")
s=s.replace(old,new,1)
anchor='''  const router = useRouter()
  const params = useSearchParams()'''
if anchor not in s:raise RuntimeError("ClientsView hook anchor changed")
s=s.replace(anchor,'''  const router = useRouter()
  useEffect(()=>{
    document.documentElement.dataset.bookingClientsHydrated="true"
    window.dispatchEvent(new Event("booking:content-hydrated"))
    return ()=>{delete document.documentElement.dataset.bookingClientsHydrated}
  },[])
  const params = useSearchParams()''',1)
p.write_text(s,encoding="utf-8")
print("BOOKING_CLIENTS_HYDRATION_HANDSHAKE_OK")
