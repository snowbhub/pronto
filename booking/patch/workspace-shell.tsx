"use client"
import Link from "next/link"
import { usePathname } from "next/navigation"
import { useState } from "react"
import { CalendarDays, LayoutDashboard, Menu, Plus, Package, CreditCard, Scissors, Settings2, Users, X, Home } from "lucide-react"
import { useNewAppointment } from "@/components/agenda/new-appointment"
import { CalendarMonthPicker } from "./calendar-month-picker"

export function BookingWorkspaceShell({ children, sidebar, topbar, mobileNav }:{
 children:React.ReactNode; sidebar:React.ReactNode;topbar:React.ReactNode; mobileNav:React.ReactNode
}) {
 const pathname=usePathname()
 const isCalendar=pathname==="/agenda"
 const [open,setOpen]=useState(false)
 const {open:openBooking}=useNewAppointment()
 if(!isCalendar)return <div data-booking-workspace="admin" className="flex h-dvh w-full min-w-0 flex-col overflow-hidden lg:h-auto lg:min-h-dvh lg:flex-row lg:overflow-visible">
   {sidebar}
   <div className="flex min-h-0 min-w-0 flex-1 flex-col">{topbar}<main className="min-h-0 min-w-0 flex-1 overflow-x-hidden overflow-y-auto overscroll-contain pb-4 lg:overflow-visible lg:pb-10">{children}</main></div>
   {mobileNav}
 </div>
 return <div data-booking-workspace="calendar" className="flex h-dvh min-h-0 w-full max-w-full flex-col overflow-hidden bg-obsidian text-ivory">
   <header className="z-30 flex h-14 shrink-0 items-center justify-between gap-2 border-b border-line bg-obsidian px-2.5 sm:px-5" aria-label="Calendar workspace">
     <div className="flex min-w-0 items-center gap-2">
       <button type="button" data-testid="calendar-mode-menu" onClick={()=>setOpen(v=>!v)} aria-label="Calendar menu" aria-expanded={open}
        className="grid size-10 shrink-0 place-items-center rounded-xl border border-line-strong bg-surface-1 text-ivory">
         {open?<X className="size-5"/>:<Menu className="size-5"/>}
       </button>
       <span className="truncate text-sm font-semibold sm:text-base">Calendar</span>
     </div>
     <div className="flex shrink-0 items-center gap-2">
       <div id="booking-header-actions"/>

     </div>
   </header>
   <main className="min-h-0 min-w-0 flex-1 overflow-y-auto overflow-x-hidden overscroll-contain">{children}</main>
   <nav aria-label="Calendar quick actions" className="z-30 grid h-[calc(64px+env(safe-area-inset-bottom))] shrink-0 grid-cols-3 items-center border-t border-line bg-obsidian px-4 pb-[env(safe-area-inset-bottom)]">
     <Link href="/agenda" className="flex min-h-12 flex-col items-center justify-center gap-1 text-[11px] text-ivory-2"><CalendarDays className="size-5"/>Today</Link>
     <button type="button" aria-label="New appointment" data-testid="calendar-new-booking" onClick={()=>openBooking()} className="flex min-h-12 flex-col items-center justify-center gap-1 text-[11px] font-semibold text-ivory">
       <span className="grid size-11 place-items-center rounded-full bg-ivory text-obsidian"><Plus className="size-6"/></span>
     </button>
     <button type="button" aria-label="Open menu" onClick={()=>setOpen(true)} className="flex min-h-12 flex-col items-center justify-center gap-1 text-[11px] text-ivory-2"><Menu className="size-5"/>Menu</button>
   </nav>
   {open&&<>
     <button type="button" aria-label="Close calendar menu" onClick={()=>setOpen(false)} className="fixed inset-0 z-40 bg-black/60"/>
     <aside className="fixed inset-y-0 left-0 z-50 flex w-[min(84vw,340px)] flex-col overflow-y-auto overscroll-contain border-r border-line bg-obsidian p-4 shadow-2xl" aria-label="Calendar menu">
       <div className="flex items-center justify-between gap-3 pb-6"><div className="font-semibold">Booking · Calendar</div><button aria-label="Close menu" onClick={()=>setOpen(false)} className="grid size-10 place-items-center"><X/></button></div>
       <CalendarMonthPicker onNavigate={()=>setOpen(false)}/>
       <div className="grid grid-cols-2 gap-2">
         {([
          ["/agenda","Calendar",CalendarDays],["/","Administration",LayoutDashboard],
          ["/inventory","Products",Package],["/cash-management","Sales & cash",CreditCard],
          ["/ajustes?tab=equipo","Staff",Users],["/ajustes?tab=servicios","Services",Scissors],
          ["/ajustes","Settings",Settings2]
         ] as const).map(([href,label,Icon])=><Link key={href} href={href} onClick={()=>setOpen(false)}
          className="flex min-h-14 min-w-0 flex-col items-center justify-center gap-1 rounded-xl border border-line bg-surface-1 px-2 py-2 text-center text-[11px] font-medium"><Icon className="size-5 text-ivory-3"/>{label}</Link>)}
       </div>
       <button type="button" onClick={()=>{setOpen(false);openBooking()}} className="mt-5 flex min-h-12 items-center justify-center gap-2 rounded-xl bg-ivory font-semibold text-obsidian"><Plus className="size-5"/>New booking</button>
     </aside>
   </>}
 </div>
}
