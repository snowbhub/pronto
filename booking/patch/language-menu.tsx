"use client"
import { useEffect, useState } from "react"
import { ChevronDown, Languages, Moon, Sun } from "lucide-react"
import { normalizeLocale, type Locale } from "./messages"

type Theme="dark"|"light"
const names:Record<Locale,string>={en:"English",de:"Deutsch",uk:"Українська"}
function storedLocale():Locale {
 if(typeof window==="undefined")return "en"
 try{return normalizeLocale(localStorage.getItem("booking_locale")||document.documentElement.dataset.locale||navigator.language)}
 catch{return "en"}
}
function storedTheme():Theme {
 if(typeof window==="undefined")return "dark"
 try{const t=localStorage.getItem("booking_theme");return t==="light"?"light":"dark"}
 catch{return "dark"}
}
export function LocaleThemeControls() {
 const [locale,setLocale]=useState<Locale>("en")
 const [theme,setTheme]=useState<Theme>("dark")
 const [open,setOpen]=useState(false)
 useEffect(()=>{setLocale(storedLocale());setTheme(storedTheme())},[])
 function choose(next:Locale){
   setLocale(next);setOpen(false)
   localStorage.setItem("booking_locale",next)
   document.cookie="booking_locale="+next+"; Path=/; Max-Age=31536000; SameSite=Lax"
   document.documentElement.dataset.locale=next
   document.documentElement.lang=next
   window.dispatchEvent(new Event("booking:locale"))
 }
 function toggle(){
   const next:Theme=theme==="dark"?"light":"dark"
   setTheme(next)
   localStorage.setItem("booking_theme",next)
   document.documentElement.dataset.theme=next
   document.documentElement.classList.toggle("dark",next==="dark")
 }
 return <div className="fixed right-3 top-3 z-[90] sm:right-5 sm:top-4">
   <div className="flex h-10 items-center gap-0.5 rounded-full border border-line-strong bg-surface-1/95 p-1 shadow-lg backdrop-blur-xl">
     <button type="button" onClick={()=>setOpen(v=>!v)} aria-expanded={open} aria-label="Change language" className="flex h-8 items-center gap-1.5 rounded-full px-2 text-xs font-semibold text-ivory hover:bg-surface-3">
       <Languages className="size-3.5"/><span>{locale==="uk"?"UA":locale.toUpperCase()}</span><ChevronDown className="size-3"/>
     </button>
     <span className="h-4 w-px bg-line-strong"/>
     <button type="button" onClick={toggle} aria-label={theme==="dark"?"Use light theme":"Use dark theme"} className="grid size-8 place-items-center rounded-full text-ivory-2 hover:bg-surface-3">
       {theme==="dark"?<Sun className="size-4"/>:<Moon className="size-4"/>}
     </button>
   </div>
   {open&&<div className="absolute right-0 top-12 min-w-44 overflow-hidden rounded-2xl border border-line-strong bg-surface-1 p-1.5 shadow-xl">
     {(["en","de","uk"] as Locale[]).map(x=><button key={x} type="button" onClick={()=>choose(x)} aria-current={locale===x?"true":undefined} className={"flex w-full items-center justify-between rounded-xl px-3 py-2.5 text-left text-sm "+(locale===x?"bg-surface-3 font-semibold text-ivory":"text-ivory-2 hover:bg-surface-2")}>
       {names[x]}<span className="text-xs text-ivory-3">{x==="uk"?"UA":x.toUpperCase()}</span>
     </button>)}
   </div>}
 </div>
}
