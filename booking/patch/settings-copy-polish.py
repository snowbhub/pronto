from pathlib import Path
import re

def replace_paragraph(path, class_name, content):
    p = Path("/app") / path
    s = p.read_text(encoding="utf-8")
    class_pattern = re.escape(class_name)
    pattern = re.compile(r'(<p className="' + class_pattern + r'">).*?(</p>)', re.S)
    s, count = pattern.subn(lambda m: m.group(1) + content + m.group(2), s, count=1)
    if count != 1:
        raise RuntimeError(f"{path}: expected one {class_name} paragraph, found {count}")
    p.write_text(s, encoding="utf-8")

replace_paragraph(
    "src/components/settings/fixed-slots-editor.tsx",
    "text-[13px] text-ivory-3",
    "Clients who always come on the same day and time can reserve a fixed slot. That slot is no longer offered to others through WhatsApp, Instagram or online booking. When the client arrives, create their appointment with Quick booking."
)
replace_paragraph(
    "src/components/settings/slot-step-form.tsx",
    "text-[12.5px] text-ivory-3",
    "This is what clients see when booking and what the AI Agent offers. Existing bookings do not change. Service duration is set on the Services tab."
)
replace_paragraph(
    "src/app/(panel)/ajustes/page.tsx",
    "text-[14px] text-ivory-2",
    "{`Each haircut earns one loyalty stamp. After ${BRAND.loyalty.stampsRequired} stamps, the next haircut is ${BRAND.loyalty.rewardDiscountPct}% off under the loyalty card rule. The discount is applied at checkout.`}"
)
print("BOOKING_SETTINGS_COPY_POLISHED")
