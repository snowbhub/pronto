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

EXPOSE 8069

# Avoid the official image's HOST/PORT DB env convention because Railway
# reserves PORT for the HTTP service port.
ENTRYPOINT []
CMD ["bash", "-lc", "exec odoo --db_host=\"$DB_HOST\" --db_port=\"${DB_PORT:-5432}\" --db_user=\"$DB_USER\" --db_password=\"$DB_PASSWORD\" --http-port=8069"]
