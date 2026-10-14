from pathlib import Path
path=Path("/app/src/i18n/bridge.tsx")
path.write_text(r'''"use client"
import { useEffect } from "react"
import { normalizeLocale, translateText, type Locale } from "./messages"

const ATTRS=["aria-label","title","placeholder"] as const
type Canonical={english:string;last:string}
const texts=new WeakMap<Text,Canonical>()
const attrs=new WeakMap<Element,Map<string,Canonical>>()

function selectedLocale():Locale{
  try{
    const stored=localStorage.getItem("booking_locale")
    if(stored)return normalizeLocale(stored)
    const cookie=document.cookie.match(/(?:^|;\\s*)booking_locale=([^;]+)/)?.[1]
    if(cookie)return normalizeLocale(decodeURIComponent(cookie))
    return normalizeLocale(navigator.language)
  }catch{return "en"}
}
function translateNode(node:Text,locale:Locale){
  const parent=node.parentElement
  if(!parent||parent.closest("script,style,code,pre,[contenteditable=true]"))return
  const text=node.nodeValue||""
  if(!text.trim())return
  const existing=texts.get(node)
  const canonical=existing && existing.last===text
     ? existing.english : translateText(text,"en")
  const rendered=translateText(canonical,locale)
  texts.set(node,{english:canonical,last:rendered})
  if(text!==rendered)node.nodeValue=rendered
}
function translateAttributes(el:Element,locale:Locale){
  let saved=attrs.get(el)
  if(!saved){saved=new Map();attrs.set(el,saved)}
  for(const attr of ATTRS){
    const v=el.getAttribute(attr)
    if(!v)continue
    const old=saved.get(attr)
    const canonical=old && old.last===v ? old.english : translateText(v,"en")
    const rendered=translateText(canonical,locale)
    saved.set(attr,{english:canonical,last:rendered})
    if(v!==rendered)el.setAttribute(attr,rendered)
  }
}
function translateTree(root:Node,locale:Locale){
  if(root instanceof Text){translateNode(root,locale);return}
  if(!(root instanceof Element)&&root!==document.body)return
  if(root instanceof Element)translateAttributes(root,locale)
  const walker=document.createTreeWalker(root,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT)
  let node:Node|null
  while((node=walker.nextNode())){
    if(node instanceof Text)translateNode(node,locale)
    else if(node instanceof Element)translateAttributes(node,locale)
  }
}
export function LocaleBridge(){
  useEffect(()=>{
    let locale=selectedLocale()
    let observer:MutationObserver|undefined
    let active=true
    const start=()=>{
      if(!active)return
      locale=selectedLocale()
      document.documentElement.lang=locale
      translateTree(document.body,locale)
      observer=new MutationObserver(mutations=>{
        const visited=new Set<Node>()
        for(const m of mutations){
          if(m.type==="characterData"){
            if(!visited.has(m.target)){visited.add(m.target);translateTree(m.target,locale)}
          }else if(m.type==="attributes"){
            if(!visited.has(m.target)){visited.add(m.target);translateTree(m.target,locale)}
          }else{
            for(const n of m.addedNodes){
              if(visited.has(n))continue
              visited.add(n)
              translateTree(n,locale)
            }
          }
        }
      })
      observer.observe(document.body,{subtree:true,characterData:true,childList:true,attributes:true,attributeFilter:[...ATTRS]})
    }
    // Hydrate the React streaming tree first. Changing server-rendered text while
    // its client components are hydrating produces React #418 mismatches.
    const timer=window.setTimeout(start,500)
    const onLocale=()=>{
      locale=selectedLocale()
      document.documentElement.lang=locale
      if(observer)translateTree(document.body,locale)
    }
    window.addEventListener("booking:locale",onLocale)
    return ()=>{active=false;clearTimeout(timer);observer?.disconnect();window.removeEventListener("booking:locale",onLocale)}
  },[])
  return null
}
''',encoding="utf-8")
print("BOOKING_I18N_BRIDGE_STABLE_SWITCHER_INSTALLED")
