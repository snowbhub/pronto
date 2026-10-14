import { chromium } from "playwright"
import { mkdir,writeFile } from "node:fs/promises"

const base=process.env.BOOKING_BASE_URL || "https://booking-production-8515.up.railway.app"
const adminPassword=process.env.BOOKING_TEST_PANEL_PASSWORD || ""
const dir="booking/screenshots"
await mkdir(dir,{recursive:true})
const browser=await chromium.launch({headless:true,args:["--no-sandbox"]})
const problems=[]
const shots=[]
const routes=[
  ["today","/"],["calendar","/agenda"],["cash","/caja"],["finance","/finanzas"],
  ["employees","/ajustes?tab=equipo"],["services","/ajustes?tab=servicios"],
  ["ranks","/ranks"],["inventory","/inventory"],["payroll","/payroll"],
  ["cash-management","/cash-management"],["analytics","/analytics"],
  ["ai","/agente"],["inbox","/bandeja"],["customers","/clientes"],
  ["settings","/ajustes"],["staff-accounts","/staff-accounts"]
]
for(const locale of ["uk","de","en"]){
 const context=await browser.newContext({
   viewport:{width:390,height:844},deviceScaleFactor:1,
   locale:locale==="uk"?"uk-UA":locale==="de"?"de-DE":"en-GB",
   isMobile:true,hasTouch:true
 })
 await context.addCookies([{name:"booking_locale",value:locale,url:base}])
 await context.addInitScript(language=>{
   localStorage.setItem("booking_locale",language)
   localStorage.setItem("booking_theme","light")
 },locale)
 const page=await context.newPage()
 page.on("pageerror",e=>problems.push({locale,path:page.url(),type:"js",message:e.message}))
 const screens=[["customer-booking","/reservar"],["staff-login","/staff-login"],["admin-login","/login"]]
 if(adminPassword){
  try{
   await page.goto(base+"/login",{waitUntil:"domcontentloaded",timeout:30000})
   await page.locator('input[type="password"]').first().fill(adminPassword)
   await page.locator('button[type="submit"]').first().click()
   await page.waitForTimeout(1000)
   if(new URL(page.url()).pathname==="/login")problems.push({locale,type:"auth",message:"Admin login was rejected; protected screenshots skipped."})
   else screens.push(...routes)
  }catch(e){problems.push({locale,type:"auth",message:String(e)})}
 }
 for(const [name,path] of screens){
  try{
   const response=await page.goto(base+path,{waitUntil:"domcontentloaded",timeout:35000})
   await page.waitForTimeout(850)
   const status=response?.status()||0
   const now=new URL(page.url()).pathname
   const report=await page.evaluate(()=>{
    const text=document.body?.innerText||""
    const width=document.documentElement.scrollWidth
    const viewport=window.innerWidth
    const spanish=(text.match(/\b(Empezar|Nuevo turno|Entrando|No vino|Cobrar|Agendar|Cambiar|Sin confirmar|Nadie por ahora)\b/g)||[]).slice(0,20)
    return {width,viewport,overflow:width>viewport+2,spanish}
   })
   const filename=`${dir}/${locale}-${name}.png`
   await page.screenshot({path:filename,fullPage:true,animations:"disabled"})
   shots.push({locale,name,url:page.url(),status,file:filename,...report})
   if(report.overflow)problems.push({locale,name,type:"horizontal-overflow",message:`${report.width}px content within ${report.viewport}px viewport`})
   if(status>=400)problems.push({locale,name,type:"http",message:String(status)})
   if(now==="/login"&&path!=="/login")problems.push({locale,name,type:"auth",message:"Protected route redirected to login"})
  }catch(e){problems.push({locale,name,type:"navigation",message:String(e)})}
 }
 await context.close()
}
await browser.close()
await writeFile(dir+"/report.json",JSON.stringify({base,shots,problems},null,2))
console.log("BOOKING_SCREENSHOTS",shots.length,"PROBLEMS",problems.length)
console.log(problems.slice(0,50))
