from pathlib import Path
import re
p=Path("/app/src/components/agenda/new-appointment.tsx")
s=p.read_text(encoding="utf-8")
replacements=[
 ("className=\"num ml-auto h-8 w-40 rounded-md","className=\"num ml-auto h-10 min-w-0 w-full sm:w-40 rounded-md"),
 ("className=\"grid grid-cols-2 gap-2 sm:grid-cols-3\"","className=\"grid min-w-0 grid-cols-2 gap-2 sm:grid-cols-3\""),
 ("className=\"grid grid-cols-4 gap-1.5 sm:grid-cols-6\"","className=\"grid min-w-0 grid-cols-3 gap-2 sm:grid-cols-6\""),
 ("<div className=\"space-y-6 px-6 py-5\">","<div className=\"min-w-0 space-y-6 px-4 py-5 sm:px-6\">"),
]
for old,new in replacements:
 if old in s:s=s.replace(old,new)
s,count=re.subn(r'(<DialogContent\s+className=")([^"]*)(")',
 lambda m:m.group(1)+("booking-create-dialog " if "booking-create-dialog" not in m.group(2) else "")+m.group(2)+m.group(3),
 s,count=1)
if count!=1:raise RuntimeError("Appointment dialog markup missing")
p.write_text(s,encoding="utf-8")
p=Path("/app/src/app/globals.css")
s=p.read_text(encoding="utf-8")
s+="""
@media(max-width:767px){
 html body [data-slot="dialog-content"][data-slot="dialog-content"][data-slot="dialog-content"]{
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
