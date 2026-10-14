import Link from "next/link"
import { PageBody,PageHeader } from "@/components/shell/page-header"
import { sqlClient } from "@/lib/data/store/postgres"
import { dayKey,addDays,TZ } from "@/lib/time"
import { formatARS } from "@/lib/money"
export const metadata={title:"Payroll"}
export default async function PayrollPage({searchParams}:PageProps<"/payroll">){
 const params=await searchParams
 const today=dayKey(new Date())
 const start=typeof params.from==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(params.from)?params.from:addDays(today,-7)
 const end=typeof params.to==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(params.to)?params.to:today
 const invalid=start>end || new Date(end).getTime()-new Date(start).getTime()>3*365*86400000
 const sql=sqlClient()
 const [staff,payments,expenses]=invalid?[[],[],[]]:await Promise.all([
  sql`select id,name,commission_pct,active from staff order by name`,
  sql`select staff_id,kind,amount,tip,units from payments
   where (paid_at at time zone ${TZ})::date between ${start}::date and ${end}::date`,
  sql`select staff_id,category,amount from expenses
   where (paid_at at time zone ${TZ})::date between ${start}::date and ${end}::date`
 ])
 const totals=staff.map(member=>{
  const relevant=payments.filter(p=>p.staff_id===member.id&&(p.kind==="servicio"||p.kind==="sena"))
  const revenue=relevant.reduce((a,p)=>a+Number(p.amount)-Number(p.tip),0)
  const tips=relevant.reduce((a,p)=>a+Number(p.tip),0)
  const commissions=Math.round(revenue*Number(member.commission_pct)/100)
  const advances=expenses.filter(e=>e.staff_id===member.id&&e.category==="vale").reduce((a,e)=>a+Number(e.amount),0)
  const paid=expenses.filter(e=>e.staff_id===member.id&&e.category==="sueldos").reduce((a,e)=>a+Number(e.amount),0)
  const count=relevant.filter(p=>p.kind==="servicio").reduce((a,p)=>a+Number(p.units||1),0)
  return {name:String(member.name),revenue,tips,commissions,advances,paid,count,commissionPct:Number(member.commission_pct),
   balance:Number(member.commission_pct)===0?0:commissions+tips-advances-paid}
 })
 const count=totals.reduce((a,r)=>a+r.count,0)
 const totalBalance=totals.reduce((a,r)=>a+r.balance,0)
 return <PageBody className="space-y-5">
  <PageHeader eyebrow="Finance" title="Staff payroll" description="Payroll by date range: commissions, tips, advances, paid amounts, and remaining balance."/>
  <form method="get" action="/payroll" className="panel grid grid-cols-2 gap-3 p-4">
   <label className="text-xs text-ivory-2">From<input name="from" type="date" defaultValue={start} className="mt-1 h-12 w-full min-w-0 rounded-xl border bg-surface-2 px-2 text-base"/></label>
   <label className="text-xs text-ivory-2">To<input name="to" type="date" defaultValue={end} className="mt-1 h-12 w-full min-w-0 rounded-xl border bg-surface-2 px-2 text-base"/></label>
   <button className="col-span-2 h-12 rounded-xl bg-ivory font-semibold text-obsidian">Apply date range</button>
   {invalid&&<p role="alert" className="col-span-2 text-sm text-danger">Choose a valid period of at most 3 years.</p>}
  </form>
  <div className="grid grid-cols-2 gap-3"><div className="panel p-4"><p className="text-xs text-ivory-3">Services</p><p className="mt-1 text-2xl font-bold">{count}</p></div><div className="panel p-4"><p className="text-xs text-ivory-3">Outstanding payroll</p><p className="mt-1 text-lg font-bold">{formatARS(totalBalance)}</p></div></div>
  <section className="space-y-3">{totals.map(line=><article key={line.name} className="panel p-4">
   <div className="flex items-center justify-between gap-3 border-b border-line pb-3"><div><h2 className="font-semibold">{line.name}</h2><p className="text-xs text-ivory-3">{line.commissionPct}% commission · {line.count} services</p></div><p className="text-right text-lg font-semibold">{formatARS(line.balance)}</p></div>
   <dl className="mt-4 grid grid-cols-2 gap-3 text-sm">
    {([["Service revenue",line.revenue],["Commission",line.commissions],["Tips",line.tips],["Advances",line.advances],["Paid",line.paid]] as [string,number][]).map(([name,amount])=><div key={name}><dt className="text-xs text-ivory-3">{name}</dt><dd className="font-semibold">{formatARS(amount)}</dd></div>)}
   </dl>
  </article>)}
  {!totals.length&&!invalid&&<p className="panel p-5 text-sm text-ivory-3">No staff added yet.</p>}
  </section>
  <p className="text-xs text-ivory-3">Current commission rates are applied to payments within the selected period. Historical rate changes are not tracked yet. Deposits are included when collected.</p>
  <Link className="inline-block text-sm underline underline-offset-4" href="/ajustes?tab=equipo">Change staff commission percentages</Link>
 </PageBody>
}
