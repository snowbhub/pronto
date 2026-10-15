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
type PhraseRow={es:string;en:string;de:string;uk:string}
const dictionary:readonly PhraseRow[]=ROWS
const exactEnglish=new Map<string,PhraseRow>()
const exactSpanish=new Map<string,PhraseRow>()
for(const row of dictionary){
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
const SHORT_MONTHS:Record<string,[string,string]>={
  Jan:["Jan.","січня"],Feb:["Feb.","лютого"],Mar:["März","березня"],Apr:["Apr.","квітня"],
  May:["Mai","травня"],Jun:["Juni","червня"],Jul:["Juli","липня"],Aug:["Aug.","серпня"],
  Sep:["Sept.","вересня"],Oct:["Okt.","жовтня"],Nov:["Nov.","листопада"],Dec:["Dez.","грудня"]
}
function grammar(text:string,locale:Locale){
  let out=calendarDateText(text,locale)
  if(locale==="de"||locale==="uk"){
    out=out.replace(/(\d{1,2})\s+(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\b/g,
      (_whole,d,month)=>d+" "+SHORT_MONTHS[month][locale==="de"?0:1])
  }
  if(locale==="en"){
    out=out.replace(/\b1\s+bookings\b/g,"1 booking")
      .replace(/\b1\s+visits\b/g,"1 visit")
      .replace(/\b1\s+services\b/g,"1 service")
      .replace(/\b1\s+clients\b/g,"1 client")
    return out
  }
  if(locale==="de"){
    out=out.replace(/\b(Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)(?:,\s*|\s+)(\d{1,2})\s+(Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\b/g,
      (_full,day,date,month)=>day+", "+date+". "+month)
    out=out.replace(/\b1\s+Termine\b/g,"1 Termin")
      .replace(/\b1\s+Besuche\b/g,"1 Besuch")
      .replace(/\b1\s+Leistungen\b/g,"1 Leistung")
      .replace(/\b1\s+Kunden\b/g,"1 Kunde")
    return out
  }
  out=out.replace(/(Понеділок|Вівторок|Середа|Четвер|П’ятниця|П'ятниця|Субота|Неділя)\s+(\d{1,2})\s+([А-Яа-яІіЇїЄєҐґ]+)(?=$|[^\p{L}])/gu,
    (_full,day,date,month)=>day+", "+date+" "+month.toLocaleLowerCase("uk"))
  out=out.replace(/\b(\d{1,2})\s+(Січень|Лютий|Березень|Квітень|Травень|Червень|Липень|Серпень|Вересень|Жовтень|Листопад|Грудень)(?=$|[^\p{L}])/gu,
    (_full,d,month)=>d+" "+MONTHS_UK[month])
  const endings:[string,string,string,string][]=[
    ["записів","запис","записи","записів"],
    ["записи","запис","записи","записів"],
    ["відвідувань","відвідування","відвідування","відвідувань"],
    ["відвідування","відвідування","відвідування","відвідувань"],
    ["послуг","послуга","послуги","послуг"],
    ["послуги","послуга","послуги","послуг"],
    ["оплат","оплата","оплати","оплат"],
    ["оплати","оплата","оплати","оплат"],
    ["клієнти","клієнт","клієнти","клієнтів"],
    ["співробітники","співробітник","співробітники","співробітників"],
  ]
  for(const [word,one,few,many] of endings){
    out=out.replace(new RegExp("(\\d+)\\s+"+word+"(?=$|[^А-Яа-яІіЇїЄєҐґ])","g"),
      (_full,number)=>number+" "+form(Number(number),one,few,many))
  }
  return out
}

const DAY_ALIASES:Record<string,number>={}
const DAY_GROUPS=[
  ["sunday","sun","domingo","dom","sonntag","so","неділя","нд"],
  ["monday","mon","lunes","lun","montag","mo","понеділок","пн"],
  ["tuesday","tue","martes","mar","dienstag","di","вівторок","вт"],
  ["wednesday","wed","miércoles","miercoles","mié","mie","mittwoch","mi","середа","ср"],
  ["thursday","thu","jueves","jue","donnerstag","do","четвер","чт"],
  ["friday","fri","viernes","vie","freitag","fr","п’ятниця","п'ятниця","пт"],
  ["saturday","sat","sábado","sabado","sáb","sab","samstag","sa","субота","сб"],
]
for(let i=0;i<DAY_GROUPS.length;i++)for(const alias of DAY_GROUPS[i])DAY_ALIASES[alias]=i
const SHORT_DAYS=new Set(["sun","dom","so","нд","mon","lun","mo","пн","tue","mar","di","вт","wed","mié","mie","mi","ср","thu","jue","do","чт","fri","vie","fr","пт","sat","sáb","sab","sa","сб"])
const MONTH_GROUPS=[
  {aliases:["january","jan","enero","ene","januar","січень","січня","січ"],en:"January",enShort:"Jan",de:"Januar",deShort:"Jan.",uk:"січень",ukGen:"січня",ukShort:"січ."},
  {aliases:["february","feb","febrero","feb","februar","лютий","лютого","лют"],en:"February",enShort:"Feb",de:"Februar",deShort:"Feb.",uk:"лютий",ukGen:"лютого",ukShort:"лют."},
  {aliases:["march","mar","marzo","märz","март","березень","березня","бер"],en:"March",enShort:"Mar",de:"März",deShort:"März",uk:"березень",ukGen:"березня",ukShort:"бер."},
  {aliases:["april","apr","abril","abr","квітень","квітня","квіт"],en:"April",enShort:"Apr",de:"April",deShort:"Apr.",uk:"квітень",ukGen:"квітня",ukShort:"квіт."},
  {aliases:["may","mayo","mai","травень","травня","трав"],en:"May",enShort:"May",de:"Mai",deShort:"Mai",uk:"травень",ukGen:"травня",ukShort:"трав."},
  {aliases:["june","jun","junio","juni","червень","червня","черв"],en:"June",enShort:"Jun",de:"Juni",deShort:"Juni",uk:"червень",ukGen:"червня",ukShort:"черв."},
  {aliases:["july","jul","julio","juli","липень","липня","лип"],en:"July",enShort:"Jul",de:"Juli",deShort:"Juli",uk:"липень",ukGen:"липня",ukShort:"лип."},
  {aliases:["august","aug","agosto","серпень","серпня","серп"],en:"August",enShort:"Aug",de:"August",deShort:"Aug.",uk:"серпень",ukGen:"серпня",ukShort:"серп."},
  {aliases:["september","sept","sep","septiembre","setiembre","вересень","вересня","вер"],en:"September",enShort:"Sep",de:"September",deShort:"Sept.",uk:"вересень",ukGen:"вересня",ukShort:"вер."},
  {aliases:["october","oct","octubre","oktober","okt","жовтень","жовтня","жовт"],en:"October",enShort:"Oct",de:"Oktober",deShort:"Okt.",uk:"жовтень",ukGen:"жовтня",ukShort:"жовт."},
  {aliases:["november","nov","noviembre","листопад","листопада","лист"],en:"November",enShort:"Nov",de:"November",deShort:"Nov.",uk:"листопад",ukGen:"листопада",ukShort:"лист."},
  {aliases:["december","dec","diciembre","dezember","dez","грудень","грудня","груд"],en:"December",enShort:"Dec",de:"Dezember",deShort:"Dez.",uk:"грудень",ukGen:"грудня",ukShort:"груд."},
]
const MONTH_ALIASES:Record<string,number>={}
for(let i=0;i<MONTH_GROUPS.length;i++)for(const alias of MONTH_GROUPS[i].aliases)MONTH_ALIASES[alias]=i
const SHORT_MONTH_ALIASES=new Set(["jan","ene","feb","mar","abr","apr","jun","jul","ago","aug","sep","sept","oct","okt","nov","dez","dec","січ","лют","бер","квіт","трав","черв","лип","серп","вер","жовт","лист","груд"])
const DAY_FORMS=[
  {en:["Sunday","Sun"],de:["Sonntag","So."],uk:["неділя","нд"]},
  {en:["Monday","Mon"],de:["Montag","Mo."],uk:["понеділок","пн"]},
  {en:["Tuesday","Tue"],de:["Dienstag","Di."],uk:["вівторок","вт"]},
  {en:["Wednesday","Wed"],de:["Mittwoch","Mi."],uk:["середа","ср"]},
  {en:["Thursday","Thu"],de:["Donnerstag","Do."],uk:["четвер","чт"]},
  {en:["Friday","Fri"],de:["Freitag","Fr."],uk:["п’ятниця","пт"]},
  {en:["Saturday","Sat"],de:["Samstag","Sa."],uk:["субота","сб"]},
]
const escapeRegex=(value:string)=>value.replace(/[.*+?^$(){}|[\]\\]/g,"\\const cache=new Map<string,string>()")
const tokenPattern=(tokens:string[])=>tokens.sort((a,b)=>b.length-a.length).map(escapeRegex).join("|")
const DATE_DAYS=tokenPattern(Object.keys(DAY_ALIASES))+"\\.?"
const DATE_MONTHS=tokenPattern(Object.keys(MONTH_ALIASES))+"\\.?"
function cleanCalendarPunctuation(text:string,locale:Locale){
  return locale==="uk"?text.replace(/(\d{1,2}\s+(?:січ|лют|бер|квіт|трав|черв|лип|серп|вер|жовт|лист|груд)\.)\./gu,"$1"):text
}
function dateWord(value:string){return value.toLocaleLowerCase("uk").replace(/\./g,"")}
function calendarDateText(value:string,locale:Locale):string{
  let out=value
  const datePattern=new RegExp("(?<![\\p{L}])("+DATE_DAYS+")(,?\\s+)(\\d{1,2})(?:\\s+(?:de|of))?\\s+("+DATE_MONTHS+")(?:\\s+(\\d{4}))?(?!\\d)","giu")
  out=out.replace(datePattern,(_all,dayRaw,separator,dayNumber,monthRaw,year)=>{
    const dayKey=dateWord(dayRaw),monthKey=dateWord(monthRaw)
    const dayIndex=DAY_ALIASES[dayKey],monthIndex=MONTH_ALIASES[monthKey]
    if(dayIndex===undefined||monthIndex===undefined)return _all
    const short=SHORT_DAYS.has(dayKey)||SHORT_MONTH_ALIASES.has(monthKey)
    const day=DAY_FORMS[dayIndex][locale][short?1:0]
    const month=MONTH_GROUPS[monthIndex]
    if(locale==="de")return day+", "+dayNumber+". "+(short?month.deShort:month.de)+(year?" "+year:"")
    if(locale==="uk")return day+", "+dayNumber+" "+(short?month.ukShort:month.ukGen)+(year?" "+year:"")
    return day+", "+dayNumber+" "+(short?month.enShort:month.en)+(year?" "+year:"")
  })
  const monthDayPattern=new RegExp("(?<![\\p{L}\\p{N}])(\\d{1,2})(\\s+)("+DATE_MONTHS+")(?![\\p{L}])","giu")
  out=out.replace(monthDayPattern,(_all,dayNumber,space,monthRaw)=>{
    const monthIndex=MONTH_ALIASES[dateWord(monthRaw)]
    if(monthIndex===undefined)return _all
    const month=MONTH_GROUPS[monthIndex],short=SHORT_MONTH_ALIASES.has(dateWord(monthRaw))
    if(locale==="de")return dayNumber+". "+(short?month.deShort:month.de)
    if(locale==="uk")return dayNumber+" "+(short?month.ukShort:month.ukGen)
    return dayNumber+" "+(short?month.enShort:month.en)
  })
  const monthYearPattern=new RegExp("(?<![\\p{L}\\p{N}])("+DATE_MONTHS+")\\s+(\\d{4})(?!\\d)","giu")
  out=out.replace(monthYearPattern,(_all,monthRaw,year)=>{
    const month=MONTH_GROUPS[MONTH_ALIASES[dateWord(monthRaw)]]
    if(!month)return _all
    const label=locale==="de"?month.de:locale==="uk"?month.uk:month.en
    return label.charAt(0).toLocaleUpperCase(locale==="uk"?"uk":locale==="de"?"de":"en")+label.slice(1)+" "+year
  })
  return out
}

const cache=new Map<string,string>()
function replaceOnce(input:string,pairs:Pair[]):string{
  let text=input
  const replacements:string[]=[]
  // Every partial match must be bounded at the start/end of a whole word.
  // Never change fragments of employee names, "commission" or service titles.
  const escapePattern=(value:string)=>value.replace(/[.*+?^$()|[\]{}\\]/g,"\\$&")
  for(const {source,target} of pairs){
    if(!source||source.length<2||!text.includes(source))continue
    const mark=()=>String.fromCharCode(0xe000)+(replacements.push(target)-1)+String.fromCharCode(0xe001)
    const startsWord=/^[\p{L}\p{N}]/u.test(source)
    const endsWord=/[\p{L}\p{N}]$/u.test(source)
    const left=startsWord?"(?<![\\p{L}\\p{N}])":""
    const right=endsWord?"(?![\\p{L}\\p{N}])":""
    const regex=new RegExp(left+escapePattern(source)+right,"gu")
    text=text.replace(regex,mark)
  }
  return text.replace(/\uE000(\d+)\uE001/g,(_whole,i)=>replacements[Number(i)]||"")
}
export function translateText(value:string,locale:Locale):string{
  if(!value||!value.trim())return value
  const key=locale+"\0"+value
  const known=cache.get(key)
  if(known!==undefined)return known
  const middle=value.trim()
  // Business brands and customer/staff names are user data, never interface copy.
  if(["Mercado Pago","WhatsApp","Instagram","Zernio","Railway","GitHub"].includes(middle))return value
  const exact=exactEnglish.get(middle)||exactSpanish.get(middle)
  if(!exact && /^[\p{Lu}][\p{L}'’-]+(?:\s+[\p{Lu}][\p{L}'’-]+){1,4}$/u.test(middle))return value
  if(exact){
    const translated=locale==="en"?exact.en:locale==="de"?exact.de:exact.uk
    const first=value.indexOf(middle)
    const final=value.slice(0,first)+translated+value.slice(first+middle.length)
    const answer=cleanCalendarPunctuation(grammar(final,locale),locale)
    if(cache.size>2400)cache.clear()
    cache.set(key,answer)
    return answer
  }
  const canonical=replaceOnce(value,spanishEntries)
  const output=cleanCalendarPunctuation(grammar(locale==="en"?canonical:replaceOnce(canonical,localeEntries[locale]),locale),locale)
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

p=root/"src/i18n/messages.test.ts"
p.write_text(r'''import { describe, expect, it } from "vitest"
import { translateText } from "./messages"

describe("localized calendar dates", () => {
  it("renders English short date labels in Ukrainian", () => {
    expect(translateText("Sat, 17 Oct", "uk")).toBe("сб, 17 жовт.")
  })
  it("normalizes a leftover Spanish short date in Ukrainian", () => {
    expect(translateText("sáb, 17 oct", "uk")).toBe("сб, 17 жовт.")
  })
  it("renders a full English date in Ukrainian", () => {
    expect(translateText("Thursday, 15 October", "uk")).toBe("четвер, 15 жовтня")
  })
  it("normalizes a leftover Spanish full date in Ukrainian", () => {
    expect(translateText("JUEVES, 15 DE OCTUBRE", "uk")).toBe("четвер, 15 жовтня")
  })
  it("renders German date punctuation and month names", () => {
    expect(translateText("Thursday, 15 October", "de")).toBe("Donnerstag, 15. Oktober")
  })
  it("keeps English date formatting canonical", () => {
    expect(translateText("Thursday, 15 October", "en")).toBe("Thursday, 15 October")
  })
  it("localizes a month heading in Ukrainian", () => {
    expect(translateText("October 2026", "uk")).toBe("Жовтень 2026")
  })
})
''',encoding="utf-8")
print("BOOKING_CALENDAR_I18N_TESTS_INSTALLED")

print("BOOKING_I18N_RUNTIME_REWRITTEN")
