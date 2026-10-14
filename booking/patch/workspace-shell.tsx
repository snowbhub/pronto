"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import { CalendarDays, LayoutDashboard, Menu, Plus, Package, CreditCard, Scissors, Settings2, Users, X } from "lucide-react"
import { useNewAppointment } from "@/components/agenda/new-appointment"

export function BookingWorkspaceShell({ children, sidebar, topbar, mobileNav }:{
 children:React.ReactNode; sidebar:React.ReactNode;topbar:React.ReactNode; mobileNav:React.ReactNode
}) {
 const pathname=usePathname()
 const isCalendar=pathname==="/agenda"
 const [open,setOpen]=useState(false)
 const {open:openBooking}=useNewAppointment()
 if(!isCalendar)return <div data-booking-workspace="admin" className="flex min-h-dvh">
   {sidebar}
   <div className="flex min-w-0 flex-1 flex-col">{topbar}<main className="min-w-0 flex-1 pb-24 lg:pb-10">{children}</main></div>
   {mobileNav}
 </div>
 return <div data-booking-workspace="calendar" className="flex h-dvh min-h-0 w-full max-w-full flex-col overflow-hidden bg-obsidian text-ivory">
   <header className="z-40 flex h-14 shrink-0 items-center justify-between gap-2 border-b border-line bg-obsidian px-3 sm:px-5" aria-label="Calendar workspace">
     <div className="flex min-w-0 items-center gap-2">
       <button type="button" onClick={()=>setOpen(v=>!v)} aria-label="Calendar menu" aria-expanded={open}
        className="grid size-10 shrink-0 place-items-center rounded-xl border border-line-strong bg-surface-1 text-ivory">
         {open?<X className="size-5"/>:<Menu className="size-5"/>}
       </button>
       <CalendarDays className="size-5 shrink-0"/>
       <span className="truncate text-base font-semibold">Calendar</span>
     </div>
     <div className="flex shrink-0 items-center gap-2">
       <div id="booking-header-actions"/>
       <Link href="/" className="inline-flex h-10 items-center gap-1.5 rounded-xl border border-line-strong bg-surface-1 px-3 text-xs font-semibold text-ivory" aria-label="Open administration">
         <LayoutDashboard className="size-4"/><span>Admin</span>
       </Link>
     </div>
   </header>
   <main className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden overscroll-contain">{children}</main>
   <nav aria-label="Calendar quick actions" className="z-30 grid h-[calc(62px+env(safe-area-inset-bottom))] shrink-0 grid-cols-4 items-center border-t border-line bg-obsidian px-3 pb-[env(safe-area-inset-bottom)] sm:mx-auto sm:w-full sm:max-w-3xl">
     <Link href="/cash-management" className="flex flex-col items-center gap-1 text-[11px] text-ivory-2"><CreditCard className="size-5"/>Sales</Link>
     <button type="button" onClick={()=>openBooking()} className="flex flex-col items-center gap-1 text-[11px] font-semibold text-ivory">
       <span className="grid size-10 place-items-center rounded-full bg-ivory text-obsidian"><Plus className="size-5"/></span><span className="sr-only">New booking</span>
     </button>
     <Link href="/inventory" className="flex flex-col items-center gap-1 text-[11px] text-ivory-2"><Package className="size-5"/>Stock</Link>
     <Link href="/" className="flex flex-col items-center gap-1 text-[11px] text-ivory-2"><LayoutDashboard className="size-5"/>Admin</Link>
   </nav>
   {open&&<>
     <button type="button" aria-label="Close calendar menu" onClick={()=>setOpen(false)} className="fixed inset-0 z-40 bg-black/60"/>
     <aside className="fixed inset-y-0 left-0 z-50 flex w-[min(84vw,340px)] flex-col border-r border-line bg-obsidian p-4 shadow-2xl" aria-label="Calendar menu">
       <div className="flex items-center justify-between gap-3 pb-6"><div className="font-semibold">Booking · Calendar</div><button aria-label="Close menu" onClick={()=>setOpen(false)} className="grid size-10 place-items-center"><X/></button></div>
       <div className="grid gap-2">
         {([
          ["/agenda","Calendar",CalendarDays],["/","Administration",LayoutDashboard],
          ["/inventory","Products",Package],["/cash-management","Sales & cash",CreditCard],
          ["/ajustes?tab=equipo","Staff",Users],["/ajustes?tab=servicios","Services",Scissors],
          ["/ajustes","Settings",Settings2]
         ] as const).map(([href,label,Icon])=><Link key={href} href={href} onClick={()=>setOpen(false)}
          className="flex min-h-12 items-center gap-3 rounded-xl border border-line bg-surface-1 px-4 text-sm font-medium"><Icon className="size-5 text-ivory-3"/>{label}</Link>)}
       </div>
       <button type="button" onClick={()=>{setOpen(false);openBooking()}} className="mt-5 flex min-h-12 items-center justify-center gap-2 rounded-xl bg-ivory font-semibold text-obsidian"><Plus className="size-5"/>New booking</button>
     </aside>
   </>}
 </div>
}
