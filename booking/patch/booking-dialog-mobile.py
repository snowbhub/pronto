from pathlib import Path
p=Path("/app/src/components/agenda/new-appointment.tsx")
s=p.read_text(encoding="utf-8")
before=s
checks=[
 ('className="max-h-[92dvh] gap-0 overflow-y-auto p-0 sm:max-w-[640px] scroll-thin"','className="booking-create-dialog max-h-[92dvh] min-w-0 max-w-[calc(100vw-12px)] overflow-x-hidden overflow-y-auto overscroll-contain p-0 sm:max-w-[640px] scroll-thin"'),
 ('className="num ml-auto h-8 w-40 rounded-md','className="num ml-auto h-10 min-w-0 w-full sm:w-40 rounded-md'),
 ('className="grid grid-cols-2 gap-2 sm:grid-cols-3"','className="grid min-w-0 grid-cols-2 gap-2 sm:grid-cols-3"'),
 ('className="grid grid-cols-4 gap-1.5 sm:grid-cols-6"','className="grid min-w-0 grid-cols-3 gap-2 sm:grid-cols-6"'),
 ('<div className="space-y-6 px-6 py-5">','<div className="min-w-0 space-y-6 px-4 py-5 sm:px-6">'),
]
for old,new in checks:
 if old not in s:raise RuntimeError("Modal markup changed: "+old)
 s=s.replace(old,new)
p.write_text(s,encoding="utf-8")
p=Path("/app/src/app/globals.css")
s=p.read_text(encoding="utf-8")
s+="""
@media(max-width:767px){
 [data-slot="dialog-content"].booking-create-dialog{
  width:calc(100vw - 12px)!important;
  max-width:calc(100vw - 12px)!important;
  max-height:calc(100dvh - env(safe-area-inset-top) - 12px)!important;
  left:6px!important;right:6px!important;bottom:6px!important;
  overflow-x:hidden!important;
  padding-bottom:env(safe-area-inset-bottom);
 }
 .booking-create-dialog > *, .booking-create-dialog form,
 .booking-create-dialog [role="group"]{min-width:0;max-width:100%}
 .booking-create-dialog button,.booking-create-dialog input{max-width:100%}
}
"""
p.write_text(s,encoding="utf-8")
print("BOOKING_NEW_APPOINTMENT_FITS_MOBILE_SCREEN",len(checks))
