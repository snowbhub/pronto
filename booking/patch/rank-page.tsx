import Link from "next/link"
import { sqlClient } from "@/lib/data/store/postgres"
import { PageBody, PageHeader } from "@/components/shell/page-header"
import { setStaffLevel, setServiceRank } from "@/lib/ranks/actions"
export const metadata={title:"Staff levels"}
const levels=[
 {id:"trainee",title:"Trainee / Стажер"},
 {id:"junior",title:"Junior / Молодший барбер"},
 {id:"barber",title:"Barber / Барбер"},
 {id:"senior",title:"Senior / Старший барбер"},
] as const
export default async function RanksPage(){
 const sql=sqlClient()
 const [staff,services,ranks,rules]=await Promise.all([
   sql`select id,name,role,commission_pct from staff where active=true order by name`,
   sql`select id,name,price from services where active=true order by sort,name`,
   sql`select staff_id,professional_level from booking_staff_levels`,
   sql`select service_id,professional_level,available from booking_service_levels`,
 ])
 const staffLevel=new Map(ranks.map(r=>[String(r.staff_id),String(r.professional_level)]))
 const rulesMap=new Map(rules.map(r=>[String(r.service_id)+":"+String(r.professional_level),Boolean(r.available)]))
 return <PageBody className="space-y-5">
   <PageHeader eyebrow="Team" title="Barber levels" description="Set professional ranks and specify which services each level can provide." />
   <section className="panel space-y-4 p-4">
    <h2 className="font-semibold">Staff members</h2>
    {!staff.length&&<p className="text-sm text-ivory-3">Add staff members in Team settings first.</p>}
    {staff.map(member=><form action={setStaffLevel} key={String(member.id)} className="flex flex-col gap-3 border-b border-line pb-4 last:border-0 last:pb-0">
     <input type="hidden" name="staffId" value={String(member.id)}/>
     <div className="flex items-center justify-between gap-3">
       <div><p className="font-medium">{String(member.name)}</p><p className="text-xs text-ivory-3">Commission: {Number(member.commission_pct)}%</p></div>
       <Link href="/ajustes?tab=equipo" className="text-xs underline underline-offset-4 text-ivory-2">Edit commission</Link>
     </div>
     <div className="flex gap-2"><select name="level" defaultValue={staffLevel.get(String(member.id))||"barber"} className="min-w-0 h-11 flex-1 rounded-xl border bg-surface-2 px-3 text-sm">{levels.map(l=><option key={l.id} value={l.id}>{l.title}</option>)}</select><button className="shrink-0 rounded-xl bg-ivory px-4 text-sm font-semibold text-obsidian">Save</button></div>
    </form>)}
   </section>
   <section className="panel space-y-4 p-4">
     <h2 className="font-semibold">Service permissions by rank</h2>
     <p className="text-sm text-ivory-3">Services without any rank restrictions are available to all levels. When you add a rule for one service, only levels explicitly allowed can book it. Different prices or durations must be configured as separate services, e.g. “Trainee haircut” and “Senior haircut”.</p>
     {services.map(service=><div key={String(service.id)} className="space-y-3 border-b border-line pb-4 last:border-0 last:pb-0">
      <div className="flex items-center justify-between gap-2"><p className="font-medium">{String(service.name)}</p><p className="text-sm text-ivory-3">{Number(service.price).toLocaleString("en")}</p></div>
      <div className="grid grid-cols-2 gap-2">
        {levels.map(level=>{
          const current=rulesMap.get(String(service.id)+":"+level.id)
          return <form action={setServiceRank} key={level.id} className="rounded-xl bg-surface-2 p-2">
           <input type="hidden" name="serviceId" value={String(service.id)}/><input type="hidden" name="level" value={level.id}/>
           <label className="block text-xs text-ivory-2">{level.title}
            <select name="available" defaultValue={current===undefined?"unset":current?"yes":"no"} className="mt-1 w-full rounded-lg border bg-surface-1 px-2 py-2 text-xs">
             <option value="unset" disabled>Not specified</option><option value="yes">Allowed</option><option value="no">Not allowed</option>
            </select>
           </label><button className="mt-2 h-8 w-full rounded-lg border border-line-strong text-xs">Apply</button>
          </form>
        })}
      </div>
     </div>)}
    {!services.length&&<Link className="text-sm underline" href="/ajustes?tab=servicios">Add services first</Link>}
   </section>
 </PageBody>
}
