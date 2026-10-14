"use client"
import Link from "next/link"
import { useEffect,useMemo,useState } from "react"
import { ChevronLeft,ChevronRight } from "lucide-react"

export function CalendarMonthPicker({onNavigate}:{onNavigate:()=>void}){
 const [month,setMonth]=useState(()=>new Date().toISOString().slice(0,7))
 const [selected,setSelected]=useState("")
 const [locale,setLocale]=useState("en")
 useEffect(()=>{
  const update=()=>{
    const language=document.documentElement.lang
    setLocale(language==="uk"?"uk":language==="de"?"de":"en")
  }
  update()
  window.addEventListener("booking:locale",update)
  const date=new URLSearchParams(window.location.search).get("dia")
  if(date&&/^\d{4}-\d{2}-\d{2}$/.test(date)){
    setSelected(date);setMonth(date.slice(0,7))
  }
  return()=>window.removeEventListener("booking:locale",update)
 },[])
 const first=new Date(month+"-01T12:00:00Z")
 const offset=(first.getUTCDay()+6)%7
 const cells=useMemo(()=>Array.from({length:42},(_,i)=>{
   const d=new Date(month+"-01T12:00:00Z")
   d.setUTCDate(1-offset+i)
   return d.toISOString().slice(0,10)
 }),[month,offset])
 const lang=locale==="uk"?"uk-UA":locale==="de"?"de-DE":"en-GB"
 const label=first.toLocaleDateString(lang,{month:"long",year:"numeric",timeZone:"UTC"})
 const shift=(amount:number)=>{
   const d=new Date(month+"-01T12:00:00Z")
   d.setUTCMonth(d.getUTCMonth()+amount)
   setMonth(d.toISOString().slice(0,7))
 }
 const today=new Date().toISOString().slice(0,10)
 return <section className="mb-4 rounded-2xl border border-line bg-surface-1 p-3" aria-label="Month calendar">
   <div className="mb-3 flex items-center justify-between gap-2">
     <button onClick={()=>shift(-1)} className="grid size-9 place-items-center rounded-lg border border-line-strong" type="button" aria-label="Previous month"><ChevronLeft className="size-4"/></button>
     <h2 className="text-sm font-semibold capitalize">{label}</h2>
     <button onClick={()=>shift(1)} className="grid size-9 place-items-center rounded-lg border border-line-strong" type="button" aria-label="Next month"><ChevronRight className="size-4"/></button>
   </div>
   <div className="grid grid-cols-7 text-center text-[10px] uppercase text-ivory-3">
     {["Mon","Tue","Wed","Thu","Fri","Sat","Sun"].map(x=><span className="py-2" key={x}>{x}</span>)}
   </div>
   <div className="grid grid-cols-7 gap-0.5">
    {cells.map(d=><Link key={d} href={"/agenda?dia="+d} onClick={onNavigate} aria-current={selected===d?"date":undefined}
      className={"num grid size-9 place-items-center rounded-full text-xs transition-colors "+
        (d===selected?"bg-ivory font-bold text-obsidian":d===today?"border border-ivory font-semibold text-ivory":d.slice(0,7)===month?"text-ivory hover:bg-surface-3":"text-ivory-3/40")}>
      {Number(d.slice(8))}
    </Link>)}
   </div>
 </section>
}
