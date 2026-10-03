FROM node:22-bookworm

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 https://github.com/clawnify/OpenSalon.git .

RUN npm install --legacy-peer-deps

ENV PORT=3000

EXPOSE 3000

CMD ["sh", "-lc", "mkdir -p /data/wrangler && npx wrangler d1 execute open-salon-db --local --file=src/server/schema.sql --persist-to /data/wrangler && npx concurrently -k -n ui,api \"npx vite --host 0.0.0.0 --port ${PORT:-3000}\" \"npx wrangler dev --local --ip 127.0.0.1 --port 8787 --persist-to /data/wrangler\""]
