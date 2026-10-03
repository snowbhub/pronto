FROM odoo:18.0

USER root

RUN mkdir -p /mnt/extra-addons \
    && python3 - <<'PY'
import io
import shutil
import urllib.request
import zipfile

url = "https://github.com/MohamedAbdelsalamMady/Businesstica-Company/archive/refs/heads/production.zip"
data = urllib.request.urlopen(url, timeout=120).read()

with zipfile.ZipFile(io.BytesIO(data)) as z:
    z.extractall("/tmp/businesstica")

src = "/tmp/businesstica/Businesstica-Company-production/salon_management_18.0"
dst = "/mnt/extra-addons/salon_management"
shutil.copytree(src, dst)
shutil.rmtree("/tmp/businesstica")
PY

USER odoo
