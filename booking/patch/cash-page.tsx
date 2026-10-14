import { PageBody,PageHeader } from "@/components/shell/page-header"
import { sqlClient } from "@/lib/data/store/postgres"
import { addExpenseType,recordExpense,recordCashMovement } from "@/lib/cash-management/actions"
import { dayKey,TZ } from "@/lib/time"
import { formatARS } from "@/lib/money"
export const metadata={title:"Cash operations"}
export default async function CashManagementPage(){
 const sql=sqlClient()
 const today=dayKey(new Date())
 const [types,expenses,movements,open,received,spent]=await Promise.all([
  sql`select id,name from booking_expense_types where active=true order by name`,
  sql`select e.description,e.amount,e.method,e.paid_at,d.payee,t.name as type_name
   from expenses e join booking_expense_details d on d.expense_id=e.id
   left join booking_expense_types t on t.id=d.expense_type_id order by e.paid_at desc limit 20`,
  sql`select direction,amount,recipient,note,created_at
   from booking_cash_movements order by created_at desc limit 30`,
  sql`select opening_cash from shop_settings where id=1`,
  sql`select coalesce(sum(amount),0)::bigint as value from payments where method='efectivo'
   and (paid_at at time zone ${TZ})::date=${today}::date`,
  sql`select coalesce(sum(amount),0)::bigint as value from expenses where method='efectivo'
   and (paid_at at time zone ${TZ})::date=${today}::date`
 ])
 const transfers=await sql`select coalesce(sum(case when direction='deposit' then amount else -amount end),0)::bigint as net
   from booking_cash_movements where (created_at at time zone ${TZ})::date=${today}::date`
 const openCash=Number(open[0]?.opening_cash||0)
 const expectedCash=openCash+Number(received[0]?.value||0)-Number(spent[0]?.value||0)+Number(transfers[0]?.net||0)
 return <PageBody className="space-y-5">
  <PageHeader eyebrow="Cash" title="Cash & expenses" description="Record expenses by category and payee, cash deposits, and withdrawals without treating transfers as sales."/>
  <div className="grid grid-cols-2 gap-3">
   <div className="panel p-4"><p className="text-xs text-ivory-3">Expected cash today</p><p className="mt-2 break-words text-xl font-bold">{formatARS(expectedCash)}</p></div>
   <div className="panel p-4"><p className="text-xs text-ivory-3">Today's cash transfers</p><p className="mt-2 break-words text-xl font-bold">{formatARS(Number(transfers[0]?.net||0))}</p></div>
  </div>
  <p className="text-xs text-ivory-3">Estimate = configured opening cash + cash sales − cash expenses + cash deposits − withdrawals. Verify the physical drawer amount during cash closing.</p>
  <section className="panel space-y-3 p-4"><h2 className="font-semibold">Expense categories</h2>
   <form action={addExpenseType} className="flex gap-2"><input type="text" name="name" required minLength={2} placeholder="e.g. Cleaning supplies" className="h-12 min-w-0 flex-1 rounded-xl border bg-surface-2 px-3 text-base"/><button className="shrink-0 rounded-xl bg-ivory px-4 text-sm font-semibold text-obsidian">Add</button></form>
   <div className="flex flex-wrap gap-2">{types.map(t=><span key={String(t.id)} className="rounded-full bg-surface-2 px-3 py-1.5 text-xs">{String(t.name)}</span>)}</div>
  </section>
  <section className="panel space-y-3 p-4"><h2 className="font-semibold">Record an expense</h2>
   <form action={recordExpense} className="grid grid-cols-2 gap-3">
    <label className="col-span-2 text-xs text-ivory-2">Category<select name="typeId" required className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base">{types.map(t=><option key={String(t.id)} value={String(t.id)}>{String(t.name)}</option>)}</select></label>
    <label className="col-span-2 text-xs text-ivory-2">What was purchased?<input name="description" required minLength={3} className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
    <label className="col-span-2 text-xs text-ivory-2">Paid to<input name="payee" placeholder="Supplier / recipient" className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
    <label className="text-xs text-ivory-2">Amount<input name="amount" type="number" min={1} required className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
    <label className="text-xs text-ivory-2">Payment<select name="method" className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"><option value="efectivo">Cash</option><option value="transferencia">Transfer</option><option value="debito">Debit card</option><option value="credito">Credit card</option></select></label>
    <button disabled={!types.length} className="col-span-2 h-12 rounded-xl bg-ivory font-semibold text-obsidian disabled:opacity-40">Save expense</button>
   </form>
  </section>
  <section className="panel space-y-3 p-4"><h2 className="font-semibold">Cash collection / withdrawal</h2>
   <form action={recordCashMovement} className="grid grid-cols-2 gap-3">
    <label className="col-span-2 text-xs text-ivory-2">Operation<select name="direction" className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"><option value="withdrawal">Cash withdrawal / collection</option><option value="deposit">Cash deposit to drawer</option></select></label>
    <label className="col-span-2 text-xs text-ivory-2">Amount<input name="amount" type="number" min={1} required className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
    <label className="col-span-2 text-xs text-ivory-2">Responsible / recipient<input name="recipient" placeholder="Owner, bank, employee" className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
    <label className="col-span-2 text-xs text-ivory-2">Note<input name="note" className="mt-1 h-12 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
    <button className="col-span-2 h-12 rounded-xl bg-ivory font-semibold text-obsidian">Record cash movement</button>
   </form>
  </section>
  <section className="panel p-4"><h2 className="mb-3 font-semibold">Recent expenses</h2><div className="divide-y divide-line">{expenses.map((e,i)=><div key={i} className="flex items-start justify-between gap-2 py-3"><div className="min-w-0"><p className="text-sm font-medium">{String(e.description)}</p><p className="text-xs text-ivory-3">{String(e.type_name||"Other")}{e.payee?" · "+String(e.payee):""}</p></div><span className="shrink-0 text-sm font-semibold">{formatARS(Number(e.amount))}</span></div>)}{!expenses.length&&<p className="text-sm text-ivory-3">No expenses yet.</p>}</div></section>
  <section className="panel p-4"><h2 className="mb-3 font-semibold">Cash movement history</h2><div className="divide-y divide-line">{movements.map((m,i)=><div key={i} className="flex items-start justify-between gap-2 py-3"><div><p className="text-sm font-medium">{m.direction==="deposit"?"Cash deposit":"Cash withdrawal"}</p><p className="text-xs text-ivory-3">{String(m.recipient||"")}{m.note?" · "+String(m.note):""}</p></div><p className="shrink-0 text-sm font-semibold">{m.direction==="deposit"?"+":"−"}{formatARS(Number(m.amount))}</p></div>)}{!movements.length&&<p className="text-sm text-ivory-3">No cash movements yet.</p>}</div></section>
 </PageBody>
}
