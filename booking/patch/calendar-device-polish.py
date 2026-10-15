from pathlib import Path
import re
root=Path('/app')

p=root/'src/components/agenda/day-grid.tsx'; s=p.read_text(encoding='utf-8')
# Show a stable three-column mobile viewport; page through the team with controls.
s=s.replace('  const staffScrollRef=useRef<HTMLDivElement>(null)\n  const [mobileMode,setMobileMode] = useState(false)\n  const visibleStaff=staff', '''  const [mobileMode,setMobileMode] = useState(false)
  const [staffPage,setStaffPage] = useState(0)
  const visibleStaff=mobileMode ? staff.slice(staffPage,staffPage+3) : staff
  useEffect(()=>setStaffPage((page)=>Math.min(page,Math.max(0,staff.length-3))),[staff.length])''',1)
s=re.sub(r'        \{mobileMode && staff.length>3 && <div className="flex items-center justify-end gap-1 border-b border-line px-2 py-1 sm:hidden">.*?        </div>\}\n', '', s, count=1, flags=re.S)
s=s.replace('<div ref={staffScrollRef} data-calendar-scroll aria-label="Barber timeline" data-visible-staff={staff.length} className="min-w-0 overflow-x-auto overflow-y-hidden overscroll-x-contain scroll-thin">\n          <div data-calendar-grid className={mobileMode?"min-w-full":"min-w-[620px]"} style={{minWidth:mobileMode&&staff.length>3?44+staff.length*112:undefined}}>', '<div data-calendar-scroll aria-label="Barber timeline" data-visible-staff={visibleStaff.length} data-total-staff={staff.length} className="min-w-0 overflow-x-hidden overflow-y-hidden overscroll-x-none">\n          <div data-calendar-grid className="w-full min-w-0">',1)
s=s.replace('gridTemplateColumns: "44px repeat("+staff.length+", minmax("+(mobileMode&&staff.length>3?"112px":"0px")+",1fr))"', 'gridTemplateColumns: "44px repeat("+visibleStaff.length+", minmax(0,1fr))"',2)
old='<div className="sticky left-0 z-30 bg-obsidian" />'
new='''<div className="sticky left-0 z-30 flex items-center justify-center gap-0.5 bg-obsidian">
                {mobileMode && staff.length>3 && <>
                  <button type="button" data-testid="calendar-staff-prev" aria-label="Previous barbers" disabled={staffPage===0} onClick={()=>setStaffPage((page)=>Math.max(0,page-1))} className="grid size-[19px] place-items-center rounded border border-line text-ivory-2 disabled:opacity-30"><ChevronLeft className="size-3.5"/></button>
                  <button type="button" data-testid="calendar-staff-next" aria-label="Next barbers" disabled={staffPage>=staff.length-3} onClick={()=>setStaffPage((page)=>Math.min(staff.length-3,page+1))} className="grid size-[19px] place-items-center rounded border border-line text-ivory-2 disabled:opacity-30"><ChevronRight className="size-3.5"/></button>
                </>}
              </div>'''
if old not in s: raise RuntimeError('staff control mount missing')
s=s.replace(old,new,1)
# Status palette requested by user: new blue, confirmed neutral, active green, done yellow, canceled red.
s=s.replace('a.status === "en_curso" && "border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset"','a.status === "en_curso" && "border-l-emerald-500 bg-emerald-400/15 ring-1 ring-emerald-400/30 ring-inset"')
s=s.replace('a.status === "confirmado" && "border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset"','a.status === "confirmado" && "border-l-slate-400 bg-slate-400/10 ring-1 ring-slate-300/20 ring-inset"')
s=s.replace('a.status === "pendiente" && "border-l-orange-500 bg-orange-400/15 ring-1 ring-orange-400/25 ring-inset"','a.status === "pendiente" && "border-l-sky-400 bg-sky-300/15 ring-1 ring-sky-300/30 ring-inset"')
s=s.replace('a.status === "completado" && "border-l-amber-500 bg-amber-400/15 ring-1 ring-amber-400/25 ring-inset"','a.status === "completado" && "border-l-amber-500 bg-amber-300/20 ring-1 ring-amber-300/30 ring-inset"')
# Rename accessibility labels to the translated locale layer's plain-key bridge.
s=s.replace('aria-label="Previous barbers"','aria-label="←"').replace('aria-label="Next barbers"','aria-label="→"')
p.write_text(s,encoding='utf-8')

p=root/'src/components/shell/booking-workspace-shell.tsx'; s=p.read_text(encoding='utf-8')
s=s.replace('import { useState } from "react"','import { useRef, useState } from "react"',1)
s=s.replace(' const [open,setOpen]=useState(false)',' const [open,setOpen]=useState(false)\n const menuTouch=useRef<{x:number;y:number}|null>(null)',1)
# remove the whole top header, preserving main calendar region.
s,n=re.subn(r'   <header className="z-30 flex h-14.*?</header>\n', '', s, count=1, flags=re.S)
if n!=1: raise RuntimeError('calendar header not found')
s=s.replace('className="fixed inset-y-0 left-0 z-50 flex w-[min(84vw,340px)] flex-col overflow-y-auto overscroll-contain border-r border-line bg-obsidian p-4 shadow-2xl transition-transform duration-200 "+(open?"visible translate-x-0":"invisible -translate-x-full pointer-events-none")', 'className="fixed inset-y-0 right-0 z-50 flex w-[min(88vw,360px)] flex-col overflow-x-hidden overflow-y-auto overscroll-contain border-l border-line bg-obsidian p-3 shadow-2xl transition-transform duration-200 touch-pan-y "+(open?"visible translate-x-0":"invisible translate-x-full pointer-events-none")')
s=s.replace('aria-label="Calendar menu" aria-hidden={!open} inert={!open}>', '''aria-label="Calendar menu" aria-hidden={!open} inert={!open}
       onTouchStart={(event)=>{const touch=event.touches[0];menuTouch.current={x:touch.clientX,y:touch.clientY}}}
       onTouchEnd={(event)=>{const start=menuTouch.current;menuTouch.current=null;if(!start)return;const touch=event.changedTouches[0];const dx=touch.clientX-start.x;const dy=touch.clientY-start.y;if(dx>56&&Math.abs(dx)>Math.abs(dy))setOpen(false)}}>''',1)
s=s.replace('<div className="flex items-center justify-between gap-3 pb-6"><div className="font-semibold">Booking · Calendar</div><button aria-label="Close menu" onClick={()=>setOpen(false)} className="grid size-10 place-items-center"><X/></button></div>\n       <div className="mb-4 rounded-xl border border-line bg-surface-1 p-3"><div id="booking-calendar-menu-controls"/></div>', '<div className="mb-3 flex min-h-10 items-center gap-2 border-b border-line pb-2"><div className="min-w-0 flex-1 truncate text-[13px] font-semibold">Запис · Календар</div><div id="booking-calendar-menu-controls" className="shrink-0 origin-right scale-[0.82]"/><button aria-label="Close menu" onClick={()=>setOpen(false)} className="grid size-8 shrink-0 place-items-center rounded-lg border border-line"><X className="size-4"/></button></div>',1)
p.write_text(s,encoding='utf-8')

# Avoid iOS input zoom even when dialogs/sheets render in a portal outside the calendar shell.
p=root/'src/app/globals.css'; s=p.read_text(encoding='utf-8')
s+='''\n\n@media(max-width:767px){
 input,select,textarea{font-size:16px!important;}
 [data-slot="dialog-content"]{box-sizing:border-box;width:calc(100vw - 16px);max-width:calc(100vw - 16px);max-height:calc(100dvh - env(safe-area-inset-top) - env(safe-area-inset-bottom) - 16px);overflow-x:hidden;overflow-y:auto;overscroll-behavior:contain;}
 [data-slot="dialog-content"]>*,[data-slot="sheet-content"]>*{box-sizing:border-box;min-width:0;max-width:100%;}
 [data-slot="sheet-content"]{box-sizing:border-box;width:min(100vw,100%)!important;max-width:100vw!important;min-width:0;overflow-x:hidden;overscroll-behavior:contain;}
 [data-booking-workspace="calendar"] [data-calendar-scroll]{overflow-x:hidden!important;touch-action:pan-y;overscroll-behavior-x:none;}
 [data-booking-workspace="calendar"] [data-calendar-grid]{width:100%;min-width:0;}
}
'''
p.write_text(s,encoding='utf-8')

# Translate payment method names and success toast in the active app locale.
p=root/'src/components/caja/charge-dialog.tsx'; s=p.read_text(encoding='utf-8')
s=s.replace('import { useState, useTransition } from "react"','import { useEffect, useState, useTransition } from "react"',1)
s=s.replace('import { BRAND } from "@/config/brand"','import { BRAND } from "@/config/brand"\nimport { normalizeLocale, type Locale } from "@/i18n/messages"',1)
s=s.replace('  const [method, setMethod] = useState<PaymentMethod>("efectivo")','''  const [method, setMethod] = useState<PaymentMethod>("efectivo")
  const [locale,setLocale]=useState<Locale>("en")
  useEffect(()=>{const read=()=>setLocale(normalizeLocale(localStorage.getItem("booking_locale")));read();window.addEventListener("booking:locale",read);return()=>window.removeEventListener("booking:locale",read)},[])
  const methodLabels:Record<Locale,Record<PaymentMethod,string>>={
    uk:{efectivo:"Готівка",transferencia:"Переказ",mercadopago:"Mercado Pago",debito:"Дебетова картка",credito:"Кредитна картка"},
    en:{efectivo:"Cash",transferencia:"Bank transfer",mercadopago:"Mercado Pago",debito:"Debit card",credito:"Credit card"},
    de:{efectivo:"Barzahlung",transferencia:"Überweisung",mercadopago:"Mercado Pago",debito:"Debitkarte",credito:"Kreditkarte"}
  }
  const copy={
    uk:{paid:"Оплачено",stamps:(n:number,total:number)=>`Картку лояльності оновлено: ${n} з ${total} відміток.`,discount:"Застосовано знижку 50% за карткою лояльності. Розпочато нову картку."},
    en:{paid:"Paid",stamps:(n:number,total:number)=>`Loyalty card updated: ${n} of ${total} stamps.`,discount:"The 50% loyalty discount was applied. A new card has started."},
    de:{paid:"Bezahlt",stamps:(n:number,total:number)=>`Treuekarte aktualisiert: ${n} von ${total} Stempeln.`,discount:"Der Treuerabatt von 50 % wurde angewendet. Eine neue Karte wurde gestartet."}
  }[locale]''',1)
s=s.replace('toast.success(`Cobrado ${formatARS(res.data!.amount)} · ${METHOD_LABEL[method]}`, {','toast.success(`${copy.paid} ${formatARS(res.data!.amount)} · ${methodLabels[locale][method]}`, {',1)
s=s.replace('`${client?.name.split(" ")[0]} suma un sello: ${stampsAfter} de ${BRAND.loyalty.stampsRequired}.`','copy.stamps(stampsAfter,BRAND.loyalty.stampsRequired)',1)
s=s.replace('"Se aplicó el 50% de la tarjeta de fidelidad. Arranca una tarjeta nueva."','copy.discount',1)
s=s.replace('{METHOD_LABEL[m]}','{methodLabels[locale][m]}',1)
s=s.replace('import { formatARS, METHOD_LABEL, METHODS } from "@/lib/money"','import { formatARS, METHODS } from "@/lib/money"',1)
p.write_text(s,encoding='utf-8')
print('BOOKING_CALENDAR_DEVICE_POLISH_INSTALLED')
