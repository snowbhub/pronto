import { chromium } from "playwright"
import { createHmac } from "node:crypto"
import { mkdir, writeFile } from "node:fs/promises"

const base = process.env.BOOKING_BASE_URL || "http://127.0.0.1:3000"
const password = process.env.BOOKING_TEST_PANEL_PASSWORD || ""
const dir = "booking/screenshots"
await mkdir(dir, { recursive:true })
const errors = []
const captures = []
const routes = [
 ["dashboard","/"],["calendar-day","/agenda"],["calendar-week","/agenda?view=week"],
 ["settings-team","/ajustes?tab=equipo"],["settings-services","/ajustes?tab=servicios"],
 ["settings-main","/ajustes"],["clients","/clientes"],["inbox","/bandeja"],
 ["finance","/finanzas"],["cash","/caja"],["inventory","/inventory"],
 ["cash-management","/cash-management"],["payroll","/payroll"],
 ["ranks","/ranks"],["staff-accounts","/staff-accounts"],["analytics","/analytics"],
 ["agent","/agente"],["public-booking","/reservar"],["login","/login"],
 ["staff-login","/staff-login"]
]
const browser=await chromium.launch({headless:true,args:["--no-sandbox"]})
for(const device of [{id:"iphone",width:390,height:844,isMobile:true},{id:"desktop",width:1440,height:900,isMobile:false}]){
 for(const locale of ["uk","de","en"]){
  const context=await browser.newContext({viewport:{width:device.width,height:device.height},deviceScaleFactor:1,isMobile:device.isMobile,hasTouch:device.isMobile,locale:locale==="uk"?"uk-UA":locale==="de"?"de-DE":"en-GB"})
  await context.addCookies([{name:"booking_locale",value:locale,url:base}])
  if(password){
    const cookie=createHmac("sha256",password).update("booking-panel-v1").digest("hex")
    await context.addCookies([{name:"booking_panel",value:cookie,url:base,httpOnly:true}])
  }
  await context.addInitScript(lang=>{
   localStorage.setItem("booking_locale",lang)
   localStorage.setItem("booking_theme","light")
  },locale)
  const page=await context.newPage()
  page.on("pageerror",e=>errors.push({device:device.id,locale,route:page.url(),type:"javascript",detail:e.message}))
  const logFrame=async (name,route)=>{
   await page.waitForTimeout(350)
   const metrics=await page.evaluate(()=>{
    const visible=(el)=>{const rect=el.getBoundingClientRect();const styles=getComputedStyle(el);return styles.display!=="none" && styles.visibility!=="hidden"&&rect.width>0&&rect.height>0}
    const main=document.querySelector('main')
    const fixedNavs=[...document.querySelectorAll('nav')].filter(el=>visible(el)&&getComputedStyle(el).position==="fixed")
    const positionedNavs=[...document.querySelectorAll("nav.booking-app-nav")].filter(visible)
    const navs=positionedNavs.map(el=>{const r=el.getBoundingClientRect();return {top:Math.round(r.top),bottom:Math.round(r.bottom),height:Math.round(r.height)}})
    const visibleText=(document.body.innerText||"").trim()
    return {visibleText:visibleText.slice(0,3500),screenWidth:innerWidth,pageWidth:document.documentElement.scrollWidth,
      bodyTextLength:visibleText.length,mainTextLength:(main?.innerText||"").trim().length,
      workspace:document.querySelector('[data-booking-workspace]')?.getAttribute('data-booking-workspace')||"none",
      fixedNavCount:fixedNavs.length,navs,mainTop:main?Math.round(main.getBoundingClientRect().top):null,
      route:location.pathname,spanish:(visibleText.match(/\b(Empezar|Cobrar|Agendar|Entrando|Confirmado|No vino|Nadie por ahora|Configurar|Cancelar turno|Nuevo turno)\b/g)||[]).slice(0,12)}
   })
   const path=`${dir}/${device.id}-${locale}-${name}.png`
   await page.screenshot({path,animations:"disabled",fullPage:false})
   const item={device:device.id,locale,name,file:path,requestedRoute:route,finalRoute:page.url(),...metrics}
   captures.push(item)
   if(metrics.pageWidth>device.width+3)errors.push({device:device.id,locale,name,type:"horizontal-page-overflow",detail:`${metrics.pageWidth}px page > ${device.width}px viewport`})
   if(name!=="login"&&name!=="staff-login"&&!name.includes("public") && metrics.route==="/login")errors.push({device:device.id,locale,name,type:"unavailable-route",detail:"Redirected to login (QA credentials missing)"})
   if(metrics.workspace==="calendar"&&metrics.fixedNavCount>0)errors.push({device:device.id,locale,name,type:"calendar-navigation-overlap",detail:"Legacy fixed nav remains"})
   if(device.id==="iphone"&&metrics.workspace==="admin"&&metrics.navs.some(n=>n.top<device.height*.40&&n.height>45))errors.push({device:device.id,locale,name,type:"admin-navigation-at-top",detail:JSON.stringify(metrics.navs)})
   if(metrics.spanish.length)errors.push({device:device.id,locale,name,type:"untranslated-spanish",detail:metrics.spanish.join(", ")})

   // Manually observed defects from real screens: check complete sentences, not
   // just an optimistic dictionary-coverage percentage.
   const localeChecks={
     en:[
       ["english-plural",/\b1 (?:bookings|visits|services|clients)\b/],
     ],
     de:[
       ["german-plural",/\b1 (?:Termine|Besuche|Leistungen|Kunden)\b/],
       ["german-calendar-date",/\b(?:Montag|Dienstag|Mittwoch|Donnerstag|Freitag|Samstag|Sonntag)\s+\d{1,2}\s+(?:Januar|Februar|März|April|Mai|Juni|Juli|August|September|Oktober|November|Dezember)\b/],
     ],
     uk:[
       ["unnatural-completed-status",/(?:Обслужено|Обслуговано)/],
       ["incorrect-ukrainian-calendar-date",/(?:Понеділок|Вівторок|Середа|Четвер|П’ятниця|Субота|Неділя)\s+\d{1,2}\s+(?:січня|лютого|березня|квітня|травня|червня|липня|серпня|вересня|жовтня|листопада|грудня)/i],
     ]
   }
   const commonChecks=[
     ["untranslated-finance-paragraph",/(?:comisión \+|vales −|pagos ya hechos|Los dueños no cobran)/],
     ["untranslated-ai-model-note",/(?:Modelo: sin configurar|Cada respuesta se arma|los precios, horarios y reglas)/],
   ]
   if(locale!=="en" && name==="analytics" && /\b(?:Day|Week|Month|Year|Custom)\b/.test(metrics.visibleText))errors.push({device:device.id,locale,name,type:"analytics-period-not-localized",detail:metrics.visibleText.slice(0,220)})
   if(locale==="uk" && name==="analytics" && /Оплати in selected period/.test(metrics.visibleText))errors.push({device:device.id,locale,name,type:"analytics-payment-label-not-localized",detail:"Оплати in selected period"})
   for(const [kind,pattern] of [...commonChecks,...localeChecks[locale]]){
     const found=metrics.visibleText.match(pattern)
     if(found)errors.push({device:device.id,locale,name,type:kind,detail:found[0]})
   }

   if(locale==="uk" && /(Payroll by date range|Set professional ranks|Products, purchases|Create individual passwords|Record expenses by category|Passwords are not stored|Cash movement shows net|Choose a specialist|Choose a service|Admin panon|Registrar pago|Sin leer)/i.test(metrics.visibleText))errors.push({device:device.id,locale,name,type:"untranslated-ukrainian-sentence",detail:metrics.visibleText.match(/.{0,60}(?:Payroll by date range|Set professional ranks|Products, purchases|Create individual passwords|Record expenses by category|Passwords are not stored|Cash movement shows net|Choose a specialist|Choose a service|Admin panon|Registrar pago|Sin leer).{0,90}/i)?.[0]||""})
   // Known defects from manual mobile screenshot review; catch partial words,
   // incorrect declensions, data corruption and untranslated date/payment copy.
   if(locale==="uk"){
     const strictChecks=[
       ["customer-name-corrupted",/Test Клієнт/],
       ["mixed-language-payroll",/\d+%\s+commissi(?:on|у)(?![\p{L}])/u],
       ["incorrect-ukrainian-plural",/\b1\s+(?:записів|відвідувань|послуг)(?![\p{L}])|\b0\s+(?:запис|відвідування|послуга)(?![\p{L}])/u],
       ["untranslated-date",/\b\d{1,2}\s+(?:Sep|Oct|Nov|Dec)\b/],
       ["untranslated-booking-preposition",/\bcon\s+(?:Max|Olena|Danylo)\b/],
       ["untranslated-status",/\b(?:Atendido|Otra hora)\b/],
       ["duplicate-rank",/Стажер\s*\/\s*Стажер/],
       ["uninflected-ukrainian-month",/\d{1,2}\s+(?:Січень|Лютий|Березень|Квітень|Травень|Червень|Липень|Серпень|Вересень|Жовтень|Листопад|Грудень)(?![\p{L}])/u],
       ["untranslated-ai-provider",/(?:ZERNIO_API_KEY required|ZERNIO_WEBHOOK_SECRET required|Configure GEMINI_API_KEY.*in your Railway)/]
     ]
     for(const [type,pattern] of strictChecks){
       const found=metrics.visibleText.match(pattern)
       if(found)errors.push({device:device.id,locale,name,type,detail:found[0]})
     }
   }

  }
  for(const [name,route] of routes){
   try{
    const response=await page.goto(base+route,{waitUntil:"domcontentloaded",timeout:30000})
    await page.waitForTimeout(450)
    if(!response||response.status()>=400)errors.push({device:device.id,locale,name,type:"http",detail:response?.status()})
    await logFrame(name,route)
    if(name==="calendar-day"&&device.id==="iphone"){
     const menu=page.locator('[data-booking-workspace="calendar"] button[aria-label="Calendar menu"]')
     if(await menu.count()){
      await menu.click();await logFrame("calendar-menu",route)
      const adminEntry=page.locator('[data-booking-workspace="calendar"] aside a[href="/"]').first()
      if(await adminEntry.count()){
        await adminEntry.click()
        await page.waitForTimeout(550)
        await logFrame("switch-calendar-to-admin","/")
        if(!(await page.locator('[data-booking-workspace="admin"]').count()))
          errors.push({device:device.id,locale,name,type:"two-modes-not-separated",detail:"Calendar Administration link did not open admin shell"})
        await page.goto(base+"/agenda",{waitUntil:"domcontentloaded"})
        await page.waitForTimeout(550)
      }else{
        errors.push({device:device.id,locale,name,type:"missing-calendar-admin-switch",detail:"Calendar menu has no Administration link"})
        await page.locator('button[aria-label="Close menu"]').first().click().catch(()=>{})
      }
     }
     const scroll=page.locator('[data-booking-workspace="calendar"] main')
     await scroll.evaluate(el=>el.scrollTop=580);await logFrame("calendar-scrolled",route)
     if(locale==="uk"){
       const newButton=page.locator('[data-testid="calendar-new-booking"]').first()
       if(await newButton.count()){
         await newButton.click()
         await logFrame("appointment-create",route)
         await page.keyboard.press("Escape")
       }
       const appointmentId=await page.evaluate(()=>([...document.querySelectorAll('[data-booking-workspace="calendar"] button[id]')]
         .find(el=>/^[a-f0-9]{8}-[a-f0-9-]{27,}$/.test(el.id))?.id||""))
       if(appointmentId){
         await page.locator('[id="'+appointmentId+'"]').click()
         await logFrame("appointment-detail",route)
         await page.keyboard.press("Escape")
       }
     }
    }
    if(name==="settings-main"&&device.id==="iphone"&&locale==="uk"){
      const switcher=page.locator('select[aria-label="Interface language"]')
      if(await switcher.count()){
        const original=await page.locator('main').innerText()
        await switcher.selectOption("en");await page.waitForTimeout(180)
        const translated=await page.locator('main').innerText()
        if(original===translated)errors.push({device:device.id,locale,name,type:"language-switch-did-not-update",detail:"English and Ukrainian rendered text is unchanged"})
        await logFrame("switch-to-english",route)
        await switcher.selectOption("uk");await page.waitForTimeout(150)
        await logFrame("switch-back-to-ukrainian",route)
      }
    }
    if(name==="settings-team"){
      const details=page.locator('details').first()
      if(await details.count()){await details.evaluate(el=>el.open=true);await logFrame("employee-expanded",route)}
    }
   }catch(e){errors.push({device:device.id,locale,name,type:"navigation",detail:String(e).slice(0,280)})}
  }
  await context.close()
 }
}
await browser.close()
await writeFile(dir+"/report.json",JSON.stringify({base,captured:captures.length,captures,errors},null,2))
await writeFile(dir+"/report.md","# Booking mobile and desktop visual audit\n\n"+`Captured ${captures.length} real browser screenshots, found ${errors.length} issues.\n\n`+"## Screens\n\n"+captures.map(x=>`- ${x.device} / ${x.locale} / **${x.name}** — [image](${x.file}) — workspace: ${x.workspace}, page width: ${x.pageWidth}px, main text: ${x.mainTextLength} chars`).join("\n")+"\n\n## Issues\n\n"+errors.map(x=>`- **${x.type}** ${x.device} ${x.locale} ${x.name}: ${x.detail}`).join("\n"))
console.log("BOOKING_VISUAL_AUDIT_RESULT",JSON.stringify({captured:captures.length,issues:errors.length,byType:errors.reduce((p,e)=>(p[e.type]=(p[e.type]||0)+1,p),{})}))
if(errors.length)process.exitCode=1
