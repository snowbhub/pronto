from pathlib import Path
import re
root=Path("/app")
p=root/"src/i18n/messages.ts"
s=p.read_text(encoding="utf-8")
start=s.index("export function translateText(")
stop=s.index("export const t=",start)
replacement=r'''type Pair={source:string;target:string}
const spanishEntries:Pair[]=[...ROWS].filter(r=>r.es!==r.en).map(r=>({source:r.es,target:r.en})).sort((a,b)=>b.source.length-a.source.length)
const localeEntries:Record<"de"|"uk",Pair[]>={
  de:[...ROWS].filter(r=>r.en!==r.de).map(r=>({source:r.en,target:r.de})).sort((a,b)=>b.source.length-a.source.length),
  uk:[...ROWS].filter(r=>r.en!==r.uk).map(r=>({source:r.en,target:r.uk})).sort((a,b)=>b.source.length-a.source.length),
}
const cache=new Map<string,string>()
function replaceOnce(input:string,pairs:Pair[]):string{
  let text=input
  const replacements:string[]=[]
  for(const {source,target} of pairs){
    if(!source||!text.includes(source))continue
    const mark=()=>String.fromCharCode(0xe000)+(replacements.push(target)-1)+String.fromCharCode(0xe001)
    if(/^[a-zA-Z]+$/.test(source)){
      const safe=source.replace(/[.*+?^$()|[\]{}]/g,"\\$&")
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
  const canonical=replaceOnce(value,spanishEntries)
  const output=locale==="en"?canonical:replaceOnce(canonical,localeEntries[locale])
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
