from pathlib import Path
p=Path("/app/src/components/agenda/day-grid.tsx")
s=p.read_text(encoding="utf-8")
s=s.replace('''  const [chargingId, setChargingId] = useState<string | null>(null)''','''  const [chargingId, setChargingId] = useState<string | null>(null)
  const [mobileMode,setMobileMode] = useState(false)
  const [selectedStaffId,setSelectedStaffId] = useState(staff[0]?.id ?? "")
  useEffect(()=>{
    const media=window.matchMedia("(max-width:767px)")
    const sync=()=>setMobileMode(media.matches)
    sync()
    media.addEventListener("change",sync)
    return ()=>media.removeEventListener("change",sync)
  },[])
  useEffect(()=>{
    if(staff.length && !staff.some(s=>s.id===selectedStaffId))setSelectedStaffId(staff[0].id)
  },[staff,selectedStaffId])
  const visibleStaff=mobileMode?staff.filter(s=>s.id===selectedStaffId):staff
''')
s=s.replace('''      <div className="panel overflow-hidden">
        <div className="overflow-x-auto scroll-thin">
          <div className="min-w-[620px]">''','''      <div className="panel min-w-0 overflow-hidden">
        {staff.length===0 && <div className="p-5 text-center text-sm text-ivory-2">No barbers added. Add staff under Settings → Team before creating appointments.</div>}
        {mobileMode && staff.length>0 && <div className="grid grid-cols-2 gap-2 border-b border-line p-3">
          {staff.map(member=><button key={member.id} type="button" onClick={()=>setSelectedStaffId(member.id)}
            aria-pressed={selectedStaffId===member.id}
            className={cn("min-w-0 rounded-xl border px-3 py-3 text-left text-sm font-medium transition-colors",
              selectedStaffId===member.id?"border-ivory-2 bg-surface-3 text-ivory":"border-line bg-surface-1 text-ivory-2")}>
            <span className="block truncate">{member.name}</span>
            <span className="mt-1 block text-xs font-normal text-ivory-3">{appointments.filter(a=>a.staffId===member.id&&a.status!=="cancelado").length} bookings</span>
          </button>)}
        </div>}
        {mobileMode && staff.length>0 && <p className="border-b border-line px-4 py-2 text-xs text-ivory-3">Tap an empty time to add a booking, or tap an appointment to open its details.</p>}
        <div className={mobileMode?"overflow-x-hidden":"overflow-x-auto scroll-thin"}>
          <div className={mobileMode?"w-full min-w-0":"min-w-[620px]"}>''')
s=s.replace('''gridTemplateColumns: `56px repeat(${staff.length}, minmax(0,1fr))`''','''gridTemplateColumns: `56px repeat(${visibleStaff.length}, minmax(0,1fr))`''')
# The original maps appear exactly in header and grid; retain other staff references for actions/transfer.
s=s.replace('''{staff.map((s) => {''','''{visibleStaff.map((s) => {''',1)
s=s.replace('''{staff.map((s) => (''','''{visibleStaff.map((s) => (''',1)
p.write_text(s,encoding="utf-8")
print("BOOKING_CALENDAR_SINGLE_COLUMN_MOBILE",s.count("visibleStaff.map"),s.count("visibleStaff.length"))
