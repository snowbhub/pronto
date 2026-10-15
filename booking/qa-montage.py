from PIL import Image, ImageOps, ImageDraw, ImageFont
from pathlib import Path
from io import BytesIO
import base64, json
root=Path("booking/screenshots")
out=Path("booking/qa-results")
out.mkdir(parents=True, exist_ok=True)
selected=["dashboard","calendar-day","calendar-week","calendar-menu","calendar-scrolled","settings-main","settings-team","employee-expanded","settings-services","settings-fixed","settings-business","settings-connections","cash-management","inventory","payroll","clients","inbox","agent","login"]
for device in ("iphone","desktop"):
  images=[]
  for page in selected:
    p=root/f"{device}-uk-{page}.png"
    if not p.exists():continue
    im=Image.open(p).convert("RGB")
    im.thumbnail((300,550) if device=="iphone" else (500,315))
    card=Image.new("RGB",(314,im.height+36),"#edf0f3") if device=="iphone" else Image.new("RGB",(514,im.height+36),"#edf0f3")
    card.paste(im,((card.width-im.width)//2,34))
    d=ImageDraw.Draw(card)
    d.text((10,10),page,fill="#242424")
    images.append(card)
  if not images:continue
  cols=4 if device=="iphone" else 3
  w=max(im.width for im in images)
  h=max(im.height for im in images)
  height=h*((len(images)+cols-1)//cols)
  montage=Image.new("RGB",(w*cols,height),"#d8dfe5")
  for idx,im in enumerate(images):montage.paste(im,((idx%cols)*w,(idx//cols)*h))
  buff=BytesIO()
  montage.save(buff,format="JPEG",quality=68,optimize=True)
  (out/f"{device}-montage.b64").write_text(base64.b64encode(buff.getvalue()).decode("ascii"),encoding="ascii")
  montage.save(out/f"{device}-montage.jpg",quality=68,optimize=True)
report=root/"report.json"
if report.exists():
  (out/"report.json").write_bytes(report.read_bytes())
  print("BOOKING_QA_MONTAGE",json.dumps({"report":json.loads(report.read_text()).get("captured"),"images":len(images),"device":device}))
