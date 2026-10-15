from pathlib import Path
import re
p=Path("/app/src/components/agenda/new-appointment.tsx")
s=p.read_text(encoding="utf-8")
replacements=[
 ("className=\"num ml-auto h-8 w-40 rounded-md","className=\"num ml-auto h-10 min-w-0 w-full sm:w-40 rounded-md"),
 ("className=\"grid grid-cols-2 gap-2 sm:grid-cols-3\"","className=\"grid min-w-0 grid-cols-2 gap-2 sm:grid-cols-3\""),
 ("className=\"grid grid-cols-4 gap-1.5 sm:grid-cols-6\"","className=\"grid min-w-0 grid-cols-3 gap-2 sm:grid-cols-6\""),
 ("className=\"min-w-[68px] px-2 py-2 text-center\"","className=\"h-auto w-[68px] min-w-[68px] shrink-0 px-2 py-2 text-center\""),
 ("<div className=\"space-y-6 px-6 py-5\">","<div className=\"min-w-0 space-y-6 px-4 py-5 sm:px-6\">"),
]
for old,new in replacements:
 if old in s:s=s.replace(old,new)
s,count_id=re.subn(r'(<DialogContent\s+)className="', r'\1id="booking-create-dialog" className="', s, count=1)
if count_id!=1:raise RuntimeError("Appointment dialog id target missing")
s,count=re.subn(r'(<DialogContent\b[^>]*\bclassName=")([^"]*)(")',
 lambda m:m.group(1)+("booking-create-dialog max-[767px]:translate-x-0! max-[767px]:translate-y-0! " if "booking-create-dialog" not in m.group(2) else "")+m.group(2)+m.group(3),
 s,count=1)
if count!=1:raise RuntimeError("Appointment dialog markup missing")
p.write_text(s,encoding="utf-8")
p=Path("/app/src/app/globals.css")
s=p.read_text(encoding="utf-8")
s+="""
@media(max-width:767px){
 #booking-create-dialog{
  width:calc(100vw - 12px)!important;
  max-width:calc(100vw - 12px)!important;
  max-height:calc(100dvh - env(safe-area-inset-top) - 12px)!important;
  left:6px!important;right:6px!important;top:6px!important;bottom:auto!important;
  transform:none!important;translate:none!important;
  overflow-x:hidden!important;overflow-y:auto!important;
  padding-bottom:env(safe-area-inset-bottom);
 }
 .booking-create-dialog > *, .booking-create-dialog form,
 .booking-create-dialog [role="group"]{min-width:0;max-width:100%}
 .booking-create-dialog button,.booking-create-dialog input{max-width:100%}
}
"""
p.write_text(s,encoding="utf-8")
print("BOOKING_NEW_APPOINTMENT_FITS_MOBILE_SCREEN",count)
