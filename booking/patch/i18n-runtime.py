from pathlib import Path
import re
root=Path("/app")
p=root/"src/i18n/messages.ts"
s=p.read_text(encoding="utf-8")
start=s.index("export function translateText(")
stop=s.index("export const t=",start)
replacement=r'''type Pair={source:string;target:string}
const spanishEntries:Pair[]=[...ROWS].filter(r=>String(r.es)!==String(r.en)).map(r=>({source:r.es,target:r.en})).sort((a,b)=>b.source.length-a.source.length)
const localeEntries:Record<"de"|"uk",Pair[]>={
  de:[...ROWS].filter(r=>String(r.en)!==String(r.de)).map(r=>({source:r.en,target:r.de})).sort((a,b)=>b.source.length-a.source.length),
  uk:[...ROWS].filter(r=>String(r.en)!==String(r.uk)).map(r=>({source:r.en,target:r.uk})).sort((a,b)=>b.source.length-a.source.length),
}
const exactEnglish=new Map<string,(typeof ROWS)[number]>()
const exactSpanish=new Map<string,(typeof ROWS)[number]>()
for(const row of ROWS){
  if(!exactEnglish.has(row.en))exactEnglish.set(row.en,row)
  if(!exactSpanish.has(row.es))exactSpanish.set(row.es,row)
}
function form(n:number,one:string,few:string,many:string):string{
  const last=n%10,ten=n%100
  return ten>=11&&ten<=14?many:last===1?one:last>=2&&last<=4?few:many
}
const MONTHS_UK:Record<string,string>={
  Січень:"січня",Лютий:"лютого",Березень:"березня",Квітень:"квітня",
  Травень:"травня",Червень:"червня",Липень:"липня",Серпень:"серпня",
  Вересень:"вересня",Жовтень:"жовтня",Листопад:"листопада",Грудень:"грудня",
}
function grammar(text:string,locale:Locale){
  if(locale!=="uk")return text
  let out=text.replace(/\b(\d{1,2})\s+(Січень|Лютий|Березень|Квітень|Травень|Червень|Липень|Серпень|Вересень|Жовтень|Листопад|Грудень)(?=$|[\\s.,!?])/g,
    (_full,d,month)=>d+" "+MONTHS_UK[month])
  const endings:[string,string,string,string][]=[
    ["записи","запис","записи","записів"],
    ["відвідувань","відвідування","відвідування","відвідувань"],
    ["послуги","послуга","послуги","послуг"],
    ["оплат","оплата","оплати","оплат"],
    ["клієнти","клієнт","клієнти","клієнтів"],
    ["співробітники","співробітник","співробітники","співробітників"],
  ]
  for(const [word,one,few,many] of endings){
    out=out.replace(new RegExp("(\\d+)\\s+"+word+"(?=$|[^А-Яа-яІіЇїЄєҐґ])","g"),
      (_full,number)=>number+" "+form(Number(number),one,few,many))
  }
  return out
}
const cache=new Map<string,string>()
function replaceOnce(input:string,pairs:Pair[]):string{
  let text=input
  const replacements:string[]=[]
  for(const {source,target} of pairs){
    if(!source||!text.includes(source))continue
    const mark=()=>String.fromCharCode(0xe000)+(replacements.push(target)-1)+String.fromCharCode(0xe001)
    if(/^[a-zA-Z]+$/.test(source)){
      const safe=source
      text=text.replace(new RegExp("(?<![a-zA-Z])"+safe+"(?![a-zA-Z])","g"),mark)
    }else text=text.split(source).join(mark())
  }
  return text.replace(/\uE000(\d+)\uE001/g,(_whole,i)=>replacements[Number(i)]||"")
}
export function translateText(value:string,locale:Locale):string{
  if(!value||!value.trim())return value
  const key=locale+"\0"+value
  const known=cache.get(key)
  if(known!==undefined)return known
  const middle=value.trim()
  const exact=exactEnglish.get(middle)||exactSpanish.get(middle)
  if(exact){
    const translated=locale==="en"?exact.en:locale==="de"?exact.de:exact.uk
    const first=value.indexOf(middle)
    const final=value.slice(0,first)+translated+value.slice(first+middle.length)
    const answer=grammar(final,locale)
    if(cache.size>2400)cache.clear()
    cache.set(key,answer)
    return answer
  }
  const canonical=replaceOnce(value,spanishEntries)
  const output=grammar(locale==="en"?canonical:replaceOnce(canonical,localeEntries[locale]),locale)
  if(cache.size>2400)cache.clear()
  cache.set(key,output)
  return output
}
'''
s=s[:start]+replacement+s[stop:]
p.write_text(s,encoding="utf-8")
p=root/"src/lib/time.ts"
s=p.read_text(encoding="utf-8").replace('new Intl.DateTimeFormat("es-AR"', 'new Intl.DateTimeFormat("en-GB"')
p.write_text(s,encoding="utf-8")
print("BOOKING_I18N_RUNTIME_REWRITTEN")
