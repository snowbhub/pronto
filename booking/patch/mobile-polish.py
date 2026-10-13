from pathlib import Path
root=Path("/app")
bundle=Path("/tmp/booking-patch")
(root/"src/i18n/controls.tsx").write_text((bundle/"language-menu.tsx").read_text(encoding="utf-8"),encoding="utf-8")

p=root/"src/app/reservar/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('max-w-2xl items-center gap-3 px-4 py-4 sm:px-6','max-w-2xl items-center gap-3 py-4 pl-4 pr-32 sm:pl-6 sm:pr-36')
p.write_text(s,encoding="utf-8")

p=root/"src/components/booking/booking-flow.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('className="mt-10 rounded-[28px] bg-surface-2 px-5 pb-8 pt-8 sm:px-8"','className="relative mt-20 rounded-[28px] bg-surface-2 px-5 pb-8 pt-14 shadow-sm sm:px-8"')
s=s.replace('className="mb-5 grid size-16 place-items-center rounded-full bg-surface-3"','className="absolute -top-9 left-5 mb-5 grid size-[76px] place-items-center rounded-full border-4 border-obsidian bg-surface-3 sm:left-8"')
s=s.replace('className="text-3xl font-bold tracking-tight">{BRAND.fullName}', 'className="mt-2 text-3xl font-bold tracking-tight">{BRAND.fullName}')
p.write_text(s,encoding="utf-8")

p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8").replace('import { dayKey } from "@/lib/time"','import { dayKey, TZ } from "@/lib/time"')
s=s.replace('value="America/Argentina/Buenos_Aires (currently fixed in source; editing requires migration)"','value={TZ}')
p.write_text(s,encoding="utf-8")

p=root/"src/components/finance/week-view.tsx"
s=p.read_text(encoding="utf-8")
target='<div className="overflow-x-auto">'
cards='''<div className="space-y-3 px-4 pb-4 md:hidden">
            {d.staffLines.map(l=><div key={l.staff.id} className="rounded-xl border border-line bg-surface-2 p-4">
              <div className="mb-3 flex items-center justify-between gap-3"><span className="font-semibold text-ivory">{l.staff.name}</span><span className="font-semibold text-ivory">{formatARS(l.balance)}</span></div>
              <dl className="grid grid-cols-2 gap-x-3 gap-y-3 text-xs">
                <div><dt className="text-ivory-3">Services</dt><dd className="mt-0.5 text-ivory">{l.services}</dd></div>
                <div><dt className="text-ivory-3">Revenue</dt><dd className="mt-0.5 text-ivory">{formatARS(l.revenue)}</dd></div>
                <div><dt className="text-ivory-3">Commission</dt><dd className="mt-0.5 text-ivory">{formatARS(l.commission)}</dd></div>
                <div><dt className="text-ivory-3">Tips</dt><dd className="mt-0.5 text-ivory">{formatARS(l.tips)}</dd></div>
                <div><dt className="text-ivory-3">Advances</dt><dd className="mt-0.5 text-ivory">{formatARS(l.advances)}</dd></div>
                <div><dt className="text-ivory-3">Already paid</dt><dd className="mt-0.5 text-ivory">{formatARS(l.paid)}</dd></div>
              </dl>
            </div>)}
          </div>
          <div className="hidden overflow-x-auto md:block">'''
s=s.replace(target,cards,1)
p.write_text(s,encoding="utf-8")
print("BOOKING_MOBILE_POLISH_APPLIED")
