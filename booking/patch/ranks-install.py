from pathlib import Path
root=Path("/app")
bundle=Path("/tmp/booking-patch")
(root/"src/lib/ranks").mkdir(parents=True,exist_ok=True)
(root/"src/lib/ranks/actions.ts").write_text((bundle/"rank-actions.ts").read_text(encoding="utf-8"),encoding="utf-8")
(root/"src/app/(panel)/ranks").mkdir(parents=True,exist_ok=True)
(root/"src/app/(panel)/ranks/page.tsx").write_text((bundle/"rank-page.tsx").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/lib/domain/types.ts"
s=p.read_text(encoding="utf-8")
s=s.replace('export interface Staff {','export type ProfessionalLevel = "trainee" | "junior" | "barber" | "senior"\n\nexport interface Staff {\n  professionalLevel?: ProfessionalLevel')
p.write_text(s,encoding="utf-8")
p=root/"src/lib/data/store/postgres.ts"
s=p.read_text(encoding="utf-8")
needle='    const convs = conversations.map(toConversation)'
replacement='''    // Service eligibility is sourced from the rank matrix in PostgreSQL.
    // Service prices remain independent rows so a junior/senior cut can have its own price.
    const [rankRows, rankRules] = await Promise.all([
      sql`select staff_id,professional_level from booking_staff_levels`,
      sql`select service_id,professional_level,available from booking_service_levels`
    ])
    const staffRank = new Map(rankRows.map(r => [String(r.staff_id), String(r.professional_level)]))
    const serviceRanks = new Map<string,Set<string>>()
    for(const rule of rankRules){
      const serviceId=String(rule.service_id)
      if(!serviceRanks.has(serviceId))serviceRanks.set(serviceId,new Set())
      if(rule.available) serviceRanks.get(serviceId)!.add(String(rule.professional_level))
    }
    const convs = conversations.map(toConversation)'''
if needle not in s:raise ValueError("snapshot injection target missing")
s=s.replace(needle,replacement,1)
needle='''        ...toStaff(r),
        schedule: shifts.filter'''
replacement='''        ...toStaff(r),
        professionalLevel: (staffRank.get(String(r.id)) || "barber") as Staff["professionalLevel"],
        skipsServiceIds: [
          ...((r.skips as string[] | null) ?? []),
          ...services.filter(s => {
            const allowed=serviceRanks.get(String(s.id))
            return allowed && !allowed.has(staffRank.get(String(r.id)) || "barber")
          }).map(s => String(s.id))
        ],
        schedule: shifts.filter'''
if needle not in s:raise ValueError("Staff eligibility injection target missing")
s=s.replace(needle,replacement,1)
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('<div className="mt-5 max-w-3xl">','''<div className="mt-5 max-w-3xl">
        <Link href="/ranks" className="mb-4 flex min-h-12 items-center justify-between rounded-xl border border-line-strong bg-surface-1 px-4 text-sm font-semibold text-ivory">Barber ranks · Service permissions <span aria-hidden>→</span></Link>''')
p.write_text(s,encoding="utf-8")
p=root/"src/components/booking/booking-flow.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('services.filter(s=>s.active).map(s=>','services.filter(s=>s.active&&(staffId==="cualquiera"||!staff.find(m=>m.id===staffId)?.skipsServiceIds.includes(s.id))).map(s=>')
p.write_text(s,encoding="utf-8")
print("BOOKING_RANKS_FEATURE_WIRED")
