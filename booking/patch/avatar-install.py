from pathlib import Path
root=Path("/app")
patch=Path("/tmp/booking-patch")
p=root/"src/lib/staff/avatar-actions.ts"
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text((patch/"avatar-actions.ts").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/app/api/staff-avatar/[id]/route.ts"
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text((patch/"avatar-route.ts").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/components/settings/staff-photo-editor.tsx"
p.parent.mkdir(parents=True,exist_ok=True)
p.write_text((patch/"avatar-editor.tsx").read_text(encoding="utf-8"),encoding="utf-8")
p=root/"src/components/settings/team-editor.tsx"
s=p.read_text(encoding="utf-8")
s=s.replace('import Link from "next/link"','import Link from "next/link"\nimport Image from "next/image"\nimport { StaffPhotoEditor } from "./staff-photo-editor"')
s=s.replace('accounts=[] }: {','accounts=[],photos=[] }: {')
s=s.replace('accounts?: {staffId:string;username:string;active:boolean}[]','accounts?: {staffId:string;username:string;active:boolean}[];photos?:string[]')
s=s.replace('''<span className="grid size-9 place-items-center rounded-full bg-surface-3 text-[13px] font-semibold text-ivory">{m.name[0]}</span>''',
'''<span className="grid size-11 shrink-0 place-items-center overflow-hidden rounded-full bg-surface-3 text-sm font-semibold text-ivory">{photos.includes(m.id)?<Image unoptimized width={44} height={44} src={`/api/staff-avatar/${m.id}`} alt={m.name} className="h-full w-full object-cover" />:m.name[0]}</span>''')
s=s.replace('<p className="text-xs text-ivory-3">Change employee name, commission and profile details using the pencil above.</p>',
'''<p className="text-xs text-ivory-3">Change the name and commission with the pencil above; other employee details are below.</p>
                <StaffPhotoEditor staffId={m.id} />''')
p.write_text(s,encoding="utf-8")
p=root/"src/app/(panel)/ajustes/page.tsx"
s=p.read_text(encoding="utf-8")
needle='accounts={(await sqlClient()`select staff_id,username,active from booking_staff_accounts`).map(a=>({staffId:String(a.staff_id),username:String(a.username),active:Boolean(a.active)}))} />'
replacement='accounts={(await sqlClient()`select staff_id,username,active from booking_staff_accounts`).map(a=>({staffId:String(a.staff_id),username:String(a.username),active:Boolean(a.active)}))} photos={(await sqlClient()`select staff_id from booking_staff_avatars`).map(p=>String(p.staff_id))} />'
if needle not in s:raise RuntimeError("Staff account view integration missing")
s=s.replace(needle,replacement)
p.write_text(s,encoding="utf-8")
print("BOOKING_STAFF_PHOTO_UPLOAD_WIRED")
