FROM node:22-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates nginx \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/clawnify/OpenSalon.git .

RUN npm install --legacy-peer-deps \
    && npm run build

RUN rm -f /etc/nginx/sites-enabled/default \
    && printf '%s\n' \
      'server {' \
      '  listen 3000;' \
      '  server_name _;' \
      '  root /app/dist;' \
      '  index index.html;' \
      '  location /api/ {' \
      '    proxy_pass http://127.0.0.1:8787;' \
      '    proxy_http_version 1.1;' \
      '    proxy_set_header Host $host;' \
      '  }' \
      '  location / {' \
      '    try_files $uri $uri/ /index.html;' \
      '  }' \
      '}' > /etc/nginx/conf.d/opensalon.conf

ENV PORT=3000
EXPOSE 3000

CMD ["sh", "-lc", "set -e; mkdir -p /data/wrangler; npx wrangler d1 execute open-salon-db --local --file=src/server/schema.sql --persist-to /data/wrangler >/tmp/schema.log 2>&1; npx wrangler dev --local --ip 127.0.0.1 --port 8787 --persist-to /data/wrangler >/tmp/wrangler.log 2>&1 & API_PID=$!; trap 'kill $API_PID' TERM INT EXIT; nginx -g 'daemon off;'"]
