import { PageBody,PageHeader } from "@/components/shell/page-header"
import { sqlClient } from "@/lib/data/store/postgres"
import { saveStaffAccount,setStaffAccountActive } from "@/lib/auth/staff-actions"
export const metadata={title:"Staff accounts"}
export default async function StaffAccountsPage(){
 const sql=sqlClient()
 const accounts=await sql`select s.id,s.name,s.active as staff_active,a.username,a.active as account_active,a.created_at
  from staff s left join booking_staff_accounts a on a.staff_id=s.id order by s.name`
 return <PageBody className="space-y-5">
  <PageHeader eyebrow="Security" title="Staff accounts" description="Create individual passwords for barbers. Staff users only access their own schedule and the booking form; finances and settings remain admin-only." />
  <div className="space-y-3">
   {accounts.map(a=><section key={String(a.id)} className="panel space-y-4 p-4">
    <div className="flex items-start justify-between gap-3">
     <div><h2 className="font-semibold">{String(a.name)}</h2><p className="text-xs text-ivory-3">{a.username?String(a.username):"No account yet"}</p></div>
     <span className="rounded-full bg-surface-3 px-2 py-1 text-xs">{!a.username?"Not set":a.account_active?"Enabled":"Disabled"}</span>
    </div>
    <form action={saveStaffAccount} className="grid grid-cols-2 gap-2">
     <input type="hidden" name="staffId" value={String(a.id)}/>
     <label className="col-span-2 text-xs">Username<input required name="username" pattern="[a-z0-9._-]{3,40}" defaultValue={String(a.username||"")} autoComplete="off" className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <label className="col-span-2 text-xs">New password (at least 12 characters)<input name="password" type="password" minLength={12} maxLength={128} required autoComplete="new-password" className="mt-1 h-11 w-full rounded-xl border bg-surface-2 px-3 text-base"/></label>
     <button disabled={!a.staff_active} className="col-span-2 min-h-11 rounded-xl bg-ivory font-semibold text-obsidian disabled:opacity-40">Create / change credentials</button>
    </form>
    {a.username&&<form action={setStaffAccountActive}><input type="hidden" name="staffId" value={String(a.id)}/><input type="hidden" name="active" value={a.account_active?"false":"true"}/><button className="w-full rounded-xl border border-line-strong py-2 text-sm">{a.account_active?"Disable staff login":"Enable staff login"}</button></form>}
   </section>)}
   {!accounts.length&&<p className="panel p-5 text-sm text-ivory-3">Add barbers under Settings → Team first.</p>}
  </div>
  <p className="text-xs text-ivory-3">Passwords are not stored in plaintext and cannot be displayed after saving.</p>
 </PageBody>
}
