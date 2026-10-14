"use client"
import { useState,useTransition } from "react"
import { useRouter } from "next/navigation"
import { createStaffAppointment } from "@/lib/staff/booking-actions"
export function StaffBookingForm({options}:{options:{value:string;label:string}[]}){
 const router=useRouter()
 const [error,setError]=useState("")
 const [success,setSuccess]=useState("")
 const [pending,start]=useTransition()
 return <form className="space-y-3" onSubmit={e=>{
  e.preventDefault()
  setError("");setSuccess("")
  const form=e.currentTarget
  const data=new FormData(form)
  start(async()=>{const result=await createStaffAppointment(data);if(!result.ok)setError(result.error||"Failed to create booking");else{setSuccess("Appointment created");form.reset();router.refresh()}})
 }}>
  <label className="block text-sm text-ivory-2">Service and available time
   <select name="slot" required className="mt-1 min-h-12 w-full min-w-0 rounded-xl border border-line-strong bg-surface-2 px-3 text-base">{options.map(o=><option value={o.value} key={o.value}>{o.label}</option>)}</select>
  </label>
  <label className="block text-sm text-ivory-2">Client name<input required name="name" minLength={2} maxLength={80} className="mt-1 h-12 w-full rounded-xl border border-line-strong bg-surface-2 px-3 text-base"/></label>
  <label className="block text-sm text-ivory-2">Phone<input required name="phone" type="tel" inputMode="tel" className="mt-1 h-12 w-full rounded-xl border border-line-strong bg-surface-2 px-3 text-base"/></label>
  {error&&<p role="alert" className="text-sm text-danger">{error}</p>}
  {success&&<p role="status" className="text-sm text-ok">{success}</p>}
  <button disabled={pending||!options.length} className="min-h-12 w-full rounded-xl bg-ivory font-semibold text-obsidian disabled:opacity-40">{pending?"Saving…":"Create appointment"}</button>
 </form>
}
