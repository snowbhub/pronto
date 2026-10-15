from pathlib import Path
p=Path('/app/src/i18n/bridge.tsx')
s=p.read_text(encoding='utf-8')
guard='''  // The client directory is localized by React itself; never mutate streaming/hydrating text.
  if(location.pathname==="/clientes")return'''
if guard not in s:raise RuntimeError('Native Clients hydration guard missing')
replacement='''  // Only the OUTSIDE shell is safe to localize on the Clients route.
  // Client cards and their Suspense boundary are rendered by React with the
  // locale passed from the server; mutating those nodes caused React #418.
  if(location.pathname==="/clientes"){
    if(root!==document.body)return
    const shellNodes=[...document.body.querySelectorAll<HTMLElement>("aside,nav,.booking-app-header")]
      .filter(el=>!el.closest("main"))
    for(const element of new Set(shellNodes)){
      translateAttributes(element,locale)
      const walker=document.createTreeWalker(element,NodeFilter.SHOW_TEXT|NodeFilter.SHOW_ELEMENT)
      let node:Node|null
      while((node=walker.nextNode())){
        if(node instanceof Text)translateNode(node,locale)
        else if(node instanceof Element)translateAttributes(node,locale)
      }
    }
    return
  }'''
s=s.replace(guard,replacement,1)
p.write_text(s,encoding='utf-8')
p=Path('/app/src/components/clients/clients-view.tsx')
s=p.read_text(encoding='utf-8')
s=s.replace('{timeAgo(r.lastVisit, n)}','{tr(timeAgo(r.lastVisit, n))}')
s=s.replace('const tr=(value:string)=>translateText(value,locale)',
            'const tr=(value:string)=>value==="Last"?(locale==="uk"?"Останній візит":locale==="de"?"Letzter Besuch":"Last"):value==="now"?(locale==="uk"?"щойно":locale==="de"?"gerade eben":"now"):translateText(value,locale)',1)
print('BOOKING_CLIENTS_SHELL_SAFE_LOCALE_ENABLED')
