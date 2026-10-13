from pathlib import Path
ROOT=Path("/app")
BUNDLE=Path("/tmp/booking-patch")
(ROOT/"src/components/booking/booking-flow.tsx").write_text((BUNDLE/"modern-booking.tsx").read_text(encoding="utf-8"),encoding="utf-8")
# Preserve booking data contracts; change presentation of the public entry page only.
p=ROOT/"src/app/reservar/page.tsx"
s=p.read_text(encoding="utf-8")
start=s.index("  return (")
s=s[:start]+'''  return (
    <div className="min-h-dvh bg-obsidian text-ivory">
      <header className="sticky top-0 z-30 border-b border-line bg-obsidian/95 backdrop-blur-xl">
        <div className="mx-auto flex max-w-2xl items-center gap-3 px-4 py-4 sm:px-6">
          <div className="grid size-11 shrink-0 place-items-center rounded-xl bg-surface-2">
            <BookingMark size={29}/>
          </div>
          <div className="min-w-0 flex-1">
            <div className="text-lg font-bold tracking-tight">Booking</div>
            <div className="truncate text-xs text-ivory-3">{BRAND.address}</div>
          </div>
        </div>
      </header>
      <main className="pt-7">
        <BookingFlow services={s.services} staff={s.staff} busy={busy} now={n.toISOString()}
          stepMin={s.shopSettings.slotStepMin}
          deposit={s.shopSettings.depositEnabled ? { amount: s.shopSettings.depositAmount, holdMin: s.shopSettings.depositHoldMin } : null}/>
      </main>
      <footer className="border-t border-line px-4 py-7 text-center text-xs text-ivory-3">Booking · Appointments made simple</footer>
    </div>
  )
}
'''
s=s.replace('import { VirexMark } from "@/components/brand/virex-mark"','import { BookingMark } from "@/components/brand/virex-mark"')
p.write_text(s,encoding="utf-8")
# Reactive event-driven locale switch with no navigation/reload.
p=ROOT/"src/i18n/controls.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('location.reload()','document.documentElement.dataset.locale=x;document.documentElement.lang=x;window.dispatchEvent(new Event("booking:locale"))')
s=s.replace('fixed right-3 bottom-20 z-[90] flex items-center gap-1 rounded-xl border border-line-strong bg-surface-1/95 p-1 shadow-lg backdrop-blur lg:right-5 lg:bottom-5','fixed right-3 top-3 z-[90] flex items-center gap-0.5 rounded-full border border-line-strong bg-surface-1/95 p-1 shadow-lg backdrop-blur')
s=s.replace('<span className="grid size-8 place-items-center text-ivory-3" aria-hidden><Languages className="size-4"/></span>','')
s=s.replace('h-8 rounded-lg px-2 text-[11px]','h-8 rounded-full px-2 text-[11px]')
s=s.replace('mx-0.5 h-5 w-px','mx-0.5 h-4 w-px')
p.write_text(s,encoding="utf-8")
# Re-translate from original English source on locale change and on dynamic DOM additions.
p=ROOT/"src/i18n/bridge.tsx"
p.write_text(r'''"use client"
import { useEffect } from "react"
import { normalizeLocale, translateText, type Locale } from "./messages"
const ATTRS=["aria-label","title","placeholder"] as const
const originals=new WeakMap<Node,string>()
const originalAttrs=new WeakMap<Element,Map<string,string>>()
function selectedLocale():Locale{
  try { const v=localStorage.getItem("booking_locale"); if(v)return normalizeLocale(v) } catch {}
  return normalizeLocale(document.documentElement.dataset.locale || navigator.language)
}
function translate(root:Node,locale:Locale){
  const nodes:Node[]=[]
  if(root.nodeType===Node.TEXT_NODE) nodes.push(root)
  else { const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT);let node:Node|null;while((node=walker.nextNode()))nodes.push(node) }
  for(const node of nodes){
    const parent=node.parentElement
    if(!parent||["SCRIPT","STYLE","CODE","PRE","TEXTAREA","OPTION"].includes(parent.tagName)||parent.closest("[data-i18n-native]"))continue
    if(!originals.has(node)) originals.set(node,node.nodeValue||"")
    const source=originals.get(node)||""
    if(!source.trim())continue
    const translated=translateText(source,locale)
    if(node.nodeValue!==translated)node.nodeValue=translated
  }
  const elements=root instanceof Element?[root,...root.querySelectorAll("*")]:root instanceof Document?[...root.querySelectorAll("*")]:[]
  for(const el of elements){
    if(el.closest("[data-i18n-native]"))continue
    let map=originalAttrs.get(el)
    if(!map){map=new Map();originalAttrs.set(el,map)}
    for(const attr of ATTRS){const value=el.getAttribute(attr);if(value===null)continue;if(!map.has(attr))map.set(attr,value);const next=translateText(map.get(attr)!,locale);if(value!==next)el.setAttribute(attr,next)}
  }
}
export function LocaleBridge(){
  useEffect(()=>{
    let locale=selectedLocale()
    const render=()=>{locale=selectedLocale();document.documentElement.lang=locale;document.documentElement.dataset.locale=locale;translate(document.documentElement,locale)}
    render()
    const observer=new MutationObserver(records=>{
      for(const record of records){
        if(record.type==="characterData"){
          const node=record.target
          // React may replace a text node's value; recognize new source instead of overwriting.
          const before=originals.get(node)
          if(before!==undefined && node.nodeValue!==translateText(before,locale))originals.set(node,node.nodeValue||"")
          translate(node,locale)
        }
        for(const node of record.addedNodes) if(node.nodeType===Node.TEXT_NODE||node.nodeType===Node.ELEMENT_NODE)translate(node,locale)
      }
    })
    observer.observe(document.documentElement,{subtree:true,childList:true,characterData:true})
    window.addEventListener("booking:locale",render)
    return()=>{observer.disconnect();window.removeEventListener("booking:locale",render)}
  },[])
  return null
}
''',encoding="utf-8")
# Localization-native React subtree is translated by its own reactive dictionary.
p=ROOT/"src/components/booking/booking-flow.tsx"
s=p.read_text(encoding="utf-8").replace('className="booking-modern mx-auto','data-i18n-native className="booking-modern mx-auto')
p.write_text(s,encoding="utf-8")
print("MODERN_BOOKING_UI_APPLIED")
