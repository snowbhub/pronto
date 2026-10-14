import Link from "next/link"
import { PageBody,PageHeader } from "@/components/shell/page-header"
import { sqlClient } from "@/lib/data/store/postgres"
import { dayKey,addDays,TZ } from "@/lib/time"
import { formatARS } from "@/lib/money"
export const metadata={title:"Analytics"}
type Period="day"|"week"|"month"|"year"|"custom"
export default async function AnalyticsPage({searchParams}:PageProps<"/analytics">){
 const q=await searchParams
 const raw=typeof q.period==="string"?q.period:"month"
 const period:Period=(["day","week","month","year","custom"] as string[]).includes(raw)?raw as Period:"month"
 const today=dayKey(new Date())
 const start=period==="day"?today:period==="week"?addDays(today,-6):period==="month"?today.slice(0,7)+"-01":period==="year"?today.slice(0,4)+"-01-01":typeof q.from==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(q.from)?q.from:addDays(today,-29)
 const end=period==="custom"&&typeof q.to==="string"&&/^\d{4}-\d{2}-\d{2}$/.test(q.to)?q.to:today
 const valid=start<=end&&new Date(end).getTime()-new Date(start).getTime()<=3*365*86400000
 const sql=sqlClient()
 const [paymentRows,expenseRows]=!valid?[[],[]]:await Promise.all([
  sql`select to_char((paid_at at time zone ${TZ})::date,'YYYY-MM-DD') as day,
   sum(amount)::bigint as amount, count(*)::int as count,
   sum(case when method='efectivo' then amount else 0 end)::bigint as cash
   from payments where (paid_at at time zone ${TZ})::date between ${start}::date and ${end}::date
   group by 1 order by 1`,
  sql`select to_char((paid_at at time zone ${TZ})::date,'YYYY-MM-DD') as day,
   sum(amount)::bigint as amount,sum(case when method='efectivo' then amount else 0 end)::bigint as cash
   from expenses where (paid_at at time zone ${TZ})::date between ${start}::date and ${end}::date
   group by 1 order by 1`
 ])
 const pAmount=paymentRows.reduce((a,r)=>a+Number(r.amount),0)
 const eAmount=expenseRows.reduce((a,r)=>a+Number(r.amount),0)
 const cashNet=paymentRows.reduce((a,r)=>a+Number(r.cash),0)-expenseRows.reduce((a,r)=>a+Number(r.cash),0)
 const count=paymentRows.reduce((a,r)=>a+Number(r.count),0)
 const days=Math.max(1,Math.ceil((new Date(end).getTime()-new Date(start).getTime())/86400000)+1)
 const mode=days>45?"month":days>12?"week":"day"
 const bucket=(d:string)=>mode==="month"?d.slice(0,7):mode==="week"?addDays(d,-((new Date(d+"T12:00:00Z").getUTCDay()+6)%7)):d
 const groups=new Map<string,{revenue:number;expenses:number}>()
 for(const r of paymentRows){const key=bucket(String(r.day));const cur=groups.get(key)||{revenue:0,expenses:0};cur.revenue+=Number(r.amount);groups.set(key,cur)}
 for(const r of expenseRows){const key=bucket(String(r.day));const cur=groups.get(key)||{revenue:0,expenses:0};cur.expenses+=Number(r.amount);groups.set(key,cur)}
 const series=[...groups.entries()].sort(([a],[b])=>a.localeCompare(b)).map(([period,v])=>({period,...v}))
 const max=Math.max(1,...series.map(r=>Math.max(r.revenue,r.expenses)))
 return <PageBody className="space-y-5">
  <PageHeader eyebrow="Overview" title="Business analytics" description="Revenue, expenses and cash movements by date."/>
  <nav aria-label="Reporting period" className="grid grid-cols-5 gap-1 rounded-xl bg-surface-2 p-1">{(["day","week","month","year","custom"] as const).map(k=><Link key={k} href={"/analytics?period="+k} className={"rounded-lg px-1 py-3 text-center text-xs font-semibold capitalize "+(period===k?"bg-surface-3 text-ivory":"text-ivory-3")}>{k}</Link>)}</nav>
  {period==="custom"&&<form action="/analytics" method="get" className="panel grid grid-cols-2 gap-3 p-4"><input type="hidden" name="period" value="custom"/><label className="text-xs">From<input type="date" name="from" defaultValue={start} className="mt-1 h-11 w-full rounded-lg bg-surface-2 px-2 text-base"/></label><label className="text-xs">To<input type="date" name="to" defaultValue={end} className="mt-1 h-11 w-full rounded-lg bg-surface-2 px-2 text-base"/></label><button className="col-span-2 rounded-lg bg-ivory py-3 font-semibold text-obsidian">Apply dates</button></form>}
  {!valid&&<p className="text-sm text-danger">Choose a valid period of at most 3 years.</p>}
  <div className="grid grid-cols-2 gap-3">
   {([["Revenue",pAmount],["Expenses",eAmount],["Net movement",pAmount-eAmount],["Cash movement",cashNet]] as [string,number][]).map(([label,value])=><div key={label} className="panel p-4"><p className="text-xs text-ivory-3">{label}</p><p className="mt-2 break-words text-xl font-semibold">{formatARS(value)}</p></div>)}
  </div>
  <section className="panel p-4">
   <div className="mb-3 flex flex-wrap items-center justify-between gap-2"><h2 className="font-semibold">Revenue / expense trend</h2><span className="text-xs text-ivory-3">{start} — {end}</span></div>
   <div className="mb-3 flex items-center gap-4 text-xs text-ivory-3"><span>■ Revenue</span><span className="opacity-60">▨ Expenses</span></div>
   <div className="grid grid-cols-4 gap-2 sm:grid-cols-7">
    {series.map(d=><div key={d.period} className="min-w-0">
     <div className="flex h-28 items-end justify-center gap-0.5 rounded-lg bg-surface-2 px-1 pb-1">
      <div title={"Revenue "+formatARS(d.revenue)} style={{height:Math.max(2,Math.round(d.revenue/max*96))+"%"}} className="w-3 min-w-0 rounded-t bg-ivory"/>
      <div title={"Expenses "+formatARS(d.expenses)} style={{height:Math.max(2,Math.round(d.expenses/max*96))+"%"}} className="w-3 min-w-0 rounded-t bg-ivory-3 opacity-60"/>
     </div>
     <p className="mt-1 truncate text-center text-[10px] text-ivory-3">{d.period.slice(5)}</p>
    </div>)}
   </div>
   {!series.length&&<p className="py-8 text-center text-sm text-ivory-3">No transactions within this period.</p>}
  </section>
  <section className="panel flex items-center justify-between p-4"><div><p className="font-semibold">Transactions</p><p className="text-xs text-ivory-3">Payments in selected period</p></div><strong className="text-2xl">{count}</strong></section>
  <p className="text-xs text-ivory-3">Cash movement shows net cash receipts and cash expenses for this period. It is not a verified cash-drawer balance; use the cash closing report for that.</p>
 </PageBody>
}
