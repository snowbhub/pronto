import { createHmac, randomBytes, scryptSync, timingSafeEqual } from "node:crypto"

export const STAFF_COOKIE="booking_staff_session"
const SESSION_SECONDS=12*60*60
const secret=()=>process.env.PANEL_PASSWORD?.trim()||null
const uuid=/^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$/i
export function hashStaffPassword(plain:string){
 if(plain.length<12||plain.length>128)throw new Error("Password must contain 12–128 characters")
 const salt=randomBytes(20).toString("hex")
 return "scrypt$"+salt+"$"+scryptSync(plain,salt,64).toString("hex")
}
export function verifyStaffPassword(plain:string,stored:string){
 const parts=stored.split("$")
 if(parts.length!==3||parts[0]!=="scrypt"||! /^[0-9a-f]{40}$/.test(parts[1])||! /^[0-9a-f]{128}$/.test(parts[2]))return false
 const candidate=scryptSync(plain,parts[1],64)
 return timingSafeEqual(candidate,Buffer.from(parts[2],"hex"))
}
export function staffCookieFor(staffId:string){
 const key=secret()
 if(!key||!uuid.test(staffId))throw new Error("Staff session not configured")
 const data=Buffer.from(JSON.stringify({id:staffId,exp:Math.floor(Date.now()/1000)+SESSION_SECONDS})).toString("base64url")
 const signature=createHmac("sha256",key).update(data).digest("base64url")
 return data+"."+signature
}
export function staffIdFromCookie(token:string|undefined):string|null{
 const key=secret()
 if(!key||!token||token.length>900)return null
 const pieces=token.split(".")
 if(pieces.length!==2)return null
 const expected=createHmac("sha256",key).update(pieces[0]).digest()
 let actual:Buffer
 try{actual=Buffer.from(pieces[1],"base64url")}catch{return null}
 if(expected.length!==actual.length||!timingSafeEqual(expected,actual))return null
 try{
  const parsed=JSON.parse(Buffer.from(pieces[0],"base64url").toString("utf8"))
  if(typeof parsed.id!=="string"||!uuid.test(parsed.id)||typeof parsed.exp!=="number"||parsed.exp<Date.now()/1000)return null
  return parsed.id
 }catch{return null}
}
