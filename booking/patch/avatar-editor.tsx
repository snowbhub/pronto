"use client"
import { useRef,useState,useTransition } from "react"
import { useRouter } from "next/navigation"
import { uploadStaffAvatar } from "@/lib/staff/avatar-actions"

export function StaffPhotoEditor({staffId}:{staffId:string}){
 const input=useRef<HTMLInputElement|null>(null)
 const router=useRouter()
 const [pending,start]=useTransition()
 const [error,setError]=useState("")
 const [success,setSuccess]=useState("")
 const [selectedName,setSelectedName]=useState("")
 async function handle(file:File){
  setError("");setSuccess("")
  try{
   const image=await createImageBitmap(file)
   const factor=Math.min(1,300/Math.max(image.width,image.height))
   const canvas=document.createElement("canvas")
   canvas.width=Math.max(1,Math.round(image.width*factor))
   canvas.height=Math.max(1,Math.round(image.height*factor))
   const ctx=canvas.getContext("2d")
   if(!ctx)throw Error("Photo processing unavailable")
   ctx.drawImage(image,0,0,canvas.width,canvas.height)
   image.close()
   const blob=await new Promise<Blob>((resolve,reject)=>
     canvas.toBlob(b=>b?resolve(b):reject(Error("Could not compress photo")),"image/jpeg",0.74)
   )
   if(blob.size>350000)throw Error("Compressed photo is too large")
   const form=new FormData()
   form.append("staffId",staffId)
   form.append("photo",new File([blob],"profile.jpg",{type:"image/jpeg"}))
   start(async()=>{
    const result=await uploadStaffAvatar(form)
    if(result.ok){setSuccess("Photo saved");router.refresh()}
    else setError(result.error||"Photo not saved")
   })
  }catch(e){setError(e instanceof Error?e.message:"Could not process the image")}
 }
 return <div className="space-y-2">
   <div className="text-xs font-semibold text-ivory-2">Profile photo</div>
   <div className="flex min-w-0 items-center gap-2">
     <button type="button" disabled={pending} onClick={()=>input.current?.click()}
       className="min-h-10 shrink-0 rounded-lg border border-line-strong bg-surface-3 px-3 text-xs font-semibold text-ivory transition-opacity disabled:cursor-not-allowed disabled:opacity-50">
       Choose photo
     </button>
     <span className="min-w-0 flex-1 truncate text-xs font-normal text-ivory-3" aria-live="polite">{selectedName||"No photo selected"}</span>
   </div>
   <input ref={input} type="file" accept="image/*" aria-label="Select profile photo" disabled={pending}
     onChange={e=>{
       const file=e.currentTarget.files?.[0]
       if(file){setSelectedName(file.name);void handle(file)}
       e.currentTarget.value=""
     }}
     className="sr-only"/>
   {error&&<p role="alert" className="text-xs text-danger">{error}</p>}
   {success&&<p role="status" className="text-xs text-ok">{success}</p>}
   {pending&&<p className="text-xs text-ivory-3">Uploading photo…</p>}
 </div>
}
